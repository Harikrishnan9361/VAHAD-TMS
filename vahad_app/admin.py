from django.contrib import admin
from .models import UserProfile, Category, Destination, Booking

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'location', 'price_estimate', 'is_featured']
    list_filter = ['category', 'is_featured']
    search_fields = ['name', 'location']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'customer_name', 'destination', 'travel_date', 'total_price', 'payment_method', 'booking_status', 'created_at']
    list_filter = ['booking_status', 'payment_method', 'travel_date', 'is_paid', 'hotel_type', 'transport']
    search_fields = ['customer_name', 'email', 'booking_id', 'phone']

