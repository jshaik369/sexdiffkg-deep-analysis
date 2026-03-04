#!/usr/bin/env python3
"""RotatE v4.1 CPU — FIXED: single train() call to avoid epoch counter bug"""
import json, time, torch, pandas as pd
from pathlib import Path
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator
from pykeen.losses import MarginRankingLoss

BASE = Path('/home/jshaik369/sexdiffkg')
KG = BASE / 'data' / 'kg_v4'
OUT = BASE / 'results' / 'kg_embeddings'

print('=' * 60)
print('RotatE v4.1 CPU FIXED (single train() call, 200 epochs)')
print('Incident #10 fix: no block training')
print('=' * 60)

df = pd.read_csv(KG / 'triples.tsv', sep='\t', header=None, names=['h', 'r', 't'])
df = df.dropna()
print(f'Triples: {len(df):,}')

tf = TriplesFactory.from_labeled_triples(df[['h', 'r', 't']].values)
train, test = tf.split([0.9, 0.1], random_state=42)
print(f'Train: {train.num_triples:,}  Test: {test.num_triples:,}')
print(f'Entities: {tf.num_entities:,}  Relations: {tf.num_relations}')

device = torch.device('cpu')
print(f'Device: {device} (forced — GPU NVRTC incompatible)')
print(f'CPU threads: {torch.get_num_threads()}')

model = RotatE(
    triples_factory=train,
    embedding_dim=200,
    loss=MarginRankingLoss(margin=9.0),
).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.00005)
training_loop = SLCWATrainingLoop(model=model, triples_factory=train, optimizer=optimizer)

print(f'\nTraining 200 epochs (SINGLE call)...')
t0 = time.time()

# SINGLE train() call — avoids PyKEEN epoch counter bug (Incident #10)
losses = training_loop.train(
    triples_factory=train,
    num_epochs=200,
    batch_size=512,
    use_tqdm=True,
    use_tqdm_batch=False,
)

train_time = time.time() - t0
print(f'\nTraining complete: {train_time/60:.1f} min ({train_time/3600:.1f} hours)')
print(f'Final loss: {losses[-1]:.4f}')

# Save model FIRST (Incident #1 prevention)
model_dir = OUT / 'RotatE_v41_cpu'
model_dir.mkdir(parents=True, exist_ok=True)
torch.save(model.state_dict(), model_dir / 'model.pth')
print(f'Model saved to {model_dir}')

# Evaluate with correct API (Incident #12 fix)
print('\nEvaluating...')
evaluator = RankBasedEvaluator()
results = evaluator.evaluate(
    model=model,
    mapped_triples=test.mapped_triples,
    additional_filter_triples=[train.mapped_triples],
    batch_size=256,
)

mrr = float(results.get_metric('both.realistic.inverse_harmonic_mean_rank'))
h1 = float(results.get_metric('both.realistic.hits_at_1'))
h10 = float(results.get_metric('both.realistic.hits_at_10'))
amr = float(results.get_metric('both.realistic.arithmetic_mean_rank'))
amri = 1.0 - (2.0 * amr) / (tf.num_entities + 1)

print(f'\nRotatE v4.1 CPU Results:')
print(f'MRR:    {mrr:.5f}')
print(f'Hits@1: {h1:.5f}')
print(f'Hits@10:{h10:.5f}')
print(f'AMRI:   {amri:.4f}')

metrics = {
    'model': 'RotatE_v4.1_CPU', 'kg_version': 'v4.1',
    'entities': tf.num_entities, 'relations': tf.num_relations,
    'dim': 200, 'epochs': 200, 'batch_size': 512, 'lr': 0.00005,
    'loss': 'MarginRankingLoss(margin=9.0)',
    'mrr': mrr, 'hits_at_1': h1, 'hits_at_10': h10,
    'amr': amr, 'amri': amri,
    'training_time_hours': round(train_time / 3600, 1),
    'final_loss': losses[-1],
    'device': 'cpu',
    'note': 'Fixed single train() call. GPU NVRTC SM 12.1 incompatible.'
}
with open(OUT / 'rotatE_v41_cpu_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print(f'Metrics saved')
print('DONE')
