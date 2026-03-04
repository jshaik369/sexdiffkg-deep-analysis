#!/usr/bin/env python3
"""
Download molecular data sources for the sexdiffkg project.

Downloads:
- STRING human PPI and aliases (v12.0)
- UniProt ID mapping for Homo sapiens
- Reactome pathway data

Includes retry logic, progress tracking, and checkpoint management.
"""

import os
import gzip
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MolecularDataDownloader:
    """Download and manage molecular data sources."""
    
    def __init__(self, base_dir: str = "~/sexdiffkg"):
        """Initialize downloader with base directory."""
        self.base_dir = Path(base_dir).expanduser()
        self.raw_dir = self.base_dir / "data" / "raw"
        self.checkpoint_file = self.base_dir / "data" / ".download_checkpoint.json"
        
        # Create directories
        self.string_dir = self.raw_dir / "string"
        self.uniprot_dir = self.raw_dir / "uniprot"
        self.reactome_dir = self.raw_dir / "reactome"
        
        for d in [self.string_dir, self.uniprot_dir, self.reactome_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.checkpoints = self._load_checkpoint()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _load_checkpoint(self) -> Dict:
        """Load checkpoint file if it exists."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")
        return {}
    
    def _save_checkpoint(self):
        """Save checkpoint to file."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoints, f, indent=2, default=str)
        logger.info(f"Checkpoint saved to {self.checkpoint_file}")
    
    def _download_file(
        self,
        url: str,
        output_path: Path,
        checkpoint_key: str,
        chunk_size: int = 8192
    ) -> bool:
        """Download file with progress bar and skip if exists."""
        # Check if already downloaded
        if output_path.exists():
            if checkpoint_key in self.checkpoints:
                logger.info(f"Skipping {output_path.name} (already downloaded)")
                return True
        
        logger.info(f"Downloading {url}")
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get total size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            # Mark as completed in checkpoint
            self.checkpoints[checkpoint_key] = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'size': output_path.stat().st_size
            }
            self._save_checkpoint()
            logger.info(f"Successfully downloaded {output_path.name}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            if output_path.exists():
                output_path.unlink()
            return False
    
    def download_string_ppi(self) -> bool:
        """Download STRING human PPI data."""
        logger.info("Starting STRING PPI download...")
        url = "https://stringdb-downloads.org/download/protein.links.v12.0/9606.protein.links.v12.0.txt.gz"
        output_path = self.string_dir / "9606.protein.links.v12.0.txt.gz"
        checkpoint_key = "string_ppi_v12.0"
        
        return self._download_file(url, output_path, checkpoint_key)
    
    def download_string_aliases(self) -> bool:
        """Download STRING protein aliases."""
        logger.info("Starting STRING aliases download...")
        url = "https://stringdb-downloads.org/download/protein.aliases.v12.0/9606.protein.aliases.v12.0.txt.gz"
        output_path = self.string_dir / "9606.protein.aliases.v12.0.txt.gz"
        checkpoint_key = "string_aliases_v12.0"
        
        return self._download_file(url, output_path, checkpoint_key)
    
    def download_uniprot_mapping(self) -> bool:
        """Download UniProt ID mapping for human."""
        logger.info("Starting UniProt ID mapping download...")
        url = "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz"
        output_path = self.uniprot_dir / "HUMAN_9606_idmapping.dat.gz"
        checkpoint_key = "uniprot_idmapping_human"
        
        return self._download_file(url, output_path, checkpoint_key)
    
    def download_reactome(self) -> bool:
        """Download Reactome Ensembl to Reactome mapping."""
        logger.info("Starting Reactome download...")
        url = "https://download.reactome.org/current/Ensembl2Reactome.txt"
        output_path = self.reactome_dir / "Ensembl2Reactome.txt"
        checkpoint_key = "reactome_ensembl_mapping"
        
        return self._download_file(url, output_path, checkpoint_key)
    
    def download_all(self) -> bool:
        """Download all data sources."""
        logger.info("=" * 70)
        logger.info("MOLECULAR DATA DOWNLOAD")
        logger.info("=" * 70)
        
        results = {
            'string_ppi': self.download_string_ppi(),
            'string_aliases': self.download_string_aliases(),
            'uniprot_mapping': self.download_uniprot_mapping(),
            'reactome': self.download_reactome(),
        }
        
        logger.info("=" * 70)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("=" * 70)
        for source, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{source}: {status}")
        
        all_success = all(results.values())
        if all_success:
            logger.info("All downloads completed successfully!")
        else:
            logger.warning("Some downloads failed. Please retry.")
        
        return all_success


def main():
    """Main entry point."""
    downloader = MolecularDataDownloader()
    success = downloader.download_all()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
