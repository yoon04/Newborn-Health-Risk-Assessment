"""Check notebook syntax and the verified 2024 fixed-width parser locally.

No CDC population records are downloaded, and no ML training is run here.
"""
import ast
import json
from pathlib import Path
import unittest
import pandas as pd


NOTEBOOK = Path(__file__).resolve().parents[1] / 'research' / 'CDC_NICU_Baseline_Colab.ipynb'


class CDCNotebookTests(unittest.TestCase):
    def setUp(self):
        self.notebook = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        self.code_cells = [c['source'] for c in self.notebook['cells'] if c['cell_type'] == 'code']

    def test_all_python_cells_parse(self):
        for source in self.code_cells:
            source = '\n'.join(line for line in source.splitlines() if not line.startswith(('%', '!')))
            ast.parse(source)

    def test_archive_reader_uses_7zip_stream(self):
        install = next(s for s in self.code_cells if s.startswith('%pip install'))
        self.assertIn('install -y p7zip-full', install)
        parser = next(s for s in self.code_cells if 'with zipfile.ZipFile(zip_path)' in s)
        self.assertIn('with open_zip_text(zip_path, member.filename)', parser)
        self.assertNotIn('archive.open(', parser)
        self.assertIn('member.compress_type', parser)

    def test_stream_rejects_failed_extraction_and_cleans_up_on_interruption(self):
        import io
        from unittest.mock import patch
        source = next(s for s in self.code_cells if 'def open_zip_text' in s)
        namespace = {}
        exec(source.split("globals().pop('df'")[0], namespace)

        class FakeProcess:
            def __init__(self, code):
                self.stdout = io.BytesIO(b'valid-looking partial data\n')
                self.code = code
                self.returncode = None
                self.killed = False
            def wait(self):
                self.returncode = self.code
                return self.code
            def poll(self):
                return self.returncode
            def kill(self):
                self.killed = True
        with patch('shutil.which', return_value='7z'):
            process = FakeProcess(2)
            with patch('subprocess.Popen', return_value=process):
                with self.assertRaisesRegex(RuntimeError, 'discard this partial sample'):
                    with namespace['open_zip_text']('fixture.zip', 'records.txt') as text:
                        self.assertTrue(text.read())
            process = FakeProcess(0)
            with patch('subprocess.Popen', return_value=process):
                with namespace['open_zip_text']('fixture.zip', 'records.txt') as text:
                    self.assertTrue(text.read())
                self.assertFalse(process.killed)
            process = FakeProcess(0)
            with patch('subprocess.Popen', return_value=process):
                with self.assertRaisesRegex(ValueError, 'parser interrupted'):
                    with namespace['open_zip_text']('fixture.zip', 'records.txt'):
                        raise ValueError('parser interrupted')
                self.assertTrue(process.killed)
                self.assertTrue(process.stdout.closed)

    def test_parser_excludes_unknown_nonreporting_and_grouped_ages(self):
        source = next(s for s in self.code_cells if s.startswith('COLS ='))
        import io
        namespace = {'io': io, 'pd': pd, 'FEATURES': ['gestational_age_weeks', 'birth_weight_g', 'maternal_age']}
        exec(source, namespace)
        self.assertEqual(namespace['COLSPECS'], [(74,76),(453,454),(498,500),(503,507),(518,519),(525,526)])
        fixture = namespace['fixture']
        raw = pd.read_fwf(io.StringIO(fixture(nicu='N')+fixture(nicu='U')+fixture(flag='0')+
                             fixture(age='12')+fixture(gest='99')+fixture(weight='9999')+fixture(plurality='2')),
                          colspecs=namespace['COLSPECS'], names=namespace['COLS'], header=None, dtype=str)
        clean, counts = namespace['clean_chunk'](raw)
        self.assertEqual(len(clean), 1)
        self.assertEqual(clean.iloc[0]['nicu_admission'], 0)
        self.assertEqual(counts['raw'], 7)
        self.assertEqual(counts['eligible'], 1)

    def test_non_ascii_byte_preserves_fixed_width_positions(self):
        import io
        source = next(s for s in self.code_cells if s.startswith('COLS ='))
        namespace = {'io': io, 'pd': pd, 'FEATURES': ['gestational_age_weeks', 'birth_weight_g', 'maternal_age']}
        exec(source, namespace)
        record = bytearray(namespace['fixture'](nicu='N').encode('ascii'))
        record[20] = 0xb8  # Unused field before all selected columns.
        parser = next(s for s in self.code_cells if 'with zipfile.ZipFile(zip_path)' in s)
        self.assertIn("encoding='latin-1'", parser)
        with io.TextIOWrapper(io.BytesIO(record), encoding='latin-1') as text:
            raw = pd.read_fwf(text, colspecs=namespace['COLSPECS'], names=namespace['COLS'],
                              header=None, dtype=str)
        clean, counts = namespace['clean_chunk'](raw)
        self.assertEqual(counts['eligible'], 1)
        self.assertEqual(clean.iloc[0]['maternal_age'], 29)
        self.assertEqual(clean.iloc[0]['nicu_admission'], 0)


if __name__ == '__main__':
    unittest.main()
