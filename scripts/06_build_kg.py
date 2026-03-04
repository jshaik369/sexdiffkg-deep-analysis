#!/usr/bin/env python3
"""
Assemble the full SexDiffKG knowledge graph from processed data.

Builds a Biolink Model compliant knowledge graph with nodes and edges,
outputting in KGX format and triple format for embedding training.

Usage:
    python 06_build_kg.py --data-dir data/ --output-dir data/kg/
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SexDiffKGBuilder:
    """Builder for SexDiffKG knowledge graph."""

    def __init__(self, output_dir: Path):
        """
        Initialize the KG builder.

        Args:
            output_dir: Directory to save KG files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.nodes: Dict[str, Dict] = {}  # id -> {name, category, properties}
        self.edges: List[Dict] = []  # {subject, predicate, object, properties}
        self.triples: List[Tuple[str, str, str]] = []  # (subject, predicate, object)

    def add_node(
        self, node_id: str, node_name: str, node_category: str, **properties
    ) -> None:
        """
        Add a node to the graph.

        Args:
            node_id: Unique node identifier
            node_name: Human-readable node name
            node_category: Biolink node category
            **properties: Additional node properties
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "name": node_name,
                "category": node_category,
            }
            self.nodes[node_id].update(properties)
            logger.debug(f"Added node: {node_id} ({node_category})")

    def add_edge(
        self,
        subject_id: str,
        predicate: str,
        object_id: str,
        **properties,
    ) -> None:
        """
        Add an edge to the graph.

        Args:
            subject_id: Subject node ID
            predicate: Edge relationship type
            object_id: Object node ID
            **properties: Additional edge properties
        """
        # Ensure nodes exist
        if subject_id not in self.nodes or object_id not in self.nodes:
            logger.warning(
                f"Skipping edge: {subject_id} -> {predicate} -> {object_id} "
                "(missing node)"
            )
            return

        edge_id = f"{subject_id}--{predicate}--{object_id}"
        edge = {
            "subject": subject_id,
            "predicate": predicate,
            "object": object_id,
        }
        edge.update(properties)
        self.edges.append(edge)

        # Add to triples
        self.triples.append((subject_id, predicate, object_id))

        logger.debug(f"Added edge: {subject_id} -> {predicate} -> {object_id}")

    def load_drug_targets(self, file_path: Path) -> None:
        """
        Load drug-target interactions.

        Args:
            file_path: Path to drug_targets.parquet
        """
        logger.info(f"Loading drug targets from {file_path}")
        df = pd.read_parquet(file_path)

        for _, row in df.iterrows():
            drug_id = row["chembl_id"]
            drug_name = row.get("drug_name", drug_id)
            protein_id = row["ensembl_gene_id"]
            protein_name = row.get("gene_symbol", protein_id)
            moa = row.get("action_type", "targets")
            action_type = row.get("mechanism_of_action", "unknown")

            # Add nodes
            self.add_node(drug_id, drug_name, "Drug", chembl_id=drug_id)
            self.add_node(
                protein_id,
                protein_name,
                "Protein",
                ensembl_id=protein_id,
                gene_symbol=protein_name,
            )

            # Add edge
            self.add_edge(
                drug_id,
                "targets",
                protein_id,
                mechanism_of_action=moa,
                action_type=action_type,
            )

        logger.info(f"Loaded {len(df)} drug-target interactions")

    def load_ppi_network(self, file_path: Path) -> None:
        """
        Load protein-protein interactions.

        Args:
            file_path: Path to ppi_network.parquet
        """
        logger.info(f"Loading PPI network from {file_path}")
        df = pd.read_parquet(file_path)

        for _, row in df.iterrows():
            protein1_id = row["protein1_ensembl"]
            protein1_name = row.get("protein1_symbol", protein1_id)
            protein2_id = row["protein2_ensembl"]
            protein2_name = row.get("protein2_symbol", protein2_id)
            score = row.get("combined_score", 0.0)

            # Add nodes
            self.add_node(
                protein1_id,
                protein1_name,
                "Protein",
                ensembl_id=protein1_id,
                gene_symbol=protein1_name,
            )
            self.add_node(
                protein2_id,
                protein2_name,
                "Protein",
                ensembl_id=protein2_id,
                gene_symbol=protein2_name,
            )

            # Add edge (bidirectional as single edge)
            self.add_edge(
                protein1_id,
                "interacts_with",
                protein2_id,
                combined_score=score,
            )

        logger.info(f"Loaded {len(df)} PPI interactions")

    def load_pathways(self, file_path: Path) -> None:
        """
        Load gene-pathway associations.

        Args:
            file_path: Path to gene_pathways.parquet
        """
        logger.info(f"Loading pathways from {file_path}")
        df = pd.read_parquet(file_path)

        pathway_nodes: Set[str] = set()

        for _, row in df.iterrows():
            gene_id = row["ensembl_gene_id"]
            gene_symbol = row.get("gene_symbol", gene_id)
            pathway_id = row.get("pathway_id", "")
            pathway_name = row.get("pathway_name", pathway_id)
            source = row.get("source", "Reactome")

            # Add gene node
            self.add_node(
                gene_id,
                gene_symbol,
                "Gene",
                ensembl_id=gene_id,
                gene_symbol=gene_symbol,
            )

            # Add pathway node
            if pathway_id and pathway_id not in pathway_nodes:
                self.add_node(
                    pathway_id, pathway_name, "Pathway", source=source
                )
                pathway_nodes.add(pathway_id)

            # Add edge
            if pathway_id:
                self.add_edge(gene_id, "participates_in", pathway_id, source=source)

        logger.info(f"Loaded {len(df)} gene-pathway associations")

    def load_sex_de_genes(self, file_path: Path) -> None:
        """
        Load sex-differential expression data.

        Args:
            file_path: Path to sex_de_genes.parquet
        """
        logger.info(f"Loading sex-DE genes from {file_path}")
        df = pd.read_parquet(file_path)

        # Create tissue nodes
        tissues = df["tissue"].unique()
        for tissue in tissues:
            tissue_id = f"tissue:{tissue}"
            self.add_node(tissue_id, tissue, "Tissue")

        # Add sex-DE edges
        for _, row in df.iterrows():
            gene_id = row["ensembl_gene_id"]
            gene_symbol = row["gene_symbol"]
            tissue = row["tissue"]
            tissue_id = f"tissue:{tissue}"
            fold_change = row["fold_change_f_vs_m"]
            direction = row["direction"]
            p_value = row["p_value"]
            is_sex_de = row["is_sex_de"]

            # Add gene node
            self.add_node(
                gene_id,
                gene_symbol,
                "Gene",
                ensembl_id=gene_id,
                gene_symbol=gene_symbol,
            )

            # Add sex-DE edge
            if is_sex_de:
                self.add_edge(
                    gene_id,
                    "sex_differential_expression",
                    tissue_id,
                    fold_change=fold_change,
                    direction=direction,
                    p_value=p_value,
                    tissue_name=tissue,
                )

        logger.info(f"Loaded {len(df)} sex-DE associations")

    def load_adverse_events(self, file_path: Path, data_dir: Path) -> None:
        """
        Load drug-adverse event associations with sex stratification.

        Args:
            file_path: Path to ror_by_sex.parquet
            data_dir: Path to data directory for lookups
        """
        logger.info(f"Loading adverse events from {file_path}")
        df = pd.read_parquet(file_path)

        for _, row in df.iterrows():
            # Signal output columns: drug_name, pt, sex, ror, ror_lower, ror_upper, prr, a
            drug_name = str(row.get("drug_name", "")).strip()
            ae_name = str(row.get("pt", "")).strip()
            if not drug_name or not ae_name:
                continue
            drug_id = f"DRUG:{drug_name.upper().replace(' ', '_')}"
            ae_id = f"AE:{ae_name.upper().replace(' ', '_')}"
            sex = row.get("sex", "U")
            ror = row.get("ror", 1.0)
            ci_lower = row.get("ror_lower", row.get("ci_lower", 0.0))
            ci_upper = row.get("ror_upper", row.get("ci_upper", 0.0))
            prr = row.get("prr", 1.0)
            case_count = row.get("a", row.get("case_count", 0))

            # Add nodes
            self.add_node(drug_id, drug_name, "Drug", chembl_id=drug_id)
            self.add_node(ae_id, ae_name, "AdverseEvent", meddra_id=ae_id)

            # Add edge with sex-stratified properties
            self.add_edge(
                drug_id,
                "has_adverse_event",
                ae_id,
                sex=sex,
                ror=ror,
                ci_lower=ci_lower,
                ci_upper=ci_upper,
                prr=prr,
                case_count=case_count,
            )

        logger.info(f"Loaded {len(df)} drug-AE associations")


    def load_sex_differential_signals(self, file_path: Path) -> None:
        """
        Load sex-differential signals — the core innovation of SexDiffKG.
        
        Creates edges with log(ROR_female/ROR_male) as a property,
        making sex a structural dimension on drug-AE relationships.

        Args:
            file_path: Path to sex_differential.parquet
        """
        logger.info(f"Loading sex-differential signals from {file_path}")
        df = pd.read_parquet(file_path)

        added = 0
        for _, row in df.iterrows():
            drug_name = str(row.get("drug_name", "")).strip()
            ae_name = str(row.get("pt", "")).strip()
            if not drug_name or not ae_name:
                continue

            drug_id = f"DRUG:{drug_name.upper().replace(' ', '_')}"
            ae_id = f"AE:{ae_name.upper().replace(' ', '_')}"
            log_ror_ratio = row.get("log_ror_ratio", 0.0)
            direction = row.get("direction", "unknown")
            ror_male = row.get("ror_male", 0.0)
            ror_female = row.get("ror_female", 0.0)

            # Ensure nodes exist (they should from ror_by_sex loading)
            self.add_node(drug_id, drug_name, "Drug")
            self.add_node(ae_id, ae_name, "AdverseEvent")

            # Add sex-differential edge — THE key edge type
            self.add_edge(
                drug_id,
                "sex_differential_adverse_event",
                ae_id,
                log_ror_ratio=log_ror_ratio,
                direction=direction,
                ror_male=ror_male,
                ror_female=ror_female,
                source="FAERS_sex_stratified",
            )
            added += 1

        logger.info(f"Loaded {added} sex-differential signal edges")

    def save_nodes_tsv(self) -> Path:
        """
        Save nodes in KGX TSV format.

        Returns:
            Path to saved nodes file
        """
        output_file = self.output_dir / "nodes.tsv"
        logger.info(f"Saving {len(self.nodes)} nodes to {output_file}")

        nodes_list = []
        for node_id, node_data in self.nodes.items():
            node_dict = {
                "id": node_data["id"],
                "name": node_data["name"],
                "category": node_data["category"],
            }
            # Add additional properties as JSON
            extra_props = {
                k: v
                for k, v in node_data.items()
                if k not in ["id", "name", "category"]
            }
            if extra_props:
                node_dict["properties"] = json.dumps(extra_props)
            nodes_list.append(node_dict)

        df_nodes = pd.DataFrame(nodes_list)
        df_nodes = df_nodes[["id", "name", "category"] + 
                           [c for c in df_nodes.columns if c not in ["id", "name", "category"]]]
        df_nodes.to_csv(output_file, sep="\t", index=False)
        logger.info(f"Saved nodes to {output_file}")
        return output_file

    def save_edges_tsv(self) -> Path:
        """
        Save edges in KGX TSV format.

        Returns:
            Path to saved edges file
        """
        output_file = self.output_dir / "edges.tsv"
        logger.info(f"Saving {len(self.edges)} edges to {output_file}")

        edges_list = []
        for edge in self.edges:
            edge_dict = {
                "subject": edge["subject"],
                "predicate": edge["predicate"],
                "object": edge["object"],
            }
            # Add properties as JSON
            extra_props = {
                k: v
                for k, v in edge.items()
                if k not in ["subject", "predicate", "object"]
            }
            if extra_props:
                edge_dict["properties"] = json.dumps(extra_props)
            edges_list.append(edge_dict)

        df_edges = pd.DataFrame(edges_list)
        columns = ["subject", "predicate", "object"] + \
                 [c for c in df_edges.columns if c not in ["subject", "predicate", "object"]]
        df_edges = df_edges[columns]
        df_edges.to_csv(output_file, sep="\t", index=False)
        logger.info(f"Saved edges to {output_file}")
        return output_file

    def save_triples_tsv(self) -> Path:
        """
        Save triples in simple h,r,t format for PyKEEN.

        Returns:
            Path to saved triples file
        """
        output_file = self.output_dir / "triples.tsv"
        logger.info(f"Saving {len(self.triples)} triples to {output_file}")

        df_triples = pd.DataFrame(
            self.triples, columns=["head", "relation", "tail"]
        )
        df_triples.to_csv(output_file, sep="\t", index=False, header=False)
        logger.info(f"Saved triples to {output_file}")
        return output_file

    def get_statistics(self) -> Dict:
        """
        Get knowledge graph statistics.

        Returns:
            Dictionary with KG statistics
        """
        # Count node categories
        category_counts = {}
        for node in self.nodes.values():
            cat = node.get("category", "Unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Count edge predicates
        predicate_counts = {}
        for edge in self.edges:
            pred = edge.get("predicate", "unknown")
            predicate_counts[pred] = predicate_counts.get(pred, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_triples": len(self.triples),
            "node_categories": category_counts,
            "edge_predicates": predicate_counts,
        }


def main(args: argparse.Namespace) -> None:
    """
    Main pipeline for building SexDiffKG.

    Args:
        args: Command-line arguments
    """
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)

    logger.info("SexDiffKG builder starting")
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Output directory: {output_dir}")

    # Initialize builder
    builder = SexDiffKGBuilder(output_dir)

    # Load data
    try:
        # Drug targets
        drug_targets_file = data_dir / "processed" / "molecular" / "drug_targets.parquet"
        if drug_targets_file.exists():
            builder.load_drug_targets(drug_targets_file)
        else:
            logger.warning(f"Drug targets file not found: {drug_targets_file}")

        # PPI network
        ppi_file = data_dir / "processed" / "molecular" / "ppi_network.parquet"
        if ppi_file.exists():
            builder.load_ppi_network(ppi_file)
        else:
            logger.warning(f"PPI file not found: {ppi_file}")

        # Pathways
        pathways_file = data_dir / "processed" / "molecular" / "gene_pathways.parquet"
        if pathways_file.exists():
            builder.load_pathways(pathways_file)
        else:
            logger.warning(f"Pathways file not found: {pathways_file}")

        # Sex-DE genes
        sex_de_file = data_dir / "processed" / "molecular" / "sex_de_genes.parquet"
        if sex_de_file.exists():
            builder.load_sex_de_genes(sex_de_file)
        else:
            logger.warning(f"Sex-DE genes file not found: {sex_de_file}")

        # Adverse events (sex-stratified)
        ae_file = Path("results/signals_v2/ror_by_sex.parquet")
        if ae_file.exists():
            builder.load_adverse_events(ae_file, data_dir)
        else:
            logger.warning(f"Adverse events file not found: {ae_file}")

        # Sex-differential signals — the core innovation
        se_file = Path("results/signals_v2/sex_differential.parquet")
        if se_file.exists():
            builder.load_sex_differential_signals(se_file)
        else:
            logger.warning(f"Sex-differential signals file not found: {se_file}")

        # Save outputs
        builder.save_nodes_tsv()
        builder.save_edges_tsv()
        builder.save_triples_tsv()

        # Print statistics
        stats = builder.get_statistics()
        logger.info("Knowledge Graph Statistics:")
        logger.info(f"  Total nodes: {stats['total_nodes']}")
        logger.info(f"  Total edges: {stats['total_edges']}")
        logger.info(f"  Total triples: {stats['total_triples']}")
        logger.info("  Node categories:")
        for cat, count in stats["node_categories"].items():
            logger.info(f"    {cat}: {count}")
        logger.info("  Edge predicates:")
        for pred, count in stats["edge_predicates"].items():
            logger.info(f"    {pred}: {count}")

        logger.info("SexDiffKG builder completed successfully")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build SexDiffKG knowledge graph"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/",
        help="Root data directory",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/kg/",
        help="Output directory for KG files",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)

    main(args)
