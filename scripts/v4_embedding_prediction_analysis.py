#!/usr/bin/env python3
"""
SexDiffKG v4 — Comprehensive Embedding-Based Novel Prediction Analysis
=======================================================================
Uses the ComplEx v4 model (MRR 0.2484, Hits@10 40.69%) to:
1. Report embedding statistics and model diagnostics
2. Identify hub entities by embedding norm
3. Score ALL novel (Drug, sex_differential_adverse_event, AE) triples
4. Filter and rank top 100 clinically meaningful predictions
5. Categorize predictions by confidence tier and clinical relevance

Author: JShaik / Claude Opus 4.6
Date: 2026-03-04
"""

import json, time, gc, sys, os
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.models import ComplEx

BASE = Path.home() / "sexdiffkg"
KG_DIR = BASE / "data/kg_v4"
EMB_DIR = BASE / "results/kg_embeddings_v4/ComplEx"
OUT_DIR = BASE / "results/analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
TOP_N = 100  # Top predictions for the main output


def compute_embedding_stats(model, entity_to_id, relation_to_id):
    """Compute comprehensive embedding statistics."""
    print("\n" + "=" * 70)
    print("EMBEDDING STATISTICS")
    print("=" * 70)

    # Entity embeddings (ComplEx uses complex-valued: dim 400 = 200 real + 200 imag)
    entity_emb = model.entity_representations[0](indices=None).detach().cpu()
    relation_emb = model.relation_representations[0](indices=None).detach().cpu()

    print(f"\nEntity embeddings shape: {entity_emb.shape}")
    print(f"  - Num entities: {entity_emb.shape[0]:,}")
    print(f"  - Embedding dim (raw): {entity_emb.shape[1]} (200 complex = 400 float)")
    print(f"  - Dtype: {entity_emb.dtype}")
    print(f"  - Memory: {entity_emb.element_size() * entity_emb.nelement() / 1e6:.1f} MB")

    print(f"\nRelation embeddings shape: {relation_emb.shape}")
    print(f"  - Num relations: {relation_emb.shape[0]}")
    print(f"  - Embedding dim (raw): {relation_emb.shape[1]}")

    # Norm statistics for entities
    entity_norms = torch.norm(entity_emb, dim=1)
    print(f"\nEntity embedding norms:")
    print(f"  Mean:   {entity_norms.mean().item():.4f}")
    print(f"  Std:    {entity_norms.std().item():.4f}")
    print(f"  Min:    {entity_norms.min().item():.4f}")
    print(f"  Max:    {entity_norms.max().item():.4f}")
    print(f"  Median: {torch.median(entity_norms).item():.4f}")

    # Norm statistics for relations
    relation_norms = torch.norm(relation_emb, dim=1)
    id_to_relation = {v: k for k, v in relation_to_id.items()}
    print(f"\nRelation embedding norms:")
    for i in range(relation_emb.shape[0]):
        print(f"  {id_to_relation[i]}: {relation_norms[i].item():.4f}")

    # Norm by entity type
    id_to_entity = {v: k for k, v in entity_to_id.items()}
    type_norms = defaultdict(list)
    for idx in range(len(id_to_entity)):
        ent = id_to_entity[idx]
        if ent.startswith("DRUG:"):
            etype = "Drug"
        elif ent.startswith("AE:"):
            etype = "AdverseEvent"
        elif ent.startswith("GENE:"):
            etype = "Gene"
        elif ent.startswith("PROTEIN:"):
            etype = "Protein"
        elif ent.startswith("PATHWAY:"):
            etype = "Pathway"
        elif ent.startswith("TISSUE:"):
            etype = "Tissue"
        else:
            etype = "Other"
        type_norms[etype].append(entity_norms[idx].item())

    print(f"\nEmbedding norms by entity type:")
    for etype in sorted(type_norms.keys()):
        norms = type_norms[etype]
        print(f"  {etype}: count={len(norms):,}, mean={np.mean(norms):.4f}, "
              f"std={np.std(norms):.4f}, max={np.max(norms):.4f}")

    # Top hub entities by embedding norm
    top_k = 25
    top_indices = torch.argsort(entity_norms, descending=True)[:top_k]
    print(f"\nTop {top_k} entities by embedding norm:")
    hub_entities = []
    for rank, idx in enumerate(top_indices):
        ent = id_to_entity[idx.item()]
        norm = entity_norms[idx.item()].item()
        etype = ent.split(":")[0] if ":" in ent else "Unknown"
        name = ent.split(":", 1)[1] if ":" in ent else ent
        print(f"  {rank+1:>3}. [{etype:>10}] {name:<50} norm={norm:.4f}")
        hub_entities.append({
            "rank": rank + 1,
            "entity_id": ent,
            "entity_type": etype,
            "entity_name": name,
            "embedding_norm": round(norm, 4),
        })

    return {
        "entity_count": int(entity_emb.shape[0]),
        "relation_count": int(relation_emb.shape[0]),
        "embedding_dim_complex": 200,
        "embedding_dim_raw": int(entity_emb.shape[1]),
        "entity_embedding_memory_mb": round(entity_emb.element_size() * entity_emb.nelement() / 1e6, 1),
        "entity_norm_stats": {
            "mean": round(entity_norms.mean().item(), 4),
            "std": round(entity_norms.std().item(), 4),
            "min": round(entity_norms.min().item(), 4),
            "max": round(entity_norms.max().item(), 4),
            "median": round(torch.median(entity_norms).item(), 4),
        },
        "relation_norms": {id_to_relation[i]: round(relation_norms[i].item(), 4)
                           for i in range(relation_emb.shape[0])},
        "norms_by_type": {
            etype: {
                "count": len(norms),
                "mean": round(np.mean(norms), 4),
                "std": round(np.std(norms), 4),
                "max": round(np.max(norms), 4),
            }
            for etype, norms in sorted(type_norms.items())
        },
        "hub_entities_by_norm": hub_entities,
    }, entity_norms, type_norms


