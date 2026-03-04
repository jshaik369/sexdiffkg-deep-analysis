#!/usr/bin/env python3
"""
Download all FDA FAERS quarterly ASCII data files from 2004Q1 through 2025Q3.

This script downloads AERS/FAERS data from the FDA FIS website, manages downloads
with resume capability via checkpoint tracking, and creates symlinks for data access.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
def setup_logging(log_dir: Path) -> None:
    """Configure logging to both file and console."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"faers_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info(f"Logging initialized. Log file: {log_file}")


def create_session_with_retries(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Tuple[int, ...] = (500, 502, 504)
) -> requests.Session:
    """
    Create a requests Session with retry logic.
    
    Args:
        retries: Number of retries
        backoff_factor: Backoff factor for exponential backoff
        status_forcelist: HTTP status codes to retry on
    
    Returns:
        Configured requests.Session with retry adapter
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "HEAD"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_file_size(session: requests.Session, url: str) -> Optional[int]:
    """
    Get the size of a remote file via HEAD request.
    
    Args:
        session: Requests session with retry logic
        url: URL to check
    
    Returns:
        File size in bytes, or None if HEAD request fails
    """
    try:
        response = session.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return int(response.headers.get('content-length', 0))
    except requests.RequestException:
        pass
    return None


def file_needs_download(
    file_path: Path,
    remote_size: Optional[int]
) -> bool:
    """
    Determine if a file needs to be downloaded.
    
    Args:
        file_path: Path to local file
        remote_size: Size of remote file (bytes)
    
    Returns:
        True if file should be downloaded, False otherwise
    """
    if not file_path.exists():
        return True
    
    local_size = file_path.stat().st_size
    if local_size == 0:
        return True
    
    if remote_size is not None and local_size != remote_size:
        return True
    
    return False


def download_file(
    session: requests.Session,
    url: str,
    output_path: Path,
    chunk_size: int = 8192
) -> bool:
    """
    Download a file from URL to output path.
    
    Args:
        session: Requests session with retry logic
        url: URL to download from
        output_path: Path to save file to
        chunk_size: Chunk size for streaming download
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        logging.info(f"Downloaded {output_path.name}: {total_size:,} bytes")
        return True
    
    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")
        return False


def create_symlink(target: Path, link: Path) -> bool:
    """
    Create a symlink from link to target.
    
    Args:
        target: Path to target file
        link: Path to symlink to create
    
    Returns:
        True if successful, False otherwise
    """
    try:
        link.parent.mkdir(parents=True, exist_ok=True)
        
        if link.exists() or link.is_symlink():
            link.unlink()
        
        link.symlink_to(target)
        return True
    
    except (OSError, RuntimeError) as e:
        logging.error(f"Failed to create symlink {link}: {e}")
        return False


def generate_quarters() -> List[Tuple[int, int]]:
    """
    Generate list of (year, quarter) tuples from 2004Q1 to 2025Q3.
    
    Returns:
        List of (year, quarter) tuples
    """
    quarters = []
    for year in range(2004, 2026):
        max_quarter = 4 if year < 2025 else 3
        for quarter in range(1, max_quarter + 1):
            quarters.append((year, quarter))
    return quarters


def determine_url_pattern(year: int, quarter: int) -> str:
    """
    Determine the correct URL pattern for a given year/quarter.
    
    AERS (2004Q1-2012Q3): aers_ascii_{YYYY}q{Q}
    FAERS (2012Q4-2025Q3): faers_ascii_{YYYY}q{Q}
    
    Args:
        year: Year
        quarter: Quarter (1-4)
    
    Returns:
        Base URL pattern name ("aers" or "faers")
    """
    if year < 2012:
        return "aers"
    elif year == 2012 and quarter < 4:
        return "aers"
    else:
        return "faers"


def load_checkpoint(checkpoint_file: Path) -> Dict[str, bool]:
    """
    Load checkpoint file tracking completed quarters.
    
    Args:
        checkpoint_file: Path to checkpoint JSON file
    
    Returns:
        Dictionary mapping quarter strings to completion status
    """
    if checkpoint_file.exists():
        try:
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Could not load checkpoint file: {e}. Starting fresh.")
    return {}


def save_checkpoint(checkpoint_file: Path, checkpoint: Dict[str, bool]) -> None:
    """
    Save checkpoint file tracking completed quarters.
    
    Args:
        checkpoint_file: Path to checkpoint JSON file
        checkpoint: Dictionary mapping quarter strings to completion status
    """
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    logging.info(f"Checkpoint saved: {checkpoint_file}")


