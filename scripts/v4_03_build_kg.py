#!/usr/bin/env python3
"""
SexDiffKG v4 — Step 3: Build Knowledge Graph with Reactome + NaN-free edges
=============================================================================
Uses DiAna-normalized signals, Reactome pathways (CC-BY 4.0), and ensures
zero NaN contamination in output triples.

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-03
"""

import json, logging, time, gzip
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/v4_03_build_kg.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / "sexdiffkg"
KG_DIR = BASE / "data" / "kg_v4"
KG_DIR.mkdir(parents=True, exist_ok=True)

# Data sources
SIGNALS_V4 = BASE / "results/signals_v4/sex_differential_v4.parquet"
ROR_V4 = BASE / "results/signals_v4/ror_by_sex_v4.parquet"
DRUG_V4 = BASE / "data/processed/faers_clean/drug_normalized_v4.parquet"

# Molecular data
STRING_PPI = BASE / "data/raw/string/9606.protein.links.v12.0.txt.gz"
STRING_ALIASES = BASE / "data/raw/string/9606.protein.aliases.v12.0.txt.gz"
REACTOME_GENE = BASE / "data/raw/reactome/Ensembl2Reactome.txt"
REACTOME_PATHS = BASE / "data/raw/reactome/ReactomePathways.txt"
CHEMBL_TARGETS = BASE / "data/processed/molecular/drug_targets.parquet"
GTEx_SEX_DE = BASE / "data/processed/molecular/sex_de_genes.parquet"

# Old data sources (for backward compatibility if needed)
KEGG_PATHWAYS = BASE / "data/processed/molecular/gene_pathways.parquet"
PPI_NETWORK = BASE / "data/processed/molecular/ppi_network.parquet"

STRING_SCORE_THRESHOLD = 700


