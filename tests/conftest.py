"""Keep the test suite isolated from any developer PostgreSQL database."""

import os


os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-secret-key'
