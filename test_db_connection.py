# test_db_connection.py
import os
import django
from django.conf import settings

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_a.settings')
django.setup()

# Test connection
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Successfully connected to Render PostgreSQL!")
        print(f"Database: {connection.settings_dict['NAME']}")
        print(f"Host: {connection.settings_dict['HOST']}")
except Exception as e:
    print(f"❌ Connection failed: {e}")