class KGBuilder:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.stats = {}
    
    def add_node(self, node_id, name, category):
        if node_id and str(node_id) != "nan":
            self.nodes[str(node_id)] = {
                "id": str(node_id),
                "name": str(name),
                "category": str(category),
            }
    
    def add_edge(self, subject, predicate, obj, **props):
        s, p, o = str(subject), str(predicate), str(obj)
        if s and o and s != "nan" and o != "nan" and p != "nan":
            edge = {"subject": s, "predicate": p, "object": o}
            edge.update(props)
            self.edges.append(edge)
    
    def save(self, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Nodes TSV
        nodes_df = pd.DataFrame(list(self.nodes.values()))
        nodes_df.to_csv(output_dir / "nodes.tsv", sep="\t", index=False)
        logger.info(f"Saved {len(nodes_df):,} nodes")
        
        # Edges TSV
        edges_df = pd.DataFrame(self.edges)
        edges_df.to_csv(output_dir / "edges.tsv", sep="\t", index=False)
        logger.info(f"Saved {len(edges_df):,} edges")
        
        # Triples TSV (subject, predicate, object — no header, for PyKEEN)
        triples_df = edges_df[["subject", "predicate", "object"]].copy()
        # CRITICAL: Remove any rows with NaN
        before = len(triples_df)
        triples_df = triples_df.dropna()
        triples_df = triples_df[
            (triples_df["subject"] != "nan") & 
            (triples_df["object"] != "nan") &
            (triples_df["predicate"] != "nan") &
            (triples_df["subject"] != "") & 
            (triples_df["object"] != "") &
            (triples_df["predicate"] != "")
        ]
        dropped = before - len(triples_df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped:,} NaN/empty triples")
        
        triples_df.to_csv(output_dir / "triples.tsv", sep="\t", index=False, header=False)
        logger.info(f"Saved {len(triples_df):,} triples (NaN-free)")
        
        return len(nodes_df), len(edges_df), len(triples_df)


def load_reactome_pathways():
    """Load Reactome gene-pathway mappings (human only)."""
    if not REACTOME_GENE.exists():
        logger.warning("Reactome Ensembl2Reactome.txt not found")
        return pd.DataFrame()
    
    logger.info("Loading Reactome pathways...")
    # Ensembl2Reactome.txt has columns: gene_id, pathway_id, url, pathway_name, evidence, species
    df = pd.read_csv(REACTOME_GENE, sep="\t", header=None,
                     names=["gene_id", "pathway_id", "url", "pathway_name", "evidence", "species"])
    # Filter human only
    df = df[df["species"] == "Homo sapiens"].copy()
    logger.info(f"Reactome human gene-pathway mappings: {len(df):,}")
    logger.info(f"  Unique genes: {df['gene_id'].nunique():,}")
    logger.info(f"  Unique pathways: {df['pathway_id'].nunique():,}")
    
    # Load pathway names
    if REACTOME_PATHS.exists():
        paths = pd.read_csv(REACTOME_PATHS, sep="\t", header=None,
                           names=["pathway_id", "pathway_name", "species"])
        paths = paths[paths["species"] == "Homo sapiens"]
        logger.info(f"Reactome human pathways: {len(paths):,}")
    
    return df


def load_string_ppi():
    """Load STRING PPI network (human, score >= 700)."""
    if not STRING_PPI.exists():
        logger.warning(f"STRING PPI not found at {STRING_PPI}")
        # Fall back to pre-processed
        if PPI_NETWORK.exists():
            logger.info("Using pre-processed PPI network")
            return pd.read_parquet(PPI_NETWORK)
        return pd.DataFrame()
    
    logger.info("Loading STRING PPI (fresh from raw)...")
    df = pd.read_csv(STRING_PPI, sep=" ", compression="gzip")
    df = df[df["combined_score"] >= STRING_SCORE_THRESHOLD].copy()
    # Remove 9606. prefix
    df["protein1"] = df["protein1"].str.replace("9606.", "", regex=False)
    df["protein2"] = df["protein2"].str.replace("9606.", "", regex=False)
    logger.info(f"STRING PPI edges (score >= {STRING_SCORE_THRESHOLD}): {len(df):,}")
    return df


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("SexDiffKG v4 — Knowledge Graph Construction")
    logger.info("=" * 70)
    
    kg = KGBuilder()
    
    # ─── Layer 1: Drug-AE edges from FAERS (sex-stratified ROR) ───
    logger.info("\n--- Layer 1: Drug-AE edges (has_adverse_event) ---")
    if ROR_V4.exists():
        ror = pd.read_parquet(ROR_V4)
        logger.info(f"Loaded {len(ror):,} ROR entries")
        
        for _, row in ror.iterrows():
            drug = f"DRUG:{row['drug_name']}"
            ae = f"AE:{row['adverse_event']}"
            kg.add_node(drug, row["drug_name"], "Drug")
            kg.add_node(ae, row["adverse_event"], "AdverseEvent")
            kg.add_edge(drug, "has_adverse_event", ae)
        
        kg.stats["has_adverse_event"] = len(ror)
        logger.info(f"  Added {len(ror):,} has_adverse_event edges")
    else:
        logger.error("ROR v4 file not found!")
        return
    
    # ─── Layer 2: Sex-differential signals ───
    logger.info("\n--- Layer 2: Sex-differential signals ---")
    if SIGNALS_V4.exists():
        sig = pd.read_parquet(SIGNALS_V4)
        logger.info(f"Loaded {len(sig):,} sex-differential signals")
        
        for _, row in sig.iterrows():
            drug = f"DRUG:{row['drug_name']}"
            ae = f"AE:{row['adverse_event']}"
            kg.add_edge(drug, "sex_differential_adverse_event", ae)
        
        kg.stats["sex_differential_adverse_event"] = len(sig)
        logger.info(f"  Added {len(sig):,} sex_differential_adverse_event edges")
    
    # ─── Layer 3: Drug-Target interactions (ChEMBL) ───
    logger.info("\n--- Layer 3: Drug-target interactions (ChEMBL) ---")
    if CHEMBL_TARGETS.exists():
        targets = pd.read_parquet(CHEMBL_TARGETS)
        logger.info(f"Loaded {len(targets):,} drug-target interactions")
        
        target_count = 0
        for _, row in targets.iterrows():
            drug_name = str(row.get("drug_name", row.get("drugname_normalized", ""))).upper()
            gene = str(row.get("gene_name", row.get("target_name", "")))
            if drug_name and gene and drug_name != "nan" and gene != "nan":
                drug = f"DRUG:{drug_name}"
                gene_id = f"GENE:{gene}"
                kg.add_node(gene_id, gene, "Gene")
                kg.add_edge(drug, "targets", gene_id)
                target_count += 1
        
        kg.stats["targets"] = target_count
        logger.info(f"  Added {target_count:,} targets edges")
    else:
        logger.warning("ChEMBL targets not found")
    
    # ─── Layer 4: Protein-Protein Interactions (STRING) ───
    logger.info("\n--- Layer 4: PPI network (STRING v12) ---")
    ppi = load_string_ppi()
    if len(ppi) > 0:
        ppi_count = 0
        for _, row in ppi.iterrows():
            p1 = str(row.get("protein1", row.get("protein_a", "")))
            p2 = str(row.get("protein2", row.get("protein_b", "")))
            if p1 and p2 and p1 != "nan" and p2 != "nan":
                p1_id = f"PROTEIN:{p1}"
                p2_id = f"PROTEIN:{p2}"
                kg.add_node(p1_id, p1, "Protein")
                kg.add_node(p2_id, p2, "Protein")
                kg.add_edge(p1_id, "interacts_with", p2_id)
                ppi_count += 1
        
        kg.stats["interacts_with"] = ppi_count
        logger.info(f"  Added {ppi_count:,} interacts_with edges")
    
    # ─── Layer 5: Gene-Pathway (Reactome — CC-BY 4.0) ───
    logger.info("\n--- Layer 5: Gene-pathway (Reactome) ---")
    reactome = load_reactome_pathways()
    if len(reactome) > 0:
        pathway_count = 0
        for _, row in reactome.iterrows():
            gene_id = f"GENE:{row['gene_id']}"
            pathway_id = f"PATHWAY:{row['pathway_id']}"
            kg.add_node(gene_id, row["gene_id"], "Gene")
            kg.add_node(pathway_id, row.get("pathway_name", row["pathway_id"]), "Pathway")
            kg.add_edge(gene_id, "participates_in", pathway_id)
            pathway_count += 1
        
        kg.stats["participates_in"] = pathway_count
        logger.info(f"  Added {pathway_count:,} participates_in edges (Reactome)")
    else:
        # Fall back to KEGG if Reactome not available
        if KEGG_PATHWAYS.exists():
            logger.info("Falling back to KEGG pathways...")
            kegg = pd.read_parquet(KEGG_PATHWAYS)
            pathway_count = 0
            for _, row in kegg.iterrows():
                gene = str(row.get("gene_name", row.get("gene", "")))
                pathway = str(row.get("pathway_name", row.get("pathway", "")))
                if gene and pathway and gene != "nan" and pathway != "nan":
                    gene_id = f"GENE:{gene}"
                    pw_id = f"PATHWAY:{pathway}"
                    kg.add_node(gene_id, gene, "Gene")
                    kg.add_node(pw_id, pathway, "Pathway")
                    kg.add_edge(gene_id, "participates_in", pw_id)
                    pathway_count += 1
            kg.stats["participates_in"] = pathway_count
            logger.info(f"  Added {pathway_count:,} participates_in edges (KEGG fallback)")
    
    # ─── Layer 6: Sex-differential gene expression (GTEx) ───
    logger.info("\n--- Layer 6: Sex-differential expression (GTEx) ---")
    if GTEx_SEX_DE.exists() and GTEx_SEX_DE.stat().st_size > 200:
        sex_de = pd.read_parquet(GTEx_SEX_DE)
        de_count = 0
        for _, row in sex_de.iterrows():
            gene = str(row.get("gene", row.get("gene_name", "")))
            tissue = str(row.get("tissue", ""))
            if gene and tissue and gene != "nan" and tissue != "nan":
                gene_id = f"GENE:{gene}"
                tissue_id = f"TISSUE:{tissue}"
                kg.add_node(gene_id, gene, "Gene")
                kg.add_node(tissue_id, tissue, "Tissue")
                kg.add_edge(tissue_id, "sex_differential_expression", gene_id)
                de_count += 1
        
        kg.stats["sex_differential_expression"] = de_count
        logger.info(f"  Added {de_count:,} sex_differential_expression edges")
    else:
        logger.warning("GTEx sex-DE data not found or empty")
    
    # ─── Save KG ───
    logger.info("\n--- Saving KG v4 ---")
    n_nodes, n_edges, n_triples = kg.save(KG_DIR)
    
    # Node type breakdown
    node_types = {}
    for n in kg.nodes.values():
        cat = n["category"]
        node_types[cat] = node_types.get(cat, 0) + 1
    
    elapsed = time.time() - start
    
    summary = {
        "version": "v4",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_nodes": n_nodes,
        "total_edges": n_edges,
        "total_triples": n_triples,
        "nan_triples_dropped": n_edges - n_triples,
        "node_types": node_types,
        "edge_types": kg.stats,
        "data_sources": {
            "signals": "v4_diana_normalized",
            "ppi": "STRING_v12_score_700",
            "pathways": "Reactome_CC-BY-4.0" if len(reactome) > 0 else "KEGG_fallback",
            "targets": "ChEMBL_36",
            "sex_de": "GTEx_v8",
        },
        "elapsed_seconds": round(elapsed, 1),
    }
    
    with open(KG_DIR / "kg_v4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"\nKG v4 Summary:")
    logger.info(f"  Nodes: {n_nodes:,}")
    logger.info(f"  Edges: {n_edges:,}")
    logger.info(f"  Triples (NaN-free): {n_triples:,}")
    for cat, cnt in sorted(node_types.items(), key=lambda x: -x[1]):
        logger.info(f"  {cat}: {cnt:,}")
    for rel, cnt in sorted(kg.stats.items(), key=lambda x: -x[1]):
        logger.info(f"  {rel}: {cnt:,}")
    
    logger.info(f"\nDone in {elapsed:.0f}s")
    logger.info("V4_KG_BUILD_COMPLETE")


if __name__ == "__main__":
    main()
