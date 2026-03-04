# ComplEx Embedding Novel Predictions (2026-03-04)

## Model
- ComplEx v4: MRR 0.2484, Hits@10 40.69%, AMRI 0.9902
- 200 complex dimensions (400 real values per entity)
- 113,012 entities, 5 relations
- Checkpoint: `results/kg_embeddings_v4/ComplEx/model.pt`

## Prediction Methodology
- Scored 26.6M novel Drug-AE pairs for `sex_differential_adverse_event` relation
- Filtered: Drug degree >= 5, AE degree >= 3
- Excluded existing SDAE edges (96,281) and HAE edges (614,978)
- Output: `results/analysis/embedding_predictions.json` + `embedding_predictions_top100.tsv`

## Embedding Space Properties
| Entity Type | Count | Mean Norm | Interpretation |
|-------------|-------|-----------|----------------|
| AdverseEvent | 9,949 | 14.79 | Hub entities |
| Drug | 7,208 | 9.40 | Hub entities |
| Pathway | 2,279 | 9.01 | Medium |
| Protein | 16,201 | 8.95 | Medium |
| Gene | 77,375 | 4.80 | Leaf entities |

AEs and Drugs have highest norms — they are the "hubs" of the KG embedding space.

## Top Clinically Plausible Predictions
| Drug | Adverse Event | Score | Has HAE? |
|------|---------------|-------|----------|
| Cariprazine | Sexual dysfunction | 11.00 | No |
| Tramadol HCl | Dependence | 10.14 | Yes |
| Thiotepa | Venoocclusive disease | 10.49 | Yes |
| Quetiapine fumarate | Suspected suicide | 9.93 | No |
| Lithium | Schizophrenia | 9.58 | Yes |

## Key Insight
46/100 top predictions have existing `has_adverse_event` edges (known drug-AE association) — the model predicts these known associations should ALSO be sex-differential. 54 are truly novel.

## Publication Value
- Demonstrates KG embedding utility for pharmacovigilance hypothesis generation
- Complements signal-based analysis with structure-based prediction
- Can validate top predictions against external databases (DrugBank, SIDER)

## Next Steps
1. Validate top 100 predictions against SIDER/DrugBank known sex differences
2. Cross-reference with literature case reports
3. Prioritize predictions with both high score AND clinical plausibility for prospective study
