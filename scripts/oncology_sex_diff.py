import pandas as pd
import json
import numpy as np

df = pd.read_parquet('/home/jshaik369/sexdiffkg/results/signals_v4/sex_differential_v4.parquet')
df['drug_upper'] = df['drug_name'].str.upper()

# Oncology drugs by mechanism
checkpoint_inhibitors = ['NIVOLUMAB','PEMBROLIZUMAB','ATEZOLIZUMAB','DURVALUMAB',
    'IPILIMUMAB','AVELUMAB','CEMIPLIMAB','TREMELIMUMAB']
tyrosine_kinase = ['IMATINIB','DASATINIB','NILOTINIB','BOSUTINIB','PONATINIB',
    'SUNITINIB','SORAFENIB','PAZOPANIB','CABOZANTINIB','LENVATINIB',
    'REGORAFENIB','AXITINIB','VANDETANIB','ERLOTINIB','GEFITINIB',
    'OSIMERTINIB','LAPATINIB','NERATINIB','TUCATINIB','IBRUTINIB',
    'ACALABRUTINIB','ZANUBRUTINIB','PALBOCICLIB','RIBOCICLIB','ABEMACICLIB']
anti_her2 = ['TRASTUZUMAB','PERTUZUMAB','ADO-TRASTUZUMAB EMTANSINE',
    'TRASTUZUMAB DERUXTECAN','TRASTUZUMAB EMTANSINE']
hormonal = ['TAMOXIFEN','LETROZOLE','ANASTROZOLE','EXEMESTANE',
    'FULVESTRANT','ENZALUTAMIDE','ABIRATERONE','APALUTAMIDE',
    'DAROLUTAMIDE','BICALUTAMIDE','FLUTAMIDE','GOSERELIN','LEUPROLIDE']
alkylating = ['CYCLOPHOSPHAMIDE','CISPLATIN','CARBOPLATIN','OXALIPLATIN',
    'TEMOZOLOMIDE','BENDAMUSTINE','MELPHALAN','BUSULFAN','CHLORAMBUCIL']
antimetabolites = ['METHOTREXATE','FLUOROURACIL','CAPECITABINE','GEMCITABINE',
    'CYTARABINE','PEMETREXED','AZACITIDINE','DECITABINE']

classes = {
    'Checkpoint_inhibitors': checkpoint_inhibitors,
    'Tyrosine_kinase_inhibitors': tyrosine_kinase,
    'Anti_HER2': anti_her2,
    'Hormonal_therapy': hormonal,
    'Alkylating_agents': alkylating,
    'Antimetabolites': antimetabolites
}

results = {}
for class_name, drugs in classes.items():
    subset = df[df['drug_upper'].isin(drugs)]
    if len(subset) == 0:
        continue
    f_count = (subset['direction'] == 'female_higher').sum()
    m_count = (subset['direction'] == 'male_higher').sum()
    pct_f = f_count / len(subset) * 100

    print(f"\n=== {class_name}: {len(subset)} signals, {subset['drug_upper'].nunique()} drugs ===")
    print(f"  Female-higher: {f_count} ({pct_f:.1f}%), Male-higher: {m_count}, meanLogR: {subset['log_ratio'].mean():.3f}")

    results[class_name] = {
        'total': int(len(subset)), 'drugs': int(subset['drug_upper'].nunique()),
        'f': int(f_count), 'm': int(m_count), 'pct_f': float(pct_f),
        'mean_logR': float(subset['log_ratio'].mean()),
        'per_drug': {}
    }

    for drug in sorted(subset['drug_upper'].unique()):
        d = subset[subset['drug_upper'] == drug]
        df_c = (d['direction']=='female_higher').sum()
        dm_c = (d['direction']=='male_higher').sum()
        dpct = df_c/len(d)*100 if len(d) > 0 else 0
        print(f"    {drug}: {len(d)} signals, {df_c}F/{dm_c}M ({dpct:.1f}%F), logR={d['log_ratio'].mean():.3f}")
        results[class_name]['per_drug'][drug] = {
            'total': int(len(d)), 'f': int(df_c), 'm': int(dm_c),
            'pct_f': float(dpct), 'mean_logR': float(d['log_ratio'].mean())
        }

