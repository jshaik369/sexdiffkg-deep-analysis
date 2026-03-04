#!/usr/bin/env python3
"""Comprehensive model comparison script.
Compares ComplEx v4, DistMult v4, DistMult v4.1, RotatE v4.1 side by side.
Run after all training completes."""

import json
import os
from pathlib import Path
from datetime import datetime

BASE = Path('/home/jshaik369/sexdiffkg')

def load_metrics(name, path):
    """Load metrics from a JSON file."""
    full_path = BASE / path
    if full_path.exists():
        with open(full_path) as f:
            data = json.load(f)
        return data
    return None

def extract_pykeen_metrics(data):
    """Extract key metrics from PyKEEN results."""
    if not data:
        return None
    
    metrics = data.get('metrics', {})
    if 'both' in metrics:
        m = metrics['both']['realistic']
    elif 'realistic' in metrics:
        m = metrics['realistic']
    else:
        m = metrics
    
    return {
        'MRR': m.get('inverse_harmonic_mean_rank', m.get('MRR', None)),
        'Hits@1': m.get('hits_at_1', m.get('Hits_at_1', None)),
        'Hits@3': m.get('hits_at_3', m.get('Hits_at_3', None)),
        'Hits@5': m.get('hits_at_5', m.get('Hits_at_5', None)),
        'Hits@10': m.get('hits_at_10', m.get('Hits_at_10', None)),
        'AMRI': m.get('adjusted_mean_rank_index', m.get('AMRI', None)),
    }

print(f"{'='*60}")
print(f"SexDiffKG Model Comparison — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}\n")

# Collect all model results
models = {}

# ComplEx v4
data = load_metrics('ComplEx v4', 'results/kg_embeddings_v4/ComplEx/complex_v4_summary.json')
if data:
    m = data.get('metrics', {})
    models['ComplEx v4'] = {
        'MRR': m.get('MRR', data.get('MRR')),
        'Hits@1': m.get('Hits@1'),
        'Hits@3': m.get('Hits@3'),
        'Hits@5': m.get('Hits@5'),
        'Hits@10': m.get('Hits@10'),
        'AMRI': m.get('AMRI'),
        'epochs': data.get('epochs', 100),
        'training_time': data.get('training_time_hours', '?'),
        'embedding_dim': data.get('embedding_dim', 200),
        'entities': data.get('entities', '?'),
    }

# ComplEx v4 from metrics JSON
c_data = load_metrics('ComplEx v4', 'results/kg_embeddings/complex_v4_metrics.json')
if c_data and 'ComplEx v4' not in models:
    models['ComplEx v4'] = extract_pykeen_metrics(c_data)
    if models['ComplEx v4']:
        models['ComplEx v4']['epochs'] = 100

# DistMult v4
d_data = load_metrics('DistMult v4', 'results/kg_embeddings_v4/DistMult/distmult_v4_summary.json')
if d_data:
    m = d_data.get('metrics', {})
    models['DistMult v4'] = {
        'MRR': m.get('MRR', d_data.get('MRR')),
        'Hits@1': m.get('Hits@1'),
        'Hits@3': m.get('Hits@3'),
        'Hits@5': m.get('Hits@5'),
        'Hits@10': m.get('Hits@10'),
        'AMRI': m.get('AMRI'),
        'epochs': d_data.get('epochs', 100),
        'training_time': d_data.get('training_time_hours', '?'),
    }

# DistMult v4.1 (check for results)
for path in ['results/kg_embeddings_v4/DistMult_v4.1/distmult_v41_summary.json',
             'results/kg_embeddings_v4/DistMult_v41/distmult_v41_summary.json',
             'results/distmult_v41_metrics.json']:
    d41_data = load_metrics('DistMult v4.1', path)
    if d41_data:
        models['DistMult v4.1'] = extract_pykeen_metrics(d41_data) or {}
        models['DistMult v4.1']['epochs'] = d41_data.get('epochs', 100)
        break

# RotatE v4
r_data = load_metrics('RotatE v4', 'results/kg_embeddings_v4/RotatE/rotatE_v4_summary.json')
if r_data:
    m = r_data.get('metrics', {})
    models['RotatE v4'] = {
        'MRR': m.get('MRR', r_data.get('MRR')),
        'Hits@1': m.get('Hits@1'),
        'Hits@3': m.get('Hits@3'),
        'Hits@5': m.get('Hits@5'),
        'Hits@10': m.get('Hits@10'),
        'AMRI': m.get('AMRI'),
        'epochs': r_data.get('epochs', 100),
    }

# RotatE v4.1 (check for results)
for path in ['results/kg_embeddings_v4/RotatE_v4.1/rotatE_v41_summary.json',
             'results/kg_embeddings_v4/RotatE_v41/rotatE_v41_summary.json']:
    r41_data = load_metrics('RotatE v4.1', path)
    if r41_data:
        models['RotatE v4.1'] = extract_pykeen_metrics(r41_data) or {}
        models['RotatE v4.1']['epochs'] = r41_data.get('epochs', 200)
        break

# DistMult v3 (baseline)
d3_data = load_metrics('DistMult v3', 'results/kg_embeddings/distmult_v3_full_metrics.json')
if d3_data:
    models['DistMult v3 (baseline)'] = extract_pykeen_metrics(d3_data) or {}
    models['DistMult v3 (baseline)']['epochs'] = 100

# Print comparison table
metrics_to_show = ['MRR', 'Hits@1', 'Hits@3', 'Hits@5', 'Hits@10', 'AMRI']
header = f"{'Model':<25}" + "".join(f"{m:>12}" for m in metrics_to_show) + f"{'Epochs':>8}"
print(header)
print("-" * len(header))

for model_name, metrics in sorted(models.items()):
    row = f"{model_name:<25}"
    for m in metrics_to_show:
        val = metrics.get(m)
        if val is not None:
            if isinstance(val, float):
                row += f"{val:>12.4f}"
            else:
                row += f"{str(val):>12}"
        else:
            row += f"{'N/A':>12}"
    row += f"{metrics.get('epochs', '?'):>8}"
    print(row)

# Save comparison
with open(BASE / 'results/analysis/v4_model_comparison_full.json', 'w') as f:
    json.dump(models, f, indent=2)

print(f"\nSaved: results/analysis/v4_model_comparison_full.json")
print(f"\nModels found: {len(models)}")

# Summary
if models:
    best_mrr = max((m.get('MRR', 0) or 0, name) for name, m in models.items())
    print(f"\nBest MRR: {best_mrr[1]} ({best_mrr[0]:.4f})")
