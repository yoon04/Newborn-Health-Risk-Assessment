"""Run the regression suite with an isolated in-memory database."""
import os
from pathlib import Path
import sys
import unittest


if __name__ == '__main__':
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    # Set these before importing the Flask app; .env does not override them.
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'isolated-regression-test-key'
    suite = unittest.defaultTestLoader.discover(str(root / 'tests'))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
