#!/usr/bin/env python3
"""
SexDiffKG Data Lineage Audit
=============================
Traces every entity in triples.tsv back to source:
- Drug entities -> ChEMBL
- Gene/Protein entities -> Ensembl/UniProt
- Pathway/Reaction entities -> Reactome/KEGG
- Counts entities by source
- Identifies orphan entities

Author: Audit Module
Infrastructure: NVIDIA DGX Spark GB10 (ARM64, Python 3.13)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Tuple, Any
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================

HOME = Path.home()
BASE = HOME / "sexdiffkg"
DATA = BASE / "data"
KG = DATA / "kg"
RESULTS = BASE / "results"
AUDIT_OUT = RESULTS / "audits"

AUDIT_OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# ENTITY IDENTIFICATION
# ============================================================

def identify_entity_source(entity_id: str) -> str:
    """Identify the source of an entity based on its ID prefix."""
    if entity_id.startswith("CHEMBL"):
        return "ChEMBL"
    elif entity_id.startswith("ENSG"):
        return "Ensembl"
    elif entity_id.startswith("UP:"):
        return "UniProt"
    elif entity_id.startswith("REACT"):
        return "Reactome"
    elif entity_id.startswith("KEGG:"):
        return "KEGG"
    elif entity_id.startswith("GTEX:"):
        return "GTEx"
    elif entity_id.startswith("FAERS:"):
        return "FAERS"
    elif entity_id.startswith("STRING:"):
        return "STRING"
    elif any(entity_id.startswith(prefix) for prefix in ["GO:", "HP:", "DOID:", "MONDO:"]):
        return "Ontology"
    else:
        return "Unknown"

def get_entity_category(entity_id: str) -> str:
    """Get entity category based on source."""
    source = identify_entity_source(entity_id)
    category_map = {
        "ChEMBL": "Drug",
        "Ensembl": "Gene",
        "UniProt": "Protein",
        "Reactome": "Pathway",
        "KEGG": "Pathway",
        "GTEx": "Expression",
        "FAERS": "Event",
        "STRING": "Interaction",
        "Ontology": "Concept",
        "Unknown": "Unknown"
    }
    return category_map.get(source, "Unknown")

# ============================================================
# LINEAGE AUDIT CLASS
# ============================================================

class LineageAudit:
    def __init__(self):
        self.manifest = {
            "timestamp": datetime.now().isoformat(),
            "audit_version": "1.0",
            "results": {}
        }
        self.entity_sources = defaultdict(int)
        self.entity_categories = defaultdict(int)
        self.relation_types = defaultdict(int)
        self.all_entities = set()
        self.source_entities = defaultdict(set)

    def load_nodes(self) -> Dict[str, str]:
        """Load node IDs and their categories from nodes.tsv."""
        print("\n[1/4] Loading node data...")
        nodes = {}
        nodes_file = KG / "nodes.tsv"

        if not nodes_file.exists():
            print(f"WARNING: {nodes_file} not found")
            return nodes

        try:
            with open(nodes_file, "r", encoding="utf-8", errors="ignore") as f:
                # Skip header
                header = f.readline()
                for line_num, line in enumerate(f, 2):
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        node_id = parts[0]
                        node_category = parts[2]
                        nodes[node_id] = node_category

                print(f"Loaded {len(nodes)} nodes from {nodes_file.name}")
        except Exception as e:
            print(f"ERROR loading nodes: {e}")

        return nodes

    def analyze_entities(self) -> Dict[str, Any]:
        """Analyze all entities and their sources."""
        print("[2/4] Analyzing entity lineage...")
        triples_file = KG / "triples.tsv"

        if not triples_file.exists():
            print(f"ERROR: {triples_file} not found")
            return {}

        entity_count = 0
        try:
            with open(triples_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        subject = parts[0]
                        relation = parts[1]
                        obj = parts[2]

                        # Track entities
                        for entity in [subject, obj]:
                            if entity not in self.all_entities:
                                self.all_entities.add(entity)
                                source = identify_entity_source(entity)
                                category = get_entity_category(entity)
                                self.entity_sources[source] += 1
                                self.entity_categories[category] += 1
                                self.source_entities[source].add(entity)

                        # Track relations
                        self.relation_types[relation] += 1
                        entity_count += 1

                print(f"Processed {entity_count} triples")
                print(f"Total unique entities: {len(self.all_entities)}")
        except Exception as e:
            print(f"ERROR analyzing entities: {e}")

        return {
            "total_entities": len(self.all_entities),
            "total_triples": entity_count,
            "unique_sources": len(self.entity_sources),
            "unique_relation_types": len(self.relation_types)
        }

    def count_by_source(self) -> Dict[str, Any]:
        """Count entities by source."""
        print("[3/4] Counting entities by source...")

        source_summary = {}
        for source in sorted(self.entity_sources.keys()):
            count = self.entity_sources[source]
            sample_entities = list(self.source_entities[source])[:5]
            source_summary[source] = {
                "count": count,
                "percentage": round(100 * count / len(self.all_entities), 2) if self.all_entities else 0,
                "sample_entities": sample_entities
            }

        # Print summary
        print("\nEntity count by source:")
        for source, info in sorted(source_summary.items(), key=lambda x: x[1]["count"], reverse=True):
            pct = info["percentage"]
            print(f"  {source:20} {info['count']:>10,} entities ({pct:>6.2f}%)")

        return source_summary

    def analyze_relations(self) -> Dict[str, Any]:
        """Analyze relation type distribution."""
        print("[4/4] Analyzing relation types...")

        relation_summary = {}
        total_relations = sum(self.relation_types.values())

        for relation in sorted(self.relation_types.keys()):
            count = self.relation_types[relation]
            relation_summary[relation] = {
                "count": count,
                "percentage": round(100 * count / total_relations, 2) if total_relations else 0
            }

        # Print top relations
        print("\nTop 10 relation types:")
        for relation, info in sorted(
            relation_summary.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:10]:
            pct = info["percentage"]
            print(f"  {relation:30} {info['count']:>10,} edges ({pct:>6.2f}%)")

        return relation_summary

    def identify_orphans(self, nodes: Dict[str, str]) -> Dict[str, Any]:
        """Identify orphan entities (in triples but not in nodes)."""
        print("\nIdentifying orphan entities...")

        orphans = {
            "in_triples_not_in_nodes": list(self.all_entities - set(nodes.keys())),
            "in_nodes_not_in_triples": list(set(nodes.keys()) - self.all_entities)
        }

        # Count orphans by source
        orphan_sources = defaultdict(int)
        for orphan in orphans["in_triples_not_in_nodes"]:
            source = identify_entity_source(orphan)
            orphan_sources[source] += 1

        orphans["orphan_by_source"] = dict(orphan_sources)
        orphans["total_orphans_in_triples"] = len(orphans["in_triples_not_in_nodes"])
        orphans["total_orphans_in_nodes"] = len(orphans["in_nodes_not_in_triples"])

        if orphans["total_orphans_in_triples"] > 0:
            print(f"WARNING: {orphans['total_orphans_in_triples']} orphan entities in triples but not in nodes!")
            print("  Sample orphans:")
            for orphan in orphans["in_triples_not_in_nodes"][:10]:
                source = identify_entity_source(orphan)
                print(f"    {orphan} ({source})")

        return orphans

    def run_audit(self) -> Dict[str, Any]:
        """Run complete lineage audit."""
        print("\n" + "="*60)
        print("SexDiffKG DATA LINEAGE AUDIT")
        print("="*60)

        # Load nodes
        nodes = self.load_nodes()

        # Analyze entities
        entity_stats = self.analyze_entities()
        self.manifest["results"]["entity_statistics"] = entity_stats

        # Count by source
        source_summary = self.count_by_source()
        self.manifest["results"]["entities_by_source"] = source_summary

        # Analyze relations
        relation_summary = self.analyze_relations()
        self.manifest["results"]["relations"] = relation_summary

        # Identify orphans
        orphans = self.identify_orphans(nodes)
        self.manifest["results"]["orphan_entities"] = orphans

        # Summary statistics
        self.manifest["results"]["entity_category_distribution"] = dict(self.entity_categories)

        return self.manifest

    def save_manifest(self, filepath: Path):
        """Save manifest to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.manifest, f, indent=2)
        print(f"\nLineage audit saved to: {filepath}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    audit = LineageAudit()
    manifest = audit.run_audit()

    output_file = AUDIT_OUT / "data_lineage_audit.json"
    audit.save_manifest(output_file)

    print("\n" + "="*60)
    print("LINEAGE AUDIT COMPLETE")
    print("="*60)

    sys.exit(0)
