#!/usr/bin/env python3
"""
v4_04_unify_ids.py — SexDiffKG v4.2 ID Unification

Fixes the ID namespace fragmentation that creates 598 disconnected components.

Changes from v4.0:
1. Reactome: Filter to ENSG-only (drop mislabeled ENSP/ENST "Gene" nodes)
2. Reactome ENSP: Map to ENSG via UniProt id_mappings to recover gene-pathway edges
3. ChEMBL targets: Use ensembl_gene_id from drug_targets.parquet (not target_name)
4. GTEx: Map gene symbols to ENSG via id_mappings
5. Add encodes_for edges: GENE:ENSG -> PROTEIN:ENSP (connects PPI layer)
6. Deduplicate all edges
7. Rebuild nodes.tsv, edges.tsv, triples.tsv with new checksums

Author: J.Shaik (jshaik@coevolvenetwork.com)
"""

import pandas as pd
import numpy as np
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# === PATHS ===
PROJECT = Path("/home/jshaik369/sexdiffkg")
KG_V4 = PROJECT / "data" / "kg_v4"
KG_V42 = PROJECT / "data" / "kg_v42"
MOLECULAR = PROJECT / "data" / "processed" / "molecular"
RAW_REACTOME = PROJECT / "data" / "raw" / "reactome" / "Ensembl2Reactome.txt"

def load_id_mappings():
    """Load UniProt ID mappings (ENSG <-> ENSP <-> gene_symbol)."""
    im = pd.read_parquet(MOLECULAR / "id_mappings.parquet")
    logger.info(f"Loaded {len(im)} UniProt ID mappings")

    # Build ENSP -> ENSG mapping from string_id field
    # string_id format: "9606.ENSP00000378426"
    ensp_to_ensg = {}
    symbol_to_ensg = {}

    for _, row in im.iterrows():
        ensg = row.get("ensembl_gene_id")
        string_id = row.get("string_id")
        symbol = row.get("gene_symbol")

        if pd.notna(ensg):
            if pd.notna(string_id) and "ENSP" in str(string_id):
                ensp = str(string_id).replace("9606.", "")
                if ensp not in ensp_to_ensg:
                    ensp_to_ensg[ensp] = ensg
            if pd.notna(symbol) and isinstance(symbol, str):
                if symbol not in symbol_to_ensg:
                    symbol_to_ensg[symbol] = ensg

    logger.info(f"ENSP->ENSG mappings: {len(ensp_to_ensg)}")
    logger.info(f"Symbol->ENSG mappings: {len(symbol_to_ensg)}")
    return ensp_to_ensg, symbol_to_ensg


def build_reactome_edges(ensp_to_ensg):
    """Build clean participates_in edges from Reactome, ENSG-only."""
    logger.info("Building Reactome participates_in edges (ENSG-only)...")

    edges = set()
    pathway_names = {}

    with open(RAW_REACTOME) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 6 or parts[5] != "Homo sapiens":
                continue

            eid = parts[0].split(".")[0]
            pathway_id = parts[1]
            pathway_name = parts[3] if len(parts) > 3 else pathway_id

            if eid.startswith("ENSG"):
                edges.add((f"GENE:{eid}", "participates_in", f"PATHWAY:{pathway_id}"))
                pathway_names[f"PATHWAY:{pathway_id}"] = pathway_name
            elif eid.startswith("ENSP"):
                # Map ENSP to ENSG
                ensg = ensp_to_ensg.get(eid)
                if ensg:
                    edges.add((f"GENE:{ensg}", "participates_in", f"PATHWAY:{pathway_id}"))
                    pathway_names[f"PATHWAY:{pathway_id}"] = pathway_name

    logger.info(f"Reactome edges (ENSG-only + ENSP-mapped): {len(edges)}")
    reactome_genes = {e[0] for e in edges}
    logger.info(f"Unique Reactome genes: {len(reactome_genes)}")
    return edges, pathway_names


