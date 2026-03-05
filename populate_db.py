import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vahad_project.settings')
django.setup()

from django.contrib.auth.models import User
from vahad_app.models import Category, Destination
from django.core.files.base import ContentFile

def populate():
    print("Populating database with sample data...")

    # Create Admin User if doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@vahad.com', 'admin123')
        print("Admin user created (admin/admin123)")

    # 10 Categories
    categories_data = [
        ("Beaches", "Golden sands and blue waters."),
        ("Hill Stations", "Cool climates and misty peaks."),
        ("Historical Places", "Step back into India's rich past."),
        ("Temples", "Spiritual journeys and architecture."),
        ("Waterfalls", "Nature's majestic cascades."),
        ("Wildlife", "Encounter exotic animals in the wild."),
        ("Cities", "Vibrant culture and modern life."),
        ("Adventure", "Thrills and excitement await."),
        ("Cultural Heritage", "Rich traditions and arts."),
        ("Luxury Resorts", "Relax in ultimate comfort.")
    ]

    category_objs = {}
    for name, desc in categories_data:
        cat, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
        category_objs[name] = cat
        print(f"Category '{name}' {'created' if created else 'already exists'}")

    # Featured Destinations (Tamil Nadu focus + India)
    destinations_data = [
        ("Yercaud", "Hill Stations", "Salem, Tamil Nadu", "The Jewel of the South, famous for its coffee plantations and the Yercaud Lake.", 2500, True),
        ("Bhavani", "Historical Places", "Erode, Tamil Nadu", "Known for the Sangameswarar Temple and the confluence of rivers.", 1500, True),
        ("Marina Beach", "Beaches", "Chennai, Tamil Nadu", "The longest natural urban beach in the country.", 500, True),
        ("Ooty", "Hill Stations", "Nilgiris, Tamil Nadu", "The Queen of Hill Stations, known for the Nilgiri Mountain Railway.", 3500, True),
        ("Madurai", "Temples", "Madurai, Tamil Nadu", "The Temple City, home to the magnificent Meenakshi Amman Temple.", 2000, True),
        ("Marina Beach", "Beaches", "Chennai, Tamil Nadu", "The longest natural urban beach in the country.", 500, True),
        ("Coimbatore", "Cities", "Coimbatore, Tamil Nadu", "The Manchester of South India.", 1800, False),
        ("Bengaluru", "Cities", "Karnataka", "The Silicon Valley of India.", 3000, False),
        ("Hyderabad", "Cities", "Telangana", "The City of Pearls.", 2800, False),
        ("Hampi", "Historical Places", "Karnataka", "The UNESCO World Heritage site known for its ancient ruins.", 3000, False),
    ]

    for name, cat_name, loc, desc, price, featured in destinations_data:
        cat = category_objs[cat_name]
        dest, created = Destination.objects.get_or_create(
            name=name,
            defaults={
                'category': cat,
                'location': loc,
                'description': desc,
                'price_estimate': price,
                'is_featured': featured,
                'best_time_to_visit': 'October to March'
            }
        )
        print(f"Destination '{name}' {'created' if created else 'already exists'}")

    print("Populate complete!")

if __name__ == "__main__":
    populate()
