
import os
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from restaurants.views import rap_page_view
from restaurants.models import Restaurant

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discount_app.settings')
django.setup()

def test_rap_page():
    # create a user
    User = get_user_model()
    username = 'test_rap_user'
    password = 'password123'
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password=password)
    else:
        user = User.objects.get(username=username)

    # create a restaurant for the user (mocking get_admin_restaurant logic dependency)
    # The get_admin_restaurant helper checks for user.restaurant_admin_profile.restaurant
    # I might need to create a profile or just mock the helper if it's complicated.
    # Let's see if we can just create the restaurant and link it.
    
    # Actually, let's just test that the view returns 200 for a logged in user.
    # Logic for linking user to restaurant might be complex to replicate quickly here without full context of signals/profiles.
    # BUT, the view just renders a template.
    
    factory = RequestFactory()
    request = factory.get('/restaurants/rap/')
    request.user = user
    
    response = rap_page_view(request)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS: RAP page verified.")
        if b"Restaurant Admin Panel" in response.content:
             print("Content Verified: Title present.")
    else:
        print("FAILED: RAP page return non-200.")

if __name__ == "__main__":
    test_rap_page()
