#!/usr/bin/env python3
"""
Molecular Data Integration Pipeline (05b_build_molecular.py)

Extracts and integrates data from:
- ChEMBL 36: Drug-target interactions
- UniProt: ID mappings (UniProt → Ensembl, Gene Name, STRING)
- STRING: Protein-protein interactions
- Reactome: Gene-pathway associations

Output Parquet files:
- drug_targets.parquet: chembl_id, drug_name, uniprot_accession, target_name, mechanism_of_action, action_type
- id_mappings.parquet: uniprot_id, ensembl_gene_id, gene_symbol, string_id
- ppi_network.parquet: protein1_uniprot, protein2_uniprot, combined_score
- gene_pathways.parquet: ensembl_gene_id, gene_symbol, pathway_id, pathway_name

Verified column names from actual data:
- ChEMBL: molregno, chembl_id, pref_name, tid, accession, mechanism_of_action, action_type
- UniProt: accession (uniprot_id), id_type (Gene_Name, Ensembl, STRING), id_value
- STRING: protein1, protein2, combined_score
- Reactome: ENSG ID, pathway_id, pathway_name, organism
"""

import sqlite3
import pandas as pd
import gzip
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import duckdb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
CHEMBL_DB = Path('/home/jshaik369/veda-kg/data/chembl/chembl_36/chembl_36_sqlite/chembl_36.db')
UNIPROT_FILE = Path('/home/jshaik369/sexdiffkg/data/raw/uniprot/HUMAN_9606_idmapping.dat.gz')
STRING_PPI_FILE = Path('/home/jshaik369/sexdiffkg/data/raw/string/9606.protein.links.v12.0.txt.gz')
STRING_ALIASES_FILE = Path('/home/jshaik369/sexdiffkg/data/raw/string/9606.protein.aliases.v12.0.txt.gz')
REACTOME_FILE = Path('/home/jshaik369/sexdiffkg/data/raw/reactome/Ensembl2Reactome.txt')
OUTPUT_DIR = Path('/home/jshaik369/sexdiffkg/data/processed/molecular')


