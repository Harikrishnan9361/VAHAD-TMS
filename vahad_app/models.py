from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Destination(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='destinations')
    location = models.CharField(max_length=200)
    description = models.TextField()
    best_time_to_visit = models.CharField(max_length=200, blank=True)
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='destination_images/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Booking(models.Model):
    HOTEL_TYPES = [
        ('Budget', 'Budget'),
        ('Standard', 'Standard'),
        ('Luxury', 'Luxury'),
    ]
    TRANSPORT_TYPES = [
        ('Bus', 'Bus'),
        ('Train', 'Train'),
        ('Flight', 'Flight'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    travel_date = models.DateField()
    num_travelers = models.IntegerField(default=1)
    hotel_type = models.CharField(max_length=20, choices=HOTEL_TYPES)
    transport = models.CharField(max_length=20, choices=TRANSPORT_TYPES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.destination.name} ({self.booking_id})"
