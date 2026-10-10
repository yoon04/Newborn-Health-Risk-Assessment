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

globals().pop('df', None)  # A failed rerun must not leave an old training dataframe.
rng = np.random.default_rng(SEED)
sample = pd.DataFrame()
audit = {'raw':0,'unknown_or_nonreporting_target':0,'outside_feature_or_singleton_scope':0,'eligible':0}
with zipfile.ZipFile(zip_path) as archive:
    members = [m for m in archive.infolist() if not m.is_dir() and m.file_size > 100_000_000]
    if len(members)!=1:
        raise ValueError('Expected exactly one large U.S. natality fixed-width file; inspect ZIP before proceeding.')
    member = members[0]
    print('ZIP compression method:', member.compress_type)
    print('Parsing:', member.filename, 'uncompressed bytes:', member.file_size)
    with open_zip_text(zip_path, member.filename) as text:
        for number, raw in enumerate(pd.read_fwf(text, colspecs=COLSPECS, names=COLS,
                                                 header=None, dtype=str, chunksize=50_000), 1):
            eligible, counts = clean_chunk(raw)
            for key,value in counts.items(): audit[key] += value
            eligible['_sample_key'] = rng.random(len(eligible))
            # Keeping the smallest independent random keys is a uniform sample across all eligible rows.
            sample = pd.concat([sample,eligible], ignore_index=True).nsmallest(MAX_SAMPLE,'_sample_key')
            if number%10==0: print('Rows scanned:',audit['raw'],'eligible:',audit['eligible'])
df = sample.drop(columns='_sample_key').reset_index(drop=True)
if len(df)<1000 or df.nicu_admission.nunique()!=2:
    raise ValueError('Insufficient valid two-class data: verify file, layout and exclusions.')
print('Audit (reason counts overlap):',audit)
print('Sample:',len(df),'NICU prevalence:',df.nicu_admission.mean())
df.describe()