def build_drug_target_edges():
    """Build targets edges using ENSG from drug_targets.parquet."""
    logger.info("Building drug-target edges with ENSG gene IDs...")

    dt = pd.read_parquet(MOLECULAR / "drug_targets.parquet")
    edges = set()
    drug_nodes = {}
    gene_nodes = {}

    for _, row in dt.iterrows():
        drug_name = row["drug_name"]
        ensg = row.get("ensembl_gene_id")
        gene_symbol = row.get("gene_symbol")

        if pd.isna(drug_name):
            continue

        drug_id = f"DRUG:{drug_name}"
        drug_nodes[drug_id] = drug_name

        if pd.notna(ensg):
            gene_id = f"GENE:{ensg}"
            gene_name = gene_symbol if pd.notna(gene_symbol) else ensg
            gene_nodes[gene_id] = gene_name
            edges.add((drug_id, "targets", gene_id))
        elif pd.notna(gene_symbol):
            # Fallback to symbol if no ENSG
            gene_id = f"GENE:{gene_symbol}"
            gene_nodes[gene_id] = gene_symbol
            edges.add((drug_id, "targets", gene_id))

    logger.info(f"Drug-target edges: {len(edges)} (deduplicated from {len(dt)})")
    logger.info(f"Unique drugs: {len(drug_nodes)}, unique gene targets: {len(gene_nodes)}")
    return edges, drug_nodes, gene_nodes


def build_encodes_for_edges(ensp_to_ensg, protein_nodes):
    """Build GENE:ENSG -> encodes_for -> PROTEIN:ENSP edges."""
    logger.info("Building encodes_for edges (Gene -> Protein)...")

    edges = set()
    for ensp, ensg in ensp_to_ensg.items():
        protein_id = f"PROTEIN:{ensp}"
        if protein_id in protein_nodes:
            edges.add((f"GENE:{ensg}", "encodes_for", protein_id))

    logger.info(f"encodes_for edges: {len(edges)}")
    return edges


def build_gtex_edges(symbol_to_ensg):
    """Remap GTEx gene symbols to ENSG.

    Note: In v4, GTEx edges are stored as TISSUE -> sex_diff_expr -> GENE:SYMBOL
    (tissue is subject, gene is object).
    """
    logger.info("Remapping GTEx sex_differential_expression edges to ENSG...")

    v4_edges = pd.read_csv(KG_V4 / "edges.tsv", sep="\t")
    gtex_edges = v4_edges[v4_edges["predicate"] == "sex_differential_expression"]

    new_edges = set()
    mapped = 0
    unmapped = 0

    for _, row in gtex_edges.iterrows():
        tissue = row["subject"]   # TISSUE:Liver etc
        gene_id = row["object"]   # GENE:DDX3Y etc

        # Extract symbol from GENE:SYMBOL format
        symbol = gene_id.replace("GENE:", "")

        ensg = symbol_to_ensg.get(symbol)
        if ensg:
            new_edges.add((tissue, "sex_differential_expression", f"GENE:{ensg}"))
            mapped += 1
        else:
            # Keep original if no mapping found
            new_edges.add((tissue, "sex_differential_expression", gene_id))
            unmapped += 1

    logger.info(f"GTEx edges: {len(new_edges)} (mapped: {mapped}, unmapped: {unmapped})")
    return new_edges


def build_ppi_edges():
    """Load STRING PPI edges (unchanged, already use PROTEIN:ENSP)."""
    logger.info("Loading STRING PPI edges...")

    v4_edges = pd.read_csv(KG_V4 / "edges.tsv", sep="\t")
    ppi = v4_edges[v4_edges["predicate"] == "interacts_with"]

    edges = set()
    protein_nodes = set()
    for _, row in ppi.iterrows():
        edges.add((row["subject"], "interacts_with", row["object"]))
        protein_nodes.add(row["subject"])
        protein_nodes.add(row["object"])

    logger.info(f"PPI edges: {len(edges)}, unique proteins: {len(protein_nodes)}")
    return edges, protein_nodes