def main():
    start = time.time()
    print("=" * 70)
    print("SexDiffKG v4 — ComplEx Embedding Prediction Analysis")
    print("=" * 70)
    print(f"Model: ComplEx v4 (MRR 0.2484, Hits@10 40.69%)")
    print(f"Output: {OUT_DIR / 'embedding_predictions.json'}")

    # ──────────────────────────────────────────────────────────────────
    # 1. Load KG triples and reconstruct TriplesFactory
    # ──────────────────────────────────────────────────────────────────
    triples_file = KG_DIR / "triples.tsv"
    print(f"\n[1/8] Loading triples from {triples_file}")
    df = pd.read_csv(triples_file, sep="\t", header=None, names=["h", "r", "t"])
    df = df.dropna()
    print(f"  Total triples loaded: {len(df):,}")

    # The ComplEx model was trained on 5 relations (excluding sex_differential_expression)
    # Check which relations the model has
    relation_counts = df["r"].value_counts()
    print(f"\n  Relation distribution in KG:")
    for rel, cnt in relation_counts.items():
        print(f"    {rel}: {cnt:,}")

    # Filter to same relations used in training
    # The model has exactly 5 relations; sex_differential_expression was excluded
    df_model = df[df["r"] != "sex_differential_expression"].copy()
    df_model["h"] = df_model["h"].astype(str)
    df_model["r"] = df_model["r"].astype(str)
    df_model["t"] = df_model["t"].astype(str)
    print(f"\n  Training-compatible triples: {len(df_model):,} (5 relations)")

    # ──────────────────────────────────────────────────────────────────
    # 2. Create TriplesFactory (alphabetical sorting = matches training)
    # ──────────────────────────────────────────────────────────────────
    print(f"\n[2/8] Creating TriplesFactory...")
    factory = TriplesFactory.from_labeled_triples(
        triples=df_model[["h", "r", "t"]].values,
        create_inverse_triples=False,
    )
    print(f"  Entities: {factory.num_entities:,}")
    print(f"  Relations: {factory.num_relations}")

    assert factory.num_entities == 113012, f"Entity mismatch: {factory.num_entities} != 113012"
    assert factory.num_relations == 5, f"Relation mismatch: {factory.num_relations} != 5"

    entity_to_id = factory.entity_to_id
    relation_to_id = factory.relation_to_id
    id_to_entity = {v: k for k, v in entity_to_id.items()}
    id_to_relation = {v: k for k, v in relation_to_id.items()}

    print(f"\n  Relation ID mapping:")
    for name, idx in sorted(relation_to_id.items(), key=lambda x: x[1]):
        print(f"    {idx}: {name}")

    # ──────────────────────────────────────────────────────────────────
    # 3. Load ComplEx model
    # ──────────────────────────────────────────────────────────────────
    print(f"\n[3/8] Loading ComplEx v4 model...")
    model = ComplEx(
        triples_factory=factory,
        embedding_dim=200,
        random_seed=SEED,
    )
    state_dict = torch.load(EMB_DIR / "model.pt", map_location="cpu", weights_only=False)
    model.load_state_dict(state_dict)
    model.eval()
    print(f"  Model loaded successfully")
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")

    # ──────────────────────────────────────────────────────────────────
    # 4. Compute embedding statistics
    # ──────────────────────────────────────────────────────────────────
    print(f"\n[4/8] Computing embedding statistics...")
    emb_stats, entity_norms, type_norms = compute_embedding_stats(
        model, entity_to_id, relation_to_id
    )

    # ──────────────────────────────────────────────────────────────────
    # 5. Identify drug and AE entities, count degrees
    # ──────────────────────────────────────────────────────────────────
    print(f"\n[5/8] Analyzing entity connectivity...")
    drug_ids = sorted([entity_to_id[e] for e in entity_to_id if e.startswith("DRUG:")])
    ae_ids = sorted([entity_to_id[e] for e in entity_to_id if e.startswith("AE:")])
    print(f"  Drug entities: {len(drug_ids):,}")
    print(f"  AE entities: {len(ae_ids):,}")

    # Count edges per drug and per AE
    drug_degrees = Counter()
    ae_degrees = Counter()
    for _, row in df_model.iterrows():
        h = row["h"]
        t = row["t"]
        if h.startswith("DRUG:"):
            drug_degrees[h] += 1
        if t.startswith("AE:"):
            ae_degrees[t] += 1
        if h.startswith("AE:"):
            ae_degrees[h] += 1

    # Get existing SDAE and HAE edges
    sdae_rel = "sex_differential_adverse_event"
    hae_rel = "has_adverse_event"
    sdae_id = relation_to_id[sdae_rel]
    hae_id = relation_to_id[hae_rel]

    existing_sdae = set()
    sdae_df = df_model[df_model["r"] == sdae_rel]
    for _, row in sdae_df.iterrows():
        h_id = entity_to_id.get(row["h"])
        t_id = entity_to_id.get(row["t"])
        if h_id is not None and t_id is not None:
            existing_sdae.add((h_id, t_id))
    print(f"  Existing SDAE edges: {len(existing_sdae):,}")

    existing_hae = set()
    hae_df = df_model[df_model["r"] == hae_rel]
    for _, row in hae_df.iterrows():
        h_id = entity_to_id.get(row["h"])
        t_id = entity_to_id.get(row["t"])
        if h_id is not None and t_id is not None:
            existing_hae.add((h_id, t_id))
    print(f"  Existing HAE edges: {len(existing_hae):,}")

    # Drugs with SDAE edges (these have known sex-differential signals)
    drugs_with_sdae = set(h for h, _ in existing_sdae)
    drugs_with_hae = set(h for h, _ in existing_hae)
    print(f"  Drugs with >=1 SDAE edge: {len(drugs_with_sdae):,}")
    print(f"  Drugs with >=1 HAE edge: {len(drugs_with_hae):,}")

    # ──────────────────────────────────────────────────────────────────
    # 6. Score novel Drug-SDAE-AE triples
    # ──────────────────────────────────────────────────────────────────
    print(f"\n[6/8] Scoring novel (Drug, sex_differential_adverse_event, AE) triples...")
    total_possible = len(drug_ids) * len(ae_ids)
    print(f"  Total possible pairs: {total_possible:,}")
    print(f"  Minus existing SDAE: {len(existing_sdae):,}")
    print(f"  Novel to score: ~{total_possible - len(existing_sdae):,}")

    # We focus on drugs that have at least SOME edges (degree >= 5)
    # This filters out ultra-rare drugs where embeddings are poorly learned
    min_drug_degree = 5
    qualified_drug_ids = [d for d in drug_ids
                          if drug_degrees.get(id_to_entity[d], 0) >= min_drug_degree]
    print(f"  Drugs with degree >= {min_drug_degree}: {len(qualified_drug_ids):,}")

    # Similarly filter AEs to those with some connectivity
    min_ae_degree = 3
    qualified_ae_ids = [a for a in ae_ids
                        if ae_degrees.get(id_to_entity[a], 0) >= min_ae_degree]
    print(f"  AEs with degree >= {min_ae_degree}: {len(qualified_ae_ids):,}")

    batch_size = 500
    all_scores = []
    total_novel = 0

    with torch.no_grad():
        for i in range(0, len(qualified_drug_ids), batch_size):
            batch_drugs = qualified_drug_ids[i:i+batch_size]
            batch_triples = []
            batch_pairs = []

            for d_id in batch_drugs:
                for a_id in qualified_ae_ids:
                    if (d_id, a_id) not in existing_sdae:
                        batch_triples.append([d_id, sdae_id, a_id])
                        batch_pairs.append((d_id, a_id))

            if not batch_triples:
                continue

            total_novel += len(batch_triples)

            # Score in sub-batches
            sub_batch = 100000
            for j in range(0, len(batch_triples), sub_batch):
                t = torch.tensor(batch_triples[j:j+sub_batch], dtype=torch.long)
                scores = model.score_hrt(t).squeeze().cpu().numpy()
                if scores.ndim == 0:
                    scores = np.array([scores.item()])

                # Keep top scores from this sub-batch
                top_k = min(TOP_N * 5, len(scores))
                if top_k > 0:
                    top_idx = np.argpartition(scores, -top_k)[-top_k:]
                    for idx in top_idx:
                        pair = batch_pairs[j + idx]
                        all_scores.append((pair[0], pair[1], float(scores[idx])))

            if (i // batch_size) % 20 == 0:
                elapsed = time.time() - start
                pct = min(100.0, (i + batch_size) / len(qualified_drug_ids) * 100)
                print(f"  Progress: {pct:.1f}% | drugs processed: {i+batch_size} | "
                      f"novel scored: {total_novel:,} | elapsed: {elapsed:.0f}s")

    print(f"\n  Total novel triples scored: {total_novel:,}")

    # ──────────────────────────────────────────────────────────────────
    # 7. Rank and annotate predictions
    # ──────────────────────────────────────────────────────────────────
    print(f"\n[7/8] Ranking and annotating top {TOP_N} predictions...")
    all_scores.sort(key=lambda x: x[2], reverse=True)

    # Deduplicate (keep highest score per pair)
    seen_pairs = set()
    unique_scores = []
    for d_id, a_id, score in all_scores:
        if (d_id, a_id) not in seen_pairs:
            seen_pairs.add((d_id, a_id))
            unique_scores.append((d_id, a_id, score))

    top_predictions = unique_scores[:TOP_N]

    results = []
    for rank, (d_id, a_id, score) in enumerate(top_predictions, 1):
        drug_ent = id_to_entity[d_id]
        ae_ent = id_to_entity[a_id]
        drug_name = drug_ent.replace("DRUG:", "")
        ae_name = ae_ent.replace("AE:", "")
        has_hae = (d_id, a_id) in existing_hae
        drug_deg = drug_degrees.get(drug_ent, 0)
        ae_deg = ae_degrees.get(ae_ent, 0)
        drug_sdae_count = sum(1 for h, _ in existing_sdae if h == d_id)
        ae_sdae_count = sum(1 for _, t in existing_sdae if t == a_id)
        drug_norm = entity_norms[d_id].item()
        ae_norm = entity_norms[a_id].item()

        # Confidence tier based on score percentile and connectivity
        if score >= 12.0 and has_hae and drug_deg >= 50:
            tier = "HIGH"
        elif score >= 10.0 and (has_hae or drug_deg >= 20):
            tier = "MEDIUM"
        elif score >= 8.0:
            tier = "LOW"
        else:
            tier = "EXPLORATORY"

        results.append({
            "rank": rank,
            "drug": drug_name,
            "adverse_event": ae_name,
            "drug_entity_id": drug_ent,
            "ae_entity_id": ae_ent,
            "score": round(score, 6),
            "confidence_tier": tier,
            "has_adverse_event_edge": has_hae,
            "drug_degree": drug_deg,
            "ae_degree": ae_deg,
            "drug_existing_sdae_count": drug_sdae_count,
            "ae_existing_sdae_count": ae_sdae_count,
            "drug_embedding_norm": round(drug_norm, 4),
            "ae_embedding_norm": round(ae_norm, 4),
        })

    # ──────────────────────────────────────────────────────────────────
    # 8. Save results
    # ──────────────────────────────────────────────────────────────────
    print(f"\n[8/8] Saving results...")

    # Tier breakdown
    tier_counts = Counter(r["confidence_tier"] for r in results)
    hae_count = sum(1 for r in results if r["has_adverse_event_edge"])
    novel_count = sum(1 for r in results if not r["has_adverse_event_edge"])

    # Unique drugs and AEs in predictions
    pred_drugs = set(r["drug"] for r in results)
    pred_aes = set(r["adverse_event"] for r in results)

    # Score distribution
    scores_arr = [r["score"] for r in results]

    output = {
        "metadata": {
            "model": "ComplEx v4",
            "model_metrics": {
                "MRR": 0.2484,
                "Hits@1": 0.1678,
                "Hits@3": 0.2692,
                "Hits@5": 0.3234,
                "Hits@10": 0.4069,
                "AMRI": 0.9902,
            },
            "embedding_dim": 200,
            "num_entities": 113012,
            "num_relations": 5,
            "prediction_target_relation": sdae_rel,
            "min_drug_degree_filter": min_drug_degree,
            "min_ae_degree_filter": min_ae_degree,
            "qualified_drugs": len(qualified_drug_ids),
            "qualified_aes": len(qualified_ae_ids),
            "total_novel_scored": total_novel,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "runtime_seconds": round(time.time() - start, 1),
        },
        "embedding_statistics": emb_stats,
        "prediction_summary": {
            "top_n": TOP_N,
            "score_range": [round(min(scores_arr), 4), round(max(scores_arr), 4)],
            "score_mean": round(np.mean(scores_arr), 4),
            "score_std": round(np.std(scores_arr), 4),
            "confidence_tiers": dict(tier_counts),
            "with_has_adverse_event_edge": hae_count,
            "truly_novel_pairs": novel_count,
            "unique_drugs": len(pred_drugs),
            "unique_adverse_events": len(pred_aes),
            "existing_sdae_edges_in_kg": len(existing_sdae),
            "existing_hae_edges_in_kg": len(existing_hae),
        },
        "predictions": results,
    }

    out_path = OUT_DIR / "embedding_predictions.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Saved to: {out_path}")
    print(f"  File size: {os.path.getsize(out_path) / 1024:.1f} KB")

    # Also save a compact TSV
    tsv_path = OUT_DIR / "embedding_predictions_top100.tsv"
    pd.DataFrame(results).to_csv(tsv_path, sep="\t", index=False)
    print(f"  TSV saved to: {tsv_path}")

    # ──────────────────────────────────────────────────────────────────
    # Print summary
    # ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*90}")
    print(f"TOP {TOP_N} PREDICTED NOVEL sex_differential_adverse_event EDGES")
    print(f"{'='*90}")
    print(f"{'Rk':>3} {'Score':>8} {'Tier':>6} {'HAE':>4} {'DDeg':>5} {'Drug':<35} {'Adverse Event':<35}")
    print("-" * 100)
    for r in results[:TOP_N]:
        hae_flag = "Y" if r["has_adverse_event_edge"] else "N"
        print(f"{r['rank']:>3} {r['score']:>8.3f} {r['confidence_tier']:>6} "
              f"{hae_flag:>4} {r['drug_degree']:>5} "
              f"{r['drug'][:34]:<35} {r['adverse_event'][:34]:<35}")

    print(f"\n{'='*90}")
    print(f"SUMMARY")
    print(f"{'='*90}")
    print(f"  Model: ComplEx v4 (MRR=0.2484, Hits@10=40.69%)")
    print(f"  Entities: {factory.num_entities:,} | Relations: {factory.num_relations}")
    print(f"  Drug candidates: {len(qualified_drug_ids):,} (degree >= {min_drug_degree})")
    print(f"  AE candidates: {len(qualified_ae_ids):,} (degree >= {min_ae_degree})")
    print(f"  Novel triples scored: {total_novel:,}")
    print(f"  Top {TOP_N} predictions saved")
    print(f"    - Confidence tiers: {dict(tier_counts)}")
    print(f"    - With HAE edge: {hae_count} | Truly novel: {novel_count}")
    print(f"    - Unique drugs: {len(pred_drugs)} | Unique AEs: {len(pred_aes)}")
    print(f"    - Score range: [{min(scores_arr):.4f}, {max(scores_arr):.4f}]")
    print(f"  Runtime: {(time.time()-start)/60:.1f} minutes")
    print(f"  Output: {out_path}")


if __name__ == "__main__":
    main()
