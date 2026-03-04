import pandas as pd
import json
import numpy as np

df = pd.read_parquet('/home/jshaik369/sexdiffkg/results/signals_v4/sex_differential_v4.parquet')
df['drug_upper'] = df['drug_name'].str.upper()

# Drug lists
antipsychotics = ['RISPERIDONE','OLANZAPINE','QUETIAPINE','ARIPIPRAZOLE','HALOPERIDOL',
    'CLOZAPINE','ZIPRASIDONE','PALIPERIDONE','LURASIDONE','BREXPIPRAZOLE',
    'CARIPRAZINE','PIMOZIDE','CHLORPROMAZINE','FLUPHENAZINE','PERPHENAZINE']

ssris = ['FLUOXETINE','SERTRALINE','PAROXETINE','CITALOPRAM','ESCITALOPRAM','FLUVOXAMINE']
snris = ['VENLAFAXINE','DULOXETINE','DESVENLAFAXINE','MILNACIPRAN','LEVOMILNACIPRAN']
tcas = ['AMITRIPTYLINE','NORTRIPTYLINE','IMIPRAMINE','DESIPRAMINE','CLOMIPRAMINE','DOXEPIN']
other_ad = ['BUPROPION','MIRTAZAPINE','TRAZODONE','VILAZODONE','VORTIOXETINE']
antidepressants = ssris + snris + tcas + other_ad

anxiolytics = ['DIAZEPAM','ALPRAZOLAM','LORAZEPAM','CLONAZEPAM','BUSPIRONE',
    'MIDAZOLAM','OXAZEPAM','TEMAZEPAM','TRIAZOLAM','CHLORDIAZEPOXIDE']

mood_stabilizers = ['LITHIUM','VALPROIC ACID','LAMOTRIGINE','CARBAMAZEPINE','TOPIRAMATE']

classes = {
    'Antipsychotics': antipsychotics,
    'SSRIs': ssris, 'SNRIs': snris, 'TCAs': tcas, 'Other_AD': other_ad,
    'All_Antidepressants': antidepressants,
    'Anxiolytics': anxiolytics,
    'Mood_Stabilizers': mood_stabilizers
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
        'total': int(len(subset)),
        'drugs_found': int(subset['drug_upper'].nunique()),
        'female_higher': int(f_count),
        'male_higher': int(m_count),
        'pct_female': float(pct_f),
        'mean_logR': float(subset['log_ratio'].mean()),
        'per_drug': {}
    }
    
    # Per-drug
    for drug in sorted(subset['drug_upper'].unique()):
        d = subset[subset['drug_upper'] == drug]
        df_count = (d['direction'] == 'female_higher').sum()
        dm_count = (d['direction'] == 'male_higher').sum()
        dpct = df_count / len(d) * 100
        print(f"    {drug}: {len(d)} signals, {df_count}F/{dm_count}M ({dpct:.1f}% F), logR={d['log_ratio'].mean():.3f}")
        results[class_name]['per_drug'][drug] = {
            'total': int(len(d)), 'f': int(df_count), 'm': int(dm_count),
            'pct_f': float(dpct), 'mean_logR': float(d['log_ratio'].mean())
        }

# Cross-class psychiatric AE analysis
print("\n\n=== PSYCHIATRIC AE CROSS-CLASS PATTERNS ===")
all_psych_drugs = antipsychotics + antidepressants + anxiolytics + mood_stabilizers
psych_signals = df[df['drug_upper'].isin(all_psych_drugs)]

# Most common AEs across psych drugs
ae_stats = psych_signals.groupby('adverse_event').agg(
    n=('direction','count'),
    n_drugs=('drug_upper','nunique'),
    f=('direction', lambda x: (x=='female_higher').sum()),
    m=('direction', lambda x: (x=='male_higher').sum()),
    mean_logR=('log_ratio','mean')
).reset_index()
ae_stats['pct_f'] = ae_stats['f'] / ae_stats['n'] * 100

# AEs appearing in 10+ psych drugs
common = ae_stats[ae_stats['n_drugs'] >= 10].sort_values('pct_f', ascending=False)
print(f"\nAEs in 10+ psychotropic drugs (most female-biased first):")
for _, r in common.head(15).iterrows():
    print(f"  {r['adverse_event']}: {int(r['n_drugs'])} drugs, {int(r['f'])}F/{int(r['m'])}M ({r['pct_f']:.0f}% F)")

print(f"\nAEs in 10+ psychotropic drugs (most male-biased):")
for _, r in common.tail(15).iterrows():
    print(f"  {r['adverse_event']}: {int(r['n_drugs'])} drugs, {int(r['f'])}F/{int(r['m'])}M ({r['pct_f']:.0f}% F)")

# Weight gain, metabolic syndrome, QTc prolongation — known sex-diff AEs for antipsychotics
print("\n=== METABOLIC & CARDIAC AEs FOR ANTIPSYCHOTICS ===")
ap_signals = df[df['drug_upper'].isin(antipsychotics)]
metabolic_aes = ['Weight increased', 'Diabetes mellitus', 'Hyperglycaemia', 'Metabolic syndrome',
                 'Blood glucose increased', 'Type 2 diabetes mellitus', 'Hyperlipidaemia',
                 'Electrocardiogram QT prolonged', 'Tardive dyskinesia', 'Neuroleptic malignant syndrome',
                 'Dystonia', 'Akathisia', 'Parkinsonism', 'Prolactin increased', 'Galactorrhoea',
                 'Amenorrhoea', 'Gynaecomastia', 'Sexual dysfunction']
for ae in metabolic_aes:
    match = ap_signals[ap_signals['adverse_event'].str.lower() == ae.lower()]
    if len(match) > 0:
        f = (match['direction']=='female_higher').sum()
        m = (match['direction']=='male_higher').sum()
        pct = f/len(match)*100
        print(f"  {ae}: {len(match)} signals, {f}F/{m}M ({pct:.0f}% F), logR={match['log_ratio'].mean():.3f}")

# Save
with open('/home/jshaik369/sexdiffkg/results/analysis/psychotropic_sex_diff.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nSaved psychotropic_sex_diff.json")
