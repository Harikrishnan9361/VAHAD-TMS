from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Category, Destination, Booking, UserProfile
from .forms import UserRegisterForm
from django.contrib import messages
import uuid
from datetime import datetime

def home(request):
    categories = Category.objects.all()[:10]
    featured_destinations = Destination.objects.filter(is_featured=True)[:5]
    return render(request, 'vahad_app/home.html', {
        'categories': categories,
        'featured_destinations': featured_destinations
    })

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'vahad_app/register.html', {'form': form})

def about(request):
    return render(request, 'vahad_app/about.html')

def destinations(request):
    category_id = request.GET.get('category')
    query = request.GET.get('q')
    
    all_destinations = Destination.objects.all()
    
    if category_id:
        all_destinations = all_destinations.filter(category_id=category_id)
    
    if query:
        from django.db.models import Q
        all_destinations = all_destinations.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query)
        )
        
    categories = Category.objects.all()
    return render(request, 'vahad_app/destinations.html', {
        'destinations': all_destinations,
        'categories': categories,
        'current_category': int(category_id) if category_id else None,
        'search_query': query
    })

def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    return render(request, 'vahad_app/destination_detail.html', {'destination': destination})

@login_required
def booking(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    if request.method == 'POST':
        booking_id = str(uuid.uuid4())[:8].upper()
        
        travel_date_str = request.POST.get('travel_date')
        if not travel_date_str:
             messages.error(request, "Please select a travel date.")
             return render(request, 'vahad_app/booking.html', {'destination': destination})

        try:
            travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return render(request, 'vahad_app/booking.html', {'destination': destination})
            
        num_travelers = int(request.POST.get('num_travelers', 1))
        hotel_type = request.POST.get('hotel_type')
        transport = request.POST.get('transport')
        
        # Simple price calculation logic to match frontend
        multiplier = 1.0
        if hotel_type == 'Budget': multiplier = 0.8
        elif hotel_type == 'Luxury': multiplier = 2.5
        
        total_price = float(destination.price_estimate) * num_travelers * multiplier
        
        Booking.objects.create(
            user=request.user,
            destination=destination,
            travel_date=travel_date,
            num_travelers=num_travelers,
            hotel_type=hotel_type,
            transport=transport,
            total_price=total_price,
            booking_id=booking_id,
            is_paid=False
        )
        return redirect('payment', booking_id=booking_id)
    return render(request, 'vahad_app/booking.html', {'destination': destination})

@login_required
def payment(request, booking_id):
    booking_obj = get_object_or_404(Booking, booking_id=booking_id)
    return render(request, 'vahad_app/payment.html', {
        'booking': booking_obj
    })

@login_required
def confirmation(request, booking_id):
    booking_obj = get_object_or_404(Booking, booking_id=booking_id)
    # Mark as paid for simulation
    booking_obj.is_paid = True
    booking_obj.save()
    return render(request, 'vahad_app/confirmation.html', {'booking': booking_obj})

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'vahad_app/profile.html', {
        'bookings': bookings
    })

def premium(request):
    return render(request, 'vahad_app/premium.html')
def checkout(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    if request.method == "POST":
        method = request.POST.get("payment_method")
        is_pro = request.POST.get("is_pro") == "true"

        if is_pro:
            booking.total_price += 2999

        booking.payment_method = method
        booking.save()

        return redirect('confirmation', booking_id=booking.booking_id)

@login_required
def rewards(request):
    bookings_count = Booking.objects.filter(user=request.user).count()
    # Simple gamification logic
    points = bookings_count * 150
    level = "Explorer"
    if points > 1000: level = "Voyager"
    if points > 3000: level = "Globe Trotter"
    if points > 5000: level = "Vahad Legend"
    
    return render(request, 'vahad_app/rewards.html', {
        'points': points,
        'level': level,
        'bookings_count': bookings_count
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Phone update via UserProfile
        phone = request.POST.get('phone')
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if phone:
            profile.phone = phone
            
        # Profile Photo Update
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
            
        profile.save()
            
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    return redirect('profile')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    booking.delete()
    messages.success(request, "Booking cancelled successfully.")
    return redirect('profile')
