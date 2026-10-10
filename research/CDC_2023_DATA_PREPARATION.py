# Independent 2023 data preparation; no training or model evaluation.
from pathlib import Path
import numpy as np
import pandas as pd
import io
import io, shutil, subprocess, tempfile, zipfile
from contextlib import contextmanager

@contextmanager
def open_zip_text(zip_path, member_name):
    executable = shutil.which('7z') or shutil.which('7zz')
    if executable is None:
        raise RuntimeError('Install p7zip-full in Colab before parsing.')
    # Stream decompressed records; stderr goes to disk to avoid a full pipe blocking.
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(
            [executable, 'x', '-so', '-bd', '-y', '-spd', str(zip_path), member_name],
            stdout=subprocess.PIPE, stderr=errors)
        try:
            with io.TextIOWrapper(process.stdout, encoding='latin-1') as text:
                yield text
            returncode = process.wait()
            if returncode != 0:
                errors.seek(0)
                details = errors.read().decode('utf-8', errors='replace')
                raise RuntimeError(f'7-Zip failed (exit {returncode}); discard this partial sample. {details[-4000:]}')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            if process.stdout is not None:
                process.stdout.close()


namespace_2023 = {'io': io, 'pd': pd, 'FEATURES': ['gestational_age_weeks', 'birth_weight_g', 'maternal_age']}
exec("COLS = ['maternal_age','plurality','gestational_age_weeks','birth_weight_g','nicu_raw','nicu_reporting']\nCOLSPECS = [(74,76),(453,454),(498,500),(503,507),(518,519),(525,526)]\n\ndef clean_chunk(raw):\n    df = raw.copy()\n    for column in ['maternal_age','plurality','gestational_age_weeks','birth_weight_g']:\n        df[column] = pd.to_numeric(df[column], errors='coerce')\n    known_label = df.nicu_raw.isin(['Y','N']) & df.nicu_reporting.eq('1')\n    in_domain = (df.plurality.eq(1) & df.maternal_age.between(13,49)\n                 & df.gestational_age_weeks.between(20,45)\n                 & df.birth_weight_g.between(227,5999))\n    result = df.loc[known_label & in_domain, FEATURES].copy()\n    result['nicu_admission'] = df.loc[result.index,'nicu_raw'].map({'N':0,'Y':1}).astype(int)\n    counts = {'raw':len(df), 'unknown_or_nonreporting_target':int((~known_label).sum()),\n              'outside_feature_or_singleton_scope':int((~in_domain).sum()), 'eligible':len(result)}\n    # Exclusion reason counts overlap; eligible is the joint intersection.\n    return result, counts\n\n# Parser/cleaning self-test using an invented fixed-width row, not patient data.\ndef fixture(nicu='Y', flag='1', gest='39', weight='3200', age='29', plurality='1'):\n    line = list(' ' * 600)\n    for (start,end),value in zip(COLSPECS,[age,plurality,gest,weight,nicu,flag]):\n        line[start:end] = list(value)\n    return ''.join(line)+'\\n'\nfixture_raw = pd.read_fwf(io.StringIO(fixture()+fixture(nicu='U')+fixture(flag='0')+fixture(age='50')),\n                          colspecs=COLSPECS, names=COLS, header=None, dtype=str)\nfixture_clean, fixture_counts = clean_chunk(fixture_raw)\nassert len(fixture_clean)==1 and fixture_clean.iloc[0]['birth_weight_g']==3200\nassert fixture_clean.iloc[0]['nicu_admission']==1\nprint('Fixed-width parser self-test: passed')\n", namespace_2023)

# The six positions were independently verified in UserGuide2023.pdf, pages 10, 31, 33–35.
zip_2023_path = Path('/content/Nat2023us.zip')
rng_2023 = np.random.default_rng(42)
sample_2023 = pd.DataFrame()
audit_2023 = {'raw': 0, 'unknown_or_nonreporting_target': 0,
              'outside_feature_or_singleton_scope': 0, 'eligible': 0}
with zipfile.ZipFile(zip_2023_path) as archive:
    members = [m for m in archive.infolist()
               if not m.is_dir() and m.file_size > 100_000_000]
    if len(members) != 1:
        raise ValueError('Expected one large U.S. natality file.')
    member = members[0]
print('2023 ZIP compression method:', member.compress_type)
print('2023 Parsing:', member.filename)
with open_zip_text(zip_2023_path, member.filename) as text:
    chunks = pd.read_fwf(text, colspecs=namespace_2023['COLSPECS'],
                         names=namespace_2023['COLS'], header=None,
                         dtype=str, chunksize=50_000)
    for number, raw_2023 in enumerate(chunks, 1):
        eligible_2023, counts = namespace_2023['clean_chunk'](raw_2023)
        for key, value in counts.items():
            audit_2023[key] += value
        eligible_2023['_sample_key'] = rng_2023.random(len(eligible_2023))
        sample_2023 = pd.concat([sample_2023, eligible_2023], ignore_index=True).nsmallest(
            120_000, '_sample_key')
        if number % 10 == 0:
            print('2023 Rows scanned:', audit_2023['raw'])
candidate_2023 = sample_2023.drop(columns='_sample_key').reset_index(drop=True)
if len(candidate_2023) != 120_000 or candidate_2023.nicu_admission.nunique() != 2:
    raise ValueError('Unexpected sample size or missing outcome class; review data.')
df_2023 = candidate_2023
print('2023 Audit (reason counts overlap):', audit_2023)
print('2023 Sample:', len(df_2023), 'NICU prevalence:', df_2023.nicu_admission.mean())
print('2023 is evaluation-only: no training or threshold selection has occurred.')
print(df_2023.describe().to_string())