def build_faers_edges():
    """Load FAERS drug-AE edges (unchanged)."""
    logger.info("Loading FAERS drug-AE edges...")

    v4_edges = pd.read_csv(KG_V4 / "edges.tsv", sep="\t")

    hae_edges = set()
    sdae_edges = set()
    ae_nodes = set()
    drug_nodes_faers = set()

    for pred in ["has_adverse_event", "sex_differential_adverse_event"]:
        subset = v4_edges[v4_edges["predicate"] == pred]
        for _, row in subset.iterrows():
            edge = (row["subject"], pred, row["object"])
            if pred == "has_adverse_event":
                hae_edges.add(edge)
            else:
                sdae_edges.add(edge)
            drug_nodes_faers.add(row["subject"])
            ae_nodes.add(row["object"])

    logger.info(f"has_adverse_event: {len(hae_edges)}, sex_differential: {len(sdae_edges)}")
    logger.info(f"FAERS drugs: {len(drug_nodes_faers)}, AEs: {len(ae_nodes)}")
    return hae_edges, sdae_edges, drug_nodes_faers, ae_nodes


def assemble_kg(all_edges, drug_nodes_chembl, gene_nodes_chembl,
                pathway_names, protein_nodes, drug_nodes_faers, ae_nodes):
    """Assemble final nodes.tsv and edges.tsv."""
    logger.info("Assembling final KG...")

    # Build edges DataFrame
    edge_records = [(s, p, o) for s, p, o in all_edges]
    edges_df = pd.DataFrame(edge_records, columns=["subject", "predicate", "object"])
    edges_df = edges_df.drop_duplicates()
    edges_df = edges_df.sort_values(["predicate", "subject", "object"]).reset_index(drop=True)

    logger.info(f"Total edges: {len(edges_df)}")
    for pred, count in edges_df["predicate"].value_counts().items():
        logger.info(f"  {pred}: {count}")

    # Collect all entity IDs from edges
    all_entities = set(edges_df["subject"]) | set(edges_df["object"])

    # Build nodes
    node_records = []
    for eid in sorted(all_entities):
        if eid.startswith("DRUG:"):
            name = eid.replace("DRUG:", "")
            cat = "Drug"
        elif eid.startswith("AE:"):
            name = eid.replace("AE:", "")
            cat = "AdverseEvent"
        elif eid.startswith("GENE:"):
            raw = eid.replace("GENE:", "")
            cat = "Gene"
            if raw in gene_nodes_chembl:
                name = gene_nodes_chembl[eid] if eid in gene_nodes_chembl else raw
            else:
                name = raw
        elif eid.startswith("PROTEIN:"):
            name = eid.replace("PROTEIN:", "")
            cat = "Protein"
        elif eid.startswith("PATHWAY:"):
            name = pathway_names.get(eid, eid.replace("PATHWAY:", ""))
            cat = "Pathway"
        elif eid.startswith("TISSUE:"):
            name = eid.replace("TISSUE:", "")
            cat = "Tissue"
        else:
            name = eid
            cat = "Unknown"

        node_records.append({"id": eid, "name": name, "category": cat})

    nodes_df = pd.DataFrame(node_records)
    nodes_df = nodes_df.sort_values("id").reset_index(drop=True)

    logger.info(f"Total nodes: {len(nodes_df)}")
    for cat, count in nodes_df["category"].value_counts().items():
        logger.info(f"  {cat}: {count}")

    return nodes_df, edges_df


def compute_checksums(kg_dir):
    """Compute MD5 checksums for KG files."""
    checksums = {}
    for fname in ["nodes.tsv", "edges.tsv", "triples.tsv"]:
        fpath = kg_dir / fname
        if fpath.exists():
            md5 = hashlib.md5(fpath.read_bytes()).hexdigest()
            checksums[fname] = md5
            logger.info(f"MD5 {fname}: {md5}")
    return checksums


def count_connected_components(edges_df):
    """Count connected components using union-find."""
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for _, row in edges_df.iterrows():
        union(row["subject"], row["object"])

    components = {}
    all_nodes = set(edges_df["subject"]) | set(edges_df["object"])
    for node in all_nodes:
        root = find(node)
        if root not in components:
            components[root] = []
        components[root].append(node)

    sizes = sorted([len(v) for v in components.values()], reverse=True)
    logger.info(f"Connected components: {len(components)}")
    logger.info(f"Top 5 component sizes: {sizes[:5]}")
    return len(components), sizes


