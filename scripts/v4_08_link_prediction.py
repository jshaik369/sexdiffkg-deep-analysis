#!/usr/bin/env python3
"""
SexDiffKG v4 — Step 8: Link Prediction using ComplEx v4 embeddings
==================================================================
Predicts novel sex-differential drug-AE associations not in the training set.
Uses the pre-trained ComplEx v4 model (MRR 0.2484, Hits@10 40.69%).

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-04
"""

import json, time, gc, sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.models import ComplEx

BASE = Path.home() / "sexdiffkg"
KG_DIR = BASE / "data/kg_v4"
EMB_DIR = BASE / "results/kg_embeddings_v4/ComplEx"
OUT_DIR = BASE / "results/link_predictions"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
TOP_N = 500  # Top predictions to save


def main():
    start = time.time()
    print("=" * 70)
    print("SexDiffKG v4 — ComplEx Link Prediction")
    print("=" * 70)

    # 1. Load triples (exclude sex_differential_expression — not in ComplEx training)
    triples_file = KG_DIR / "triples.tsv"
    print(f"Loading triples from {triples_file}")
    df = pd.read_csv(triples_file, sep="\t", header=None, names=["h", "r", "t"])
    df = df.dropna()
    df = df[df["r"] != "sex_differential_expression"]
    df["h"] = df["h"].astype(str)
    df["r"] = df["r"].astype(str)
    df["t"] = df["t"].astype(str)
    print(f"Loaded {len(df):,} triples (5 relations, sans sex_diff_expression)")

    # 2. Create TriplesFactory (alphabetical entity/relation sorting = same as training)
    factory = TriplesFactory.from_labeled_triples(
        triples=df[["h", "r", "t"]].values,
        create_inverse_triples=False,
    )
    print(f"Entities: {factory.num_entities:,}, Relations: {factory.num_relations:,}")

    if factory.num_entities != 113012:
        print(f"WARNING: Entity count {factory.num_entities} != expected 113,012")
    if factory.num_relations != 5:
        print(f"WARNING: Relation count {factory.num_relations} != expected 5")

    # 3. Create ComplEx model and load weights
    print("Loading ComplEx v4 model weights...")
    model = ComplEx(
        triples_factory=factory,
        embedding_dim=200,
        random_seed=SEED,
    )
    state_dict = torch.load(EMB_DIR / "model.pt", map_location="cpu", weights_only=False)
    model.load_state_dict(state_dict)
    model.eval()
    print("Model loaded successfully")

    # 4. Get entity and relation mappings
    entity_to_id = factory.entity_to_id
    relation_to_id = factory.relation_to_id
    id_to_entity = {v: k for k, v in entity_to_id.items()}
    id_to_relation = {v: k for k, v in relation_to_id.items()}

    print("\nRelation mappings:")
    for name, idx in sorted(relation_to_id.items(), key=lambda x: x[1]):
        print(f"  {idx}: {name}")

    # 5. Get sex_differential_adverse_event relation ID
    sdae_rel = "sex_differential_adverse_event"
    if sdae_rel not in relation_to_id:
        print(f"ERROR: '{sdae_rel}' not in relations!")
        sys.exit(1)
    sdae_id = relation_to_id[sdae_rel]
    print(f"\nTarget relation: {sdae_rel} (id={sdae_id})")

    # 6. Identify Drug and AE entities
    drug_ids = [entity_to_id[e] for e in entity_to_id if e.startswith("DRUG:")]
    ae_ids = [entity_to_id[e] for e in entity_to_id if e.startswith("AE:")]
    print(f"Drug entities: {len(drug_ids):,}")
    print(f"AE entities: {len(ae_ids):,}")

    # 7. Get existing sex_differential_adverse_event triples (to exclude from predictions)
    existing_sdae = set()
    sdae_df = df[df["r"] == sdae_rel]
    for _, row in sdae_df.iterrows():
        h_id = entity_to_id.get(row["h"])
        t_id = entity_to_id.get(row["t"])
        if h_id is not None and t_id is not None:
            existing_sdae.add((h_id, t_id))
    print(f"Existing {sdae_rel} triples: {len(existing_sdae):,}")

    # Also get existing has_adverse_event triples
    hae_rel = "has_adverse_event"
    hae_id = relation_to_id[hae_rel]
    existing_hae = set()
    hae_df = df[df["r"] == hae_rel]
    for _, row in hae_df.iterrows():
        h_id = entity_to_id.get(row["h"])
        t_id = entity_to_id.get(row["t"])
        if h_id is not None and t_id is not None:
            existing_hae.add((h_id, t_id))
    print(f"Existing {hae_rel} triples: {len(existing_hae):,}")

    # 8. Score all (Drug, sex_differential_adverse_event, AE) triples not in existing
    print(f"\nScoring novel Drug-SDAE-AE triples...")
    print(f"Total possible: {len(drug_ids) * len(ae_ids):,}")

    # Process in batches to manage memory
    batch_size = 1000
    all_scores = []
    total_novel = 0

    drug_tensor = torch.tensor(drug_ids, dtype=torch.long)
    ae_tensor = torch.tensor(ae_ids, dtype=torch.long)
    rel_tensor = torch.tensor([sdae_id], dtype=torch.long)

    with torch.no_grad():
        for i in range(0, len(drug_ids), batch_size):
            batch_drugs = drug_ids[i:i+batch_size]
            batch_triples = []
            batch_pairs = []

            for d_id in batch_drugs:
                for a_id in ae_ids:
                    if (d_id, a_id) not in existing_sdae:
                        batch_triples.append([d_id, sdae_id, a_id])
                        batch_pairs.append((d_id, a_id))

            if not batch_triples:
                continue

            total_novel += len(batch_triples)

            # Score in sub-batches
            sub_batch = 50000
            for j in range(0, len(batch_triples), sub_batch):
                t = torch.tensor(batch_triples[j:j+sub_batch], dtype=torch.long)
                scores = model.score_hrt(t).squeeze().cpu().numpy()
                if scores.ndim == 0:
                    scores = np.array([scores.item()])

                # Keep top scores from this sub-batch
                top_k = min(TOP_N, len(scores))
                top_idx = np.argpartition(scores, -top_k)[-top_k:]
                for idx in top_idx:
                    pair = batch_pairs[j + idx]
                    all_scores.append((pair[0], pair[1], float(scores[idx])))

            if (i // batch_size) % 10 == 0:
                elapsed = time.time() - start
                pct = min(100, (i + batch_size) / len(drug_ids) * 100)
                print(f"  Progress: {pct:.1f}% ({i+batch_size}/{len(drug_ids)} drugs), "
                      f"novel triples scored: {total_novel:,}, elapsed: {elapsed:.0f}s")

    print(f"\nTotal novel triples scored: {total_novel:,}")

    # 9. Get top-N predictions
    all_scores.sort(key=lambda x: x[2], reverse=True)
    top_predictions = all_scores[:TOP_N]

    # 10. Enrich with drug/AE names and existing edge info
    results = []
    for d_id, a_id, score in top_predictions:
        drug_name = id_to_entity[d_id]
        ae_name = id_to_entity[a_id]
        has_hae = (d_id, a_id) in existing_hae
        results.append({
            "drug": drug_name,
            "adverse_event": ae_name,
            "score": round(score, 6),
            "has_adverse_event_edge": has_hae,
            "drug_name_clean": drug_name.replace("DRUG:", ""),
            "ae_name_clean": ae_name.replace("AE:", ""),
        })

    # 11. Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUT_DIR / "complex_v4_sdae_predictions.tsv", sep="\t", index=False)
    results_df.to_json(OUT_DIR / "complex_v4_sdae_predictions.json", orient="records", indent=2)

    # 12. Summary statistics
    has_hae_count = sum(1 for r in results if r["has_adverse_event_edge"])
    novel_count = sum(1 for r in results if not r["has_adverse_event_edge"])

    summary = {
        "model": "ComplEx v4",
        "prediction_type": "sex_differential_adverse_event",
        "total_drugs": len(drug_ids),
        "total_aes": len(ae_ids),
        "existing_sdae_edges": len(existing_sdae),
        "existing_hae_edges": len(existing_hae),
        "total_novel_scored": total_novel,
        "top_n_saved": len(results),
        "top_n_with_hae_edge": has_hae_count,
        "top_n_truly_novel": novel_count,
        "score_range": [round(results[-1]["score"], 6), round(results[0]["score"], 6)],
        "runtime_minutes": round((time.time() - start) / 60, 2),
    }

    with open(OUT_DIR / "prediction_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # 13. Print top 30
    print(f"\n{'='*90}")
    print(f"TOP 30 PREDICTED sex_differential_adverse_event EDGES")
    print(f"{'='*90}")
    print(f"{'Rank':>4} {'Score':>10} {'HAE':>4} {'Drug':<35} {'Adverse Event':<35}")
    print("-" * 90)
    for i, r in enumerate(results[:30]):
        hae_flag = "Y" if r["has_adverse_event_edge"] else "N"
        print(f"{i+1:>4} {r['score']:>10.4f} {hae_flag:>4} {r['drug_name_clean']:<35} {r['ae_name_clean']:<35}")

    print(f"\n{'='*90}")
    print(f"SUMMARY")
    print(f"{'='*90}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print(f"\nResults saved to: {OUT_DIR}/")
    print(f"Total runtime: {(time.time()-start)/60:.1f} minutes")


if __name__ == "__main__":
    main()
