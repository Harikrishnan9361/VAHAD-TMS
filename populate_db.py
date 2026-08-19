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
        ("Beaches", "Golden sands and blue waters.", "category_images/beaches.jpg"),
        ("Hill Stations", "Cool climates and misty peaks.", "category_images/hill_stations.jpg"),
        ("Historical Places", "Step back into India's rich past.", "category_images/historical.jpg"),
        ("Temples", "Spiritual journeys and architecture.", "category_images/temples.jpg"),
        ("Waterfalls", "Nature's majestic cascades.", "category_images/waterfalls.png"),
        ("Wildlife", "Encounter exotic animals in the wild.", "category_images/wildlife.png"),
        ("Cities", "Vibrant culture and modern life.", "category_images/cities.jpg"),
        ("Adventure", "Thrills and excitement await.", "category_images/adventure.png"),
        ("Cultural Heritage", "Rich traditions and arts.", "category_images/culture.png"),
        ("Luxury Resorts", "Relax in ultimate comfort.", "category_images/luxury.png")
    ]

    category_objs = {}
    for name, desc, img_path in categories_data:
        cat, created = Category.objects.update_or_create(
            name=name,
            defaults={
                'description': desc,
                'image': img_path
            }
        )
        category_objs[name] = cat
        print(f"Category '{name}' {'created' if created else 'updated'}")

    # Featured Destinations (Tamil Nadu focus + India)
    destinations_data = [
        ("Yercaud", "Hill Stations", "Salem, Tamil Nadu", "The Jewel of the South, famous for its coffee plantations and the Yercaud Lake.", 2500, True, 'destination_images/yerkard.jpg', 'October to March'),
        ("Bhavani", "Historical Places", "Erode, Tamil Nadu", "Known for the Sangameswarar Temple and the confluence of rivers.", 1500, True, 'destination_images/bhavani.jpg', 'October to March'),
        ("Marina Beach", "Beaches", "Chennai, Tamil Nadu", "The longest natural urban beach in the country.", 500, True, 'destination_images/marina_beach.jpg', 'November to February'),
        ("Ooty", "Hill Stations", "Nilgiris, Tamil Nadu", "The Queen of Hill Stations, known for the Nilgiri Mountain Railway.", 3500, True, 'destination_images/ooty.jpg', 'October to June'),
        ("Madurai", "Temples", "Madurai, Tamil Nadu", "The Temple City, home to the magnificent Meenakshi Amman Temple.", 2000, True, 'destination_images/madurai.jpg', 'October to March'),
        ("Coimbatore", "Cities", "Coimbatore, Tamil Nadu", "The Manchester of South India.", 1800, False, 'destination_images/coimbator.jpg', 'September to March'),
        ("Bengaluru", "Cities", "Karnataka", "The Silicon Valley of India.", 3000, False, 'destination_images/bangalote.jpg', 'October to March'),
        ("Hyderabad", "Cities", "Telangana", "The City of Pearls.", 2800, False, 'destination_images/hydhrapath.jpg', 'October to March'),
        ("Hampi", "Historical Places", "Karnataka", "The UNESCO World Heritage site known for its ancient ruins.", 3000, False, 'destination_images/hampi.jpg', 'October to March'),
        ("Munnar", "Hill Stations", "Idukki, Kerala", "Breathtaking green tea plantations and misty hills.", 4000, True, 'destination_images/munnar.png', 'September to May'),
        ("Goa", "Beaches", "Goa", "Scenic sun-kissed beaches and vibrant nightlife.", 4500, True, 'destination_images/goa.png', 'November to February'),
        ("Taj Mahal", "Historical Places", "Agra, Uttar Pradesh", "The ultimate symbol of love and a UNESCO World Heritage site.", 5000, True, 'destination_images/taj_mahal.png', 'October to March'),
        ("Manali", "Hill Stations", "Himachal Pradesh", "Snow-capped peaks, skiing, and adventure trails.", 5500, True, 'destination_images/manali.png', 'October to June'),
    ]

    for name, cat_name, loc, desc, price, featured, img_path, best_time in destinations_data:
        cat = category_objs[cat_name]
        dest, created = Destination.objects.update_or_create(
            name=name,
            defaults={
                'category': cat,
                'location': loc,
                'description': desc,
                'price_estimate': price,
                'is_featured': featured,
                'image': img_path,
                'best_time_to_visit': best_time
            }
        )
        print(f"Destination '{name}' {'created' if created else 'updated'}")

    print("Populate complete!")

if __name__ == "__main__":
    populate()