def extract_chembl_drug_targets() -> pd.DataFrame:
    """
    Extract drug-target interactions from ChEMBL 36.
    
    Joins:
    - drug_mechanism: mechanism data with molregno (drug) and tid (target)
    - molecule_dictionary: drug names via molregno
    - target_dictionary: target names via tid
    - target_components: component linking via tid
    - component_sequences: UniProt accession via component_id
    
    Returns DataFrame with columns:
    chembl_id, drug_name, uniprot_accession, target_name, mechanism_of_action, action_type
    """
    logger.info('Extracting ChEMBL drug-target interactions...')
    
    conn = sqlite3.connect(CHEMBL_DB)
    
    query = """
    SELECT DISTINCT
        md.chembl_id,
        md.pref_name AS drug_name,
        cs.accession AS uniprot_accession,
        td.pref_name AS target_name,
        dm.mechanism_of_action,
        dm.action_type
    FROM drug_mechanism dm
    INNER JOIN molecule_dictionary md ON dm.molregno = md.molregno
    INNER JOIN target_dictionary td ON dm.tid = td.tid
    INNER JOIN target_components tc ON dm.tid = tc.tid
    INNER JOIN component_sequences cs ON tc.component_id = cs.component_id
    WHERE cs.accession IS NOT NULL
        AND md.chembl_id IS NOT NULL
        AND td.tax_id = 9606
        AND cs.organism = 'Homo sapiens'
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    logger.info(f'Extracted {len(df)} drug-target interactions from ChEMBL')
    logger.info(f'Columns: {list(df.columns)}')
    logger.info(f'Sample:\n{df.head(3)}')
    
    return df


def parse_uniprot_mapping() -> pd.DataFrame:
    """
    Parse UniProt ID mapping file (HUMAN_9606_idmapping.dat.gz).
    
    File format (tab-separated):
    UniProt_Accession | ID_Type | ID_Value
    
    ID_Type values to extract: Gene_Name, Ensembl, STRING
    
    Returns DataFrame with columns:
    uniprot_id, ensembl_gene_id, gene_symbol, string_id
    """
    logger.info('Parsing UniProt ID mapping...')
    
    # Initialize dictionaries to collect mapping data
    uniprot_to_gene = {}
    uniprot_to_ensembl = {}
    uniprot_to_string = {}
    
    with gzip.open(UNIPROT_FILE, 'rt') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
                
            uniprot_id = parts[0]
            id_type = parts[1]
            id_value = parts[2]
            
            # Extract relevant ID types
            if id_type == 'Gene_Name' and not uniprot_id.endswith('-'):
                # Only primary UniProt entries, not isoforms
                uniprot_to_gene[uniprot_id] = id_value
            elif id_type == 'Ensembl':
                # Extract just the Ensembl ID (remove version number)
                ensembl_id = id_value.split('.')[0] if '.' in id_value else id_value
                uniprot_to_ensembl[uniprot_id] = ensembl_id
            elif id_type == 'STRING':
                # STRING ID format: 9606.ENSP00000xxxxx
                uniprot_to_string[uniprot_id] = id_value
    
    # Create unified mapping for primary UniProts only
    all_uniprots = set(uniprot_to_gene.keys()) | set(uniprot_to_ensembl.keys()) | set(uniprot_to_string.keys())
    
    mapping_data = []
    for uniprot_id in all_uniprots:
        mapping_data.append({
            'uniprot_id': uniprot_id,
            'gene_symbol': uniprot_to_gene.get(uniprot_id),
            'ensembl_gene_id': uniprot_to_ensembl.get(uniprot_id),
            'string_id': uniprot_to_string.get(uniprot_id)
        })
    
    df = pd.DataFrame(mapping_data)
    
    # Keep only rows with at least one mapping
    df = df[(df['gene_symbol'].notna()) | (df['ensembl_gene_id'].notna()) | (df['string_id'].notna())]
    
    logger.info(f'Parsed {len(df)} UniProt ID mappings')
    logger.info(f'UniProts with Gene_Name: {df["gene_symbol"].notna().sum()}')
    logger.info(f'UniProts with Ensembl: {df["ensembl_gene_id"].notna().sum()}')
    logger.info(f'UniProts with STRING: {df["string_id"].notna().sum()}')
    logger.info(f'Sample:\n{df.head(3)}')
    
    return df


def parse_string_ppi() -> pd.DataFrame:
    """
    Parse STRING PPI file (9606.protein.links.v12.0.txt.gz).
    
    File format (tab-separated):
    protein1 | protein2 | combined_score
    
    Proteins are in format: 9606.ENSP00000xxxxx
    Filter for combined_score >= 700
    
    Returns DataFrame with columns:
    protein1_string_id, protein2_string_id, combined_score
    """
    logger.info('Parsing STRING PPI network...')
    
    df = pd.read_csv(
        STRING_PPI_FILE,
        sep='\s+',
        compression='gzip',
        dtype={'protein1': str, 'protein2': str, 'combined_score': int}
    )
    
    # Filter for high confidence interactions
    df_filtered = df[df['combined_score'] >= 700].copy()
    
    logger.info(f'Parsed {len(df)} total STRING PPIs')
    logger.info(f'Filtered to {len(df_filtered)} PPIs with score >= 700')
    logger.info(f'Sample:\n{df_filtered.head(3)}')
    
    return df_filtered


def map_string_to_uniprot(string_ppi_df: pd.DataFrame) -> pd.DataFrame:
    """
    Map STRING protein IDs to UniProt accessions using STRING aliases file.
    
    STRING aliases format (tab-separated):
    string_protein_id | alias | source
    
    Source "Ensembl_UniProt" or "UniProt_ID" contain UniProt IDs.
    
    Returns DataFrame with columns:
    protein1_uniprot, protein2_uniprot, combined_score
    """
    logger.info('Building STRING to UniProt mapping...')
    
    # Parse STRING aliases to find UniProt IDs
    string_to_uniprot = {}
    
    with gzip.open(STRING_ALIASES_FILE, 'rt') as f:
        for i, line in enumerate(f):
            if i == 0:  # Skip header
                continue
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
            
            string_id = parts[0]
            alias = parts[1]
            source = parts[2]
            
            # Extract UniProt accessions from specific sources
            if source in ['Ensembl_UniProt', 'UniProt_ID']:
                # Store primary entry (before any isoform marker)
                uniprot_clean = alias.split('-')[0]
                if uniprot_clean and not string_id in string_to_uniprot:
                    string_to_uniprot[string_id] = uniprot_clean
    
    logger.info(f'Mapped {len(string_to_uniprot)} STRING IDs to UniProt')
    
    # Map PPI network
    string_ppi_df['protein1_uniprot'] = string_ppi_df['protein1'].map(string_to_uniprot)
    string_ppi_df['protein2_uniprot'] = string_ppi_df['protein2'].map(string_to_uniprot)
    
    # Keep only pairs where both proteins mapped
    ppi_mapped = string_ppi_df[
        (string_ppi_df['protein1_uniprot'].notna()) & 
        (string_ppi_df['protein2_uniprot'].notna())
    ][['protein1_uniprot', 'protein2_uniprot', 'combined_score']].copy()
    
    # Remove duplicates (both directions)
    ppi_mapped = ppi_mapped.drop_duplicates()
    
    logger.info(f'Mapped PPI network: {len(ppi_mapped)} interactions with both proteins mapped')
    logger.info(f'Sample:\n{ppi_mapped.head(3)}')
    
    return ppi_mapped


def parse_reactome_pathways() -> pd.DataFrame:
    """
    Parse Reactome pathway file (Ensembl2Reactome.txt).
    
    File format (tab-separated):
    Ensembl_Gene_ID | Pathway_ID | Pathway_URL | Pathway_Name | Evidence | Organism
    
    Filter for Homo sapiens only.
    
    Returns DataFrame with columns:
    ensembl_gene_id, pathway_id, pathway_name
    """
    logger.info('Parsing Reactome pathways...')
    
    df = pd.read_csv(
        REACTOME_FILE,
        sep='\t',
        header=None,
        dtype={0: str, 1: str, 3: str, 5: str},
        names=['ensembl_gene_id', 'pathway_id', 'pathway_url', 'pathway_name', 'evidence', 'organism'],
        engine='python'
    )
    
    # Filter for human pathways only
    df_human = df[df['organism'] == 'Homo sapiens'].copy()
    
    # Extract just gene ID (remove version)
    df_human['ensembl_gene_id'] = df_human['ensembl_gene_id'].str.split('.').str[0]
    
    # Keep relevant columns
    df_human = df_human[['ensembl_gene_id', 'pathway_id', 'pathway_name']].drop_duplicates()
    
    logger.info(f'Parsed {len(df)} total Reactome associations')
    logger.info(f'Filtered to {len(df_human)} Homo sapiens associations')
    logger.info(f'Sample:\n{df_human.head(3)}')
    
    return df_human


def integrate_data(
    drug_targets: pd.DataFrame,
    id_mappings: pd.DataFrame,
    ppi_network: pd.DataFrame,
    gene_pathways: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Integrate all datasets using verified UniProt accessions.
    
    Uses DuckDB for efficient joins.
    """
    logger.info('Integrating molecular datasets...')
    
    # Register DataFrames with DuckDB
    conn = duckdb.connect(':memory:')
    conn.register('drug_targets', drug_targets)
    conn.register('id_mappings', id_mappings)
    conn.register('ppi_network', ppi_network)
    conn.register('gene_pathways', gene_pathways)
    
    # Verify drug targets have UniProt accessions
    drug_targets_integrated = conn.execute("""
        SELECT DISTINCT
            dt.chembl_id,
            dt.drug_name,
            dt.uniprot_accession,
            dt.target_name,
            dt.mechanism_of_action,
            dt.action_type,
            im.ensembl_gene_id,
            im.gene_symbol,
            im.string_id
        FROM drug_targets dt
        LEFT JOIN id_mappings im ON dt.uniprot_accession = im.uniprot_id
    """).df()
    
    logger.info(f'Drug-target interactions after ID mapping: {len(drug_targets_integrated)}')
    logger.info(f'Sample:\n{drug_targets_integrated.head(3)}')
    
    # Verify PPI network has UniProt accessions
    ppi_network_integrated = conn.execute("""
        SELECT DISTINCT
            pn.protein1_uniprot,
            pn.protein2_uniprot,
            pn.combined_score,
            im1.ensembl_gene_id AS protein1_ensembl,
            im1.gene_symbol AS protein1_symbol,
            im2.ensembl_gene_id AS protein2_ensembl,
            im2.gene_symbol AS protein2_symbol
        FROM ppi_network pn
        LEFT JOIN id_mappings im1 ON pn.protein1_uniprot = im1.uniprot_id
        LEFT JOIN id_mappings im2 ON pn.protein2_uniprot = im2.uniprot_id
    """).df()
    
    logger.info(f'PPI network after ID mapping: {len(ppi_network_integrated)}')
    
    # Add gene symbols to gene pathways from ID mappings
    gene_pathways_integrated = conn.execute("""
        SELECT DISTINCT
            gp.ensembl_gene_id,
            gp.pathway_id,
            gp.pathway_name,
            im.uniprot_id,
            im.gene_symbol,
            im.string_id
        FROM gene_pathways gp
        LEFT JOIN id_mappings im ON gp.ensembl_gene_id = im.ensembl_gene_id
    """).df()
    
    logger.info(f'Gene pathways after ID mapping: {len(gene_pathways_integrated)}')
    
    conn.close()
    
    return (
        drug_targets_integrated,
        ppi_network_integrated,
        gene_pathways_integrated,
        id_mappings
    )


