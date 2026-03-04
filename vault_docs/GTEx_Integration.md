# GTEx Sex-Differential Expression Integration (2026-03-04)

## Data
- 289 sex_differential_expression edges in KG
- 20 tissues -> 123 genes
- Results: results/analysis/gtex_integration.json

## Tissue Distribution
| Tissue | Edges |
|--------|-------|
| Liver | 88 (30%) |
| Whole Blood | 22 |
| Kidney - Cortex | 22 |
| Adipose - Subcutaneous | 22 |
| Brain - Cortex | 17 |
| Heart - Left Ventricle | 17 |
| Lung | 17 |
| Muscle - Skeletal | 15 |

## Gene Categories (123 genes)
1. **Y-chromosome/X-escape** (13 genes): DDX3Y, KDM5D, UTY, XIST, etc. (ubiquitous across 10 tissues)
2. **CYP enzymes** (14): CYP3A4/5/7, CYP1A1/2, CYP2E1/D6/B6, etc.
3. **UGT enzymes** (10): UGT1A1/3/4/6/9, UGT2B4/7/10/15/17
4. **Drug transporters** (14): ABCB1, ABCG2, SLC22A1, SLCO1B1, etc.
5. **Hormone receptors** (4): ESR1, ESR2, AR, PGR
6. **Steroid metabolism** (12): CYP19A1, SRD5A1/2, HSD17B1/2/3, etc.
7. **Nuclear receptors** (8): PXR, CAR, FXR, PPARA, PPARG, etc.

## CRITICAL ARCHITECTURAL INSIGHT
0 of 123 GTEx genes overlap with drug targets in the KG.
- GTEx edges: Tissue -> Gene (gene symbol IDs)
- ChEMBL targets: Drug -> Protein (UniProt/ENSP IDs)
- Gene-Protein link is IMPLICIT (same gene) but NOT explicitly modeled
- KG embeddings must learn to bridge Gene-Protein gap through shared neighborhoods

## Liver Dominance
88/289 edges (30%) involve Liver -- the primary drug metabolizing organ.
14 CYP + 10 UGT + 5 SULT + 14 transporters = 43 pharmacogenes in liver alone.
This is the mechanistic link between sex-differential gene expression and sex-differential drug metabolism.

## Publication Implications
- The Gene-Protein gap is a v4.2 KG improvement opportunity (add gene_encodes_protein edges)
- Liver CYP/UGT sex differences directly explain many drug metabolism sex differences
- Cross-referencing GTEx sex-diff CYPs with drug substrate info could predict which drugs should show sex-differential PK