def main():
    logger.info("=" * 60)
    logger.info("SexDiffKG v4.2 — ID Unification Rebuild")
    logger.info("=" * 60)

    # Create output directory
    KG_V42.mkdir(parents=True, exist_ok=True)

    # Step 1: Load ID mappings
    ensp_to_ensg, symbol_to_ensg = load_id_mappings()

    # Step 2: Build all edge sets
    ppi_edges, protein_nodes = build_ppi_edges()
    hae_edges, sdae_edges, drug_nodes_faers, ae_nodes = build_faers_edges()
    reactome_edges, pathway_names = build_reactome_edges(ensp_to_ensg)
    target_edges, drug_nodes_chembl, gene_nodes_chembl = build_drug_target_edges()
    gtex_edges = build_gtex_edges(symbol_to_ensg)
    encodes_for_edges = build_encodes_for_edges(ensp_to_ensg, protein_nodes)

    # Step 3: Merge all edges
    all_edges = set()
    all_edges.update(ppi_edges)
    all_edges.update(hae_edges)
    all_edges.update(sdae_edges)
    all_edges.update(reactome_edges)
    all_edges.update(target_edges)
    all_edges.update(gtex_edges)
    all_edges.update(encodes_for_edges)

    logger.info(f"\nTotal merged edges (before dedup): {len(all_edges)}")

    # Step 4: Assemble
    nodes_df, edges_df = assemble_kg(
        all_edges, drug_nodes_chembl, gene_nodes_chembl,
        pathway_names, protein_nodes, drug_nodes_faers, ae_nodes
    )

    # Step 5: Save
    nodes_df.to_csv(KG_V42 / "nodes.tsv", sep="\t", index=False)
    edges_df.to_csv(KG_V42 / "edges.tsv", sep="\t", index=False)

    # Triples (headerless, for PyKEEN)
    triples_df = edges_df[["subject", "predicate", "object"]]
    triples_df.to_csv(KG_V42 / "triples.tsv", sep="\t", index=False, header=False)

    logger.info(f"\nSaved to {KG_V42}")

    # Step 6: Checksums
    checksums = compute_checksums(KG_V42)

    # Step 7: Connected components
    n_components, sizes = count_connected_components(edges_df)

    # Step 8: Comparison with v4.0
    v4_nodes = pd.read_csv(KG_V4 / "nodes.tsv", sep="\t")
    v4_edges = pd.read_csv(KG_V4 / "edges.tsv", sep="\t")

    logger.info("\n" + "=" * 60)
    logger.info("COMPARISON: v4.0 vs v4.2")
    logger.info("=" * 60)
    logger.info(f"Nodes: {len(v4_nodes)} -> {len(nodes_df)}")
    logger.info(f"Edges: {len(v4_edges)} -> {len(edges_df)}")
    logger.info(f"Connected components: 598 -> {n_components}")

    for cat in ["Gene", "Protein", "Drug", "AdverseEvent", "Pathway", "Tissue"]:
        old = len(v4_nodes[v4_nodes["category"] == cat])
        new = len(nodes_df[nodes_df["category"] == cat])
        logger.info(f"  {cat}: {old} -> {new}")

    # Save build summary
    summary = {
        "version": "v4.2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "changes": [
            "Reactome: filtered to ENSG-only + ENSP-mapped-to-ENSG (dropped ENST)",
            "ChEMBL targets: use ensembl_gene_id from drug_targets.parquet",
            "GTEx: gene symbols mapped to ENSG via UniProt id_mappings",
            "Added encodes_for edges: GENE:ENSG -> PROTEIN:ENSP",
            "Deduplicated all edge types"
        ],
        "nodes": len(nodes_df),
        "edges": len(edges_df),
        "connected_components": n_components,
        "top_component_sizes": sizes[:10],
        "checksums": checksums,
        "node_types": dict(nodes_df["category"].value_counts()),
        "edge_types": dict(edges_df["predicate"].value_counts()),
    }
    with open(KG_V42 / "build_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    logger.info(f"\nBuild summary saved to {KG_V42 / 'build_summary.json'}")
    logger.info("DONE")


if __name__ == "__main__":
    main()