def save_outputs(
    drug_targets: pd.DataFrame,
    ppi_network: pd.DataFrame,
    gene_pathways: pd.DataFrame,
    id_mappings: pd.DataFrame,
    output_dir: Path
) -> None:
    """Save integrated datasets to Parquet files."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save drug targets
    drug_targets_file = output_dir / 'drug_targets.parquet'
    drug_targets.to_parquet(drug_targets_file, index=False, engine='pyarrow')
    logger.info(f'Saved drug targets: {drug_targets_file} ({len(drug_targets)} rows)')
    
    # Save PPI network
    ppi_network_file = output_dir / 'ppi_network.parquet'
    ppi_network.to_parquet(ppi_network_file, index=False, engine='pyarrow')
    logger.info(f'Saved PPI network: {ppi_network_file} ({len(ppi_network)} rows)')
    
    # Save gene pathways
    gene_pathways_file = output_dir / 'gene_pathways.parquet'
    gene_pathways.to_parquet(gene_pathways_file, index=False, engine='pyarrow')
    logger.info(f'Saved gene pathways: {gene_pathways_file} ({len(gene_pathways)} rows)')
    
    # Save ID mappings
    id_mappings_file = output_dir / 'id_mappings.parquet'
    id_mappings.to_parquet(id_mappings_file, index=False, engine='pyarrow')
    logger.info(f'Saved ID mappings: {id_mappings_file} ({len(id_mappings)} rows)')
    
    logger.info(f'All outputs saved to {output_dir}')


def main():
    """Run the complete molecular data integration pipeline."""
    
    logger.info('='*80)
    logger.info('Starting Molecular Data Integration Pipeline')
    logger.info('='*80)
    
    try:
        # Extract from individual sources
        drug_targets = extract_chembl_drug_targets()
        id_mappings = parse_uniprot_mapping()
        string_ppi = parse_string_ppi()
        reactome_pathways = parse_reactome_pathways()
        
        # Map STRING protein IDs to UniProt
        ppi_network = map_string_to_uniprot(string_ppi)
        
        # Integrate all data
        (
            drug_targets_integrated,
            ppi_network_integrated,
            gene_pathways_integrated,
            id_mappings_final
        ) = integrate_data(
            drug_targets,
            id_mappings,
            ppi_network,
            reactome_pathways
        )
        
        # Save outputs
        save_outputs(
            drug_targets_integrated,
            ppi_network_integrated,
            gene_pathways_integrated,
            id_mappings_final,
            OUTPUT_DIR
        )
        
        logger.info('='*80)
        logger.info('Pipeline completed successfully!')
        logger.info('='*80)
        
        # Print summary statistics
        print('\n' + '='*80)
        print('SUMMARY STATISTICS')
        print('='*80)
        print(f'Drug-target interactions: {len(drug_targets_integrated)}')
        print(f'  - Unique drugs: {drug_targets_integrated["chembl_id"].nunique()}')
        print(f'  - Unique targets: {drug_targets_integrated["uniprot_accession"].nunique()}')
        print(f'\nID Mappings: {len(id_mappings_final)}')
        print(f'  - With gene symbols: {id_mappings_final["gene_symbol"].notna().sum()}')
        print(f'  - With Ensembl IDs: {id_mappings_final["ensembl_gene_id"].notna().sum()}')
        print(f'  - With STRING IDs: {id_mappings_final["string_id"].notna().sum()}')
        print(f'\nPPI Network: {len(ppi_network_integrated)} interactions')
        print(f'  - Unique proteins: {len(set(list(ppi_network_integrated["protein1_uniprot"].dropna()) + list(ppi_network_integrated["protein2_uniprot"].dropna())))}')
        print(f'\nGene Pathways: {len(gene_pathways_integrated)} associations')
        print(f'  - Unique genes: {gene_pathways_integrated["ensembl_gene_id"].nunique()}')
        print(f'  - Unique pathways: {gene_pathways_integrated["pathway_id"].nunique()}')
        print('='*80 + '\n')
        
    except Exception as e:
        logger.error(f'Pipeline failed with error: {e}', exc_info=True)
        raise


if __name__ == '__main__':
    main()
