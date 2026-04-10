import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.contrib.auth import get_user_model

def main():
    User = get_user_model()
    username = "admin"
    password = "Admin123456"
    email = "admin@example.com"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"superuser created: {username} / {password}")
    else:
        print("superuser exists")

if __name__ == "__main__":
    main()
