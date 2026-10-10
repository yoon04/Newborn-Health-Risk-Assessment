# Run in the existing Colab session after the successful Step 3 and split.
# Requires open_zip_text from the 7-Zip recovery cell.
import numpy as np
import pandas as pd
import zipfile

extra_fields = {
    'prepregnancy_diabetes': (312, 318),
    'prepregnancy_hypertension': (314, 320),
    'previous_preterm_birth': (317, 323)
}
extra_names, extra_specs = [], []
for name, (value_position, flag_position) in extra_fields.items():
    extra_names.extend([name, name + '_reporting'])
    extra_specs.extend([(value_position, value_position + 1),
                        (flag_position, flag_position + 1)])

rng_v3 = np.random.default_rng(SEED)
sample_v3 = pd.DataFrame()
raw_count_v3 = eligible_count_v3 = 0
with zipfile.ZipFile(zip_path) as archive:
    members = [m for m in archive.infolist()
               if not m.is_dir() and m.file_size > 100_000_000]
    if len(members) != 1:
        raise ValueError('Expected exactly one large natality file.')
    member = members[0]

with open_zip_text(zip_path, member.filename) as text:
    chunks = pd.read_fwf(
        text, colspecs=COLSPECS + extra_specs,
        names=COLS + extra_names, header=None,
        dtype=str, chunksize=50_000)
    for number, raw in enumerate(chunks, 1):
        eligible, counts = clean_chunk(raw[COLS])
        raw_count_v3 += counts['raw']
        eligible_count_v3 += counts['eligible']
        for name in extra_fields:
            values = raw.loc[eligible.index, name].str.strip()
            flags = raw.loc[eligible.index, name + '_reporting'].str.strip()
            eligible[name] = values.where(flags.eq('1')).map({'N': 0.0, 'Y': 1.0})
        eligible['_sample_key'] = rng_v3.random(len(eligible))
        sample_v3 = pd.concat([sample_v3, eligible], ignore_index=True).nsmallest(
            MAX_SAMPLE, '_sample_key')
        if number % 10 == 0:
            print('Rows scanned:', raw_count_v3)

candidate_v3 = sample_v3.drop(columns='_sample_key').reset_index(drop=True)
base_columns = list(FEATURES) + ['nicu_admission']
pd.testing.assert_frame_equal(candidate_v3[base_columns], df[base_columns])
assert eligible_count_v3 == audit['eligible']
# No extra exclusions: unknown or non-reporting predictors stay missing.
df_v3 = candidate_v3
print('Verified: original sampled records and order reproduced.')
print('Original df, split, and fitted models remain unchanged.')
feature_audit = pd.DataFrame({
    name: {
        'known_no': int(df_v3[name].eq(0).sum()),
        'known_yes': int(df_v3[name].eq(1).sum()),
        'missing_or_nonreporting': int(df_v3[name].isna().sum()),
        'missing_percent': 100 * df_v3[name].isna().mean()
    }
    for name in extra_fields
}).T
print(feature_audit.round(3).to_string())