def main() -> None:
    """Main download orchestration function."""
    parser = argparse.ArgumentParser(
        description="Download FDA FAERS quarterly ASCII data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --output-dir /custom/output --link-dir /custom/links
  %(prog)s --output-dir /data/raw_faers --link-dir /data/links
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('/media/jshaik369/cen8tb/sexdiffkg_data/raw_faers'),
        help='Directory to save downloaded ZIP files'
    )
    parser.add_argument(
        '--link-dir',
        type=Path,
        default=Path('/home/jshaik369/sexdiffkg/data/raw/faers'),
        help='Directory to create symlinks to downloaded files'
    )
    
    args = parser.parse_args()
    
    output_dir = args.output_dir
    link_dir = args.link_dir
    log_dir = output_dir / 'logs'
    checkpoint_file = output_dir / 'checkpoint.json'
    
    # Setup logging
    setup_logging(log_dir)
    logging.info("="*80)
    logging.info("FDA FAERS Download Script Started")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Link directory: {link_dir}")
    logging.info("="*80)
    
    # Create output and link directories
    output_dir.mkdir(parents=True, exist_ok=True)
    link_dir.mkdir(parents=True, exist_ok=True)
    
    # Load checkpoint
    checkpoint = load_checkpoint(checkpoint_file)
    
    # Create session with retries
    session = create_session_with_retries()
    
    quarters = generate_quarters()
    total_downloaded = 0
    total_size = 0
    failures = []
    
    logging.info(f"Total quarters to process: {len(quarters)}")
    
    for year, quarter in quarters:
        quarter_str = f"{year}Q{quarter}"
        
        # Check if already completed
        if checkpoint.get(quarter_str, False):
            logging.info(f"[{quarter_str}] Skipping (already complete)")
            continue
        
        pattern = determine_url_pattern(year, quarter)
        
        # Try both lowercase and uppercase Q
        for case in ['lowercase', 'uppercase']:
            q_str = f'q{quarter}' if case == 'lowercase' else f'Q{quarter}'
            filename = f'{pattern}_ascii_{year}{q_str}.zip'
            url = f'https://fis.fda.gov/content/Exports/{filename}'
            output_path = output_dir / filename
            link_path = link_dir / filename
            
            logging.info(f"[{quarter_str}] Attempting {filename} ({case})...")
            
            # Check remote file size
            remote_size = get_file_size(session, url)
            
            if remote_size is None:
                if case == 'lowercase':
                    continue  # Try uppercase
                else:
                    logging.error(f"[{quarter_str}] File not found (tried both cases)")
                    failures.append(quarter_str)
                    break
            
            # Skip if file already downloaded and matches size
            if not file_needs_download(output_path, remote_size):
                logging.info(f"[{quarter_str}] File already exists with correct size, skipping")
                checkpoint[quarter_str] = True
                save_checkpoint(checkpoint_file, checkpoint)
                break
            
            # Download file
            if download_file(session, url, output_path):
                # Create symlink
                if create_symlink(output_path, link_path):
                    total_downloaded += 1
                    total_size += remote_size if remote_size else output_path.stat().st_size
                    checkpoint[quarter_str] = True
                    save_checkpoint(checkpoint_file, checkpoint)
                    logging.info(f"[{quarter_str}] SUCCESS")
                    break
                else:
                    logging.error(f"[{quarter_str}] Failed to create symlink")
                    failures.append(quarter_str)
                    break
            else:
                if case == 'lowercase':
                    continue  # Try uppercase
                else:
                    logging.error(f"[{quarter_str}] Download failed (tried both cases)")
                    failures.append(quarter_str)
                    break
    
    # Print summary
    logging.info("="*80)
    logging.info("Download Summary")
    logging.info("="*80)
    logging.info(f"Total files downloaded: {total_downloaded}")
    logging.info(f"Total size downloaded: {total_size:,} bytes ({total_size / (1024**3):.2f} GB)")
    
    if failures:
        logging.warning(f"Failed quarters ({len(failures)}): {', '.join(failures)}")
    else:
        logging.info("All quarters completed successfully!")
    
    logging.info("="*80)
    print("\nDownload Summary:")
    print(f"  Files downloaded: {total_downloaded}")
    print(f"  Total size: {total_size / (1024**3):.2f} GB")
    if failures:
        print(f"  Failed quarters: {len(failures)}")
    else:
        print("  Status: All quarters completed!")


if __name__ == '__main__':
    main()
