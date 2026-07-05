"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

admin_username = os.environ.get("CREATE_ADMIN_USERNAME")
admin_email = os.environ.get("CREATE_ADMIN_EMAIL")
admin_password = os.environ.get("CREATE_ADMIN_PASSWORD")

if admin_username and admin_email and admin_password:
    try:
        User = get_user_model()
        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            print(f"--- Superuser '{admin_username}' created successfully from Env Vars! ---")
        else:
            print(f"--- Superuser '{admin_username}' already exists. ---")
    except Exception as e:
        print(f"--- Error creating superuser: {e} ---")