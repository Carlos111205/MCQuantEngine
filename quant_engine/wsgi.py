"""
WSGI config for quant_engine project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quant_engine.settings')

# Run migrations automatically on Vercel
if "VERCEL" in os.environ:
    import django
    django.setup()
    from django.core.management import call_command
    # Run migrations to initialize the ephemeral SQLite DB in /tmp
    try:
        call_command('migrate', interactive=False)
        print("Migrations completed successfully in /tmp/db.sqlite3")
    except Exception as e:
        print(f"Error running migrations: {e}")

application = get_wsgi_application()
app = application
