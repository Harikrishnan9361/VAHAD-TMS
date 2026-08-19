"""
WSGI config for vahad_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vahad_project.settings')

BASE_DIR = Path(__file__).resolve().parent.parent

# In Vercel serverless environment, ensure SQLite db is copied to writable /tmp on cold start
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    tmp_db = Path('/tmp/db.sqlite3')
    src_db = BASE_DIR / 'db.sqlite3'
    if not tmp_db.exists() or tmp_db.stat().st_size == 0:
        if src_db.exists() and src_db.stat().st_size > 0:
            try:
                shutil.copyfile(src_db, tmp_db)
            except Exception as e:
                print(f"Warning: Could not copy db.sqlite3 to /tmp: {e}")

application = get_wsgi_application()
app = application
