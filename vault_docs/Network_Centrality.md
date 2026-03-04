# SexDiffKG Network Centrality Analysis (2026-03-04)

## Data
- 109,867 nodes / 1,822,851 edges
- Results: results/analysis/network_centrality.json

## Graph Properties
- Largest connected component: 68.5% of nodes (from BFS sample)
- Scale-free degree distribution (power law)
- Drug mean degree 247, median 34 (heavy-tailed)

## Hub Nodes (Top 10 by Degree)
1. ADALIMUMAB (Drug): 8,203
2. METHOTREXATE (Drug): 6,611
3. PREDNISONE (Drug): 6,339
4. ETANERCEPT (Drug): 5,281
5. RITUXIMAB (Drug): 5,176
6. INFLIXIMAB (Drug): 4,543
7. Drug ineffective (AE): 4,529
8. TACROLIMUS (Drug): 4,529
9. PREDNISOLONE (Drug): 4,299
10. DEXAMETHASONE (Drug): 4,257

## Mean Degree by Type
| Type | Mean | Median | Max |
|------|------|--------|-----|
| Drug | 247.2 | 34 | 8,203 |
| Pathway | 162.6 | 82 | 3,680 |
| AE | 97.0 | 12 | 4,529 |
| Protein | 58.5 | 26 | 1,532 |
| Gene | 4.9 | 2 | 1,245 |

## Top Hub Protein: TP53/p53 (degree 1,532)

## Sex-Diff AE Connectivity (Top 5)
1. PREDNISONE: 926 sex-diff edges
2. METHOTREXATE: 892
3. ADALIMUMAB: 807
4. RITUXIMAB: 755
5. INFLIXIMAB: 623

## Key Insight
Immunosuppressants/anti-inflammatories dominate ALL centrality metrics.
The KG is hub-and-spoke with drugs as hubs connecting through AEs.
Gene nodes form the long tail (77k nodes, mean degree 4.9).
