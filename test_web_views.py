#!/usr/bin/env python
"""
Test the web views to ensure they work without FieldError
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_web_views():
    """Test web views"""
    client = Client()
    
    print("=" * 70)
    print("Testing Web Views")
    print("=" * 70)
    
    # Create a test user
    user = User.objects.filter(username='testuser').first()
    if not user:
        user = User.objects.create_user(username='testuser', password='testpass123')
        print("[created] Test user created")
    
    # Login
    client.login(username='testuser', password='testpass123')
    print("[login] Logged in as testuser")
    
    # Test dashboard
    print("\n[TEST 1] GET /dashboard/")
    response = client.get('/dashboard/')
    if response.status_code == 200:
        print("[OK] Dashboard loaded successfully")
    else:
        print(f"[FAIL] Status {response.status_code}")
        print(response.content.decode()[:300])
        return False
    
    # Test simulaciones section
    print("\n[TEST 2] GET /simulaciones/")
    response = client.get('/simulaciones/')
    if response.status_code == 200:
        print("[OK] Simulaciones section loaded successfully")
    else:
        print(f"[FAIL] Status {response.status_code}")
        print(response.content.decode()[:300])
        return False
    
    # Test articulos list
    print("\n[TEST 3] GET /articulos/")
    response = client.get('/articulos/')
    if response.status_code == 200:
        print("[OK] Articulos list loaded successfully")
    else:
        print(f"[FAIL] Status {response.status_code}")
        return False
    
    print("\n" + "=" * 70)
    print("All web view tests passed!")
    print("=" * 70)
    return True

if __name__ == '__main__':
    success = test_web_views()
    sys.exit(0 if success else 1)