# Checkpoint inhibitor immune-related AEs (irAEs)
print("\n\n=== CHECKPOINT INHIBITOR irAEs ===")
cpi = df[df['drug_upper'].isin(checkpoint_inhibitors)]
iraes = ['Colitis', 'Pneumonitis', 'Hepatitis', 'Thyroiditis', 'Hypophysitis',
         'Nephritis', 'Myocarditis', 'Encephalitis', 'Adrenal insufficiency',
         'Type 1 diabetes mellitus', 'Vitiligo', 'Uveitis', 'Myositis',
         'Pancreatitis', 'Hypothyroidism', 'Hyperthyroidism', 'Rash',
         'Pruritus', 'Diarrhoea', 'Fatigue']

for ae in iraes:
    match = cpi[cpi['adverse_event'].str.lower() == ae.lower()]
    if len(match) > 0:
        f = (match['direction']=='female_higher').sum()
        m = (match['direction']=='male_higher').sum()
        pct = f/len(match)*100
        print(f"  {ae}: {len(match)} signals, {f}F/{m}M ({pct:.0f}%F), logR={match['log_ratio'].mean():.3f}")

# Hormonal therapy: compare male-targeting (enzalutamide etc) vs female-targeting (tamoxifen etc)
print("\n\n=== HORMONAL THERAPY: Male vs Female targeting ===")
female_hormonal = ['TAMOXIFEN','LETROZOLE','ANASTROZOLE','EXEMESTANE','FULVESTRANT']
male_hormonal = ['ENZALUTAMIDE','ABIRATERONE','APALUTAMIDE','DAROLUTAMIDE','BICALUTAMIDE','FLUTAMIDE']

for label, drugs in [('Female-targeting', female_hormonal), ('Male-targeting', male_hormonal)]:
    sub = df[df['drug_upper'].isin(drugs)]
    if len(sub) > 0:
        f_s = (sub['direction']=='female_higher').sum()
        m_s = (sub['direction']=='male_higher').sum()
        print(f"  {label}: {len(sub)} signals, {f_s}F/{m_s}M ({f_s/len(sub)*100:.1f}%F), logR={sub['log_ratio'].mean():.3f}")

# Cardiotoxicity in oncology
print("\n\n=== ONCOLOGY CARDIOTOXICITY ===")
all_onc = checkpoint_inhibitors + tyrosine_kinase + anti_her2 + hormonal + alkylating + antimetabolites
onc_signals = df[df['drug_upper'].isin(all_onc)]
cardiac_kw = ['cardiac', 'myocard', 'heart', 'arrhythm', 'qt prolong', 'tachycard', 'bradycard',
              'cardiomyopath', 'ventricular', 'atrial', 'palpitation', 'ejection fraction']
onc_cardiac = onc_signals[onc_signals['adverse_event'].str.lower().str.contains('|'.join(cardiac_kw), na=False)]
print(f"Oncology cardiac signals: {len(onc_cardiac)}")
f_oc = (onc_cardiac['direction']=='female_higher').sum()
m_oc = (onc_cardiac['direction']=='male_higher').sum()
print(f"  Female-higher: {f_oc} ({f_oc/len(onc_cardiac)*100:.1f}%)")
print(f"  Male-higher: {m_oc}")

# Per class
for cname, drugs in classes.items():
    sub = onc_cardiac[onc_cardiac['drug_upper'].isin(drugs)]
    if len(sub) >= 3:
        f_s = (sub['direction']=='female_higher').sum()
        print(f"  {cname}: {len(sub)} cardiac signals, {f_s}F/{len(sub)-f_s}M ({f_s/len(sub)*100:.0f}%F)")

with open('/home/jshaik369/sexdiffkg/results/analysis/oncology_sex_diff.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nSaved oncology_sex_diff.json")
