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
    featured_destinations = Destination.objects.filter(is_featured=True)[:8]
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
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    
    all_destinations = Destination.objects.all().select_related('category')
    
    # 1. Filter by Category
    if category_id:
        try:
            category_id = int(category_id)
            all_destinations = all_destinations.filter(category_id=category_id)
        except (ValueError, TypeError):
            category_id = None
        
    # 2. Filter by Location
    if location:
        all_destinations = all_destinations.filter(location__icontains=location)
    
    # 3. Filter by Search Query
    if query:
        from django.db.models import Q
        keywords = query.split()
        search_filter = Q()
        for kw in keywords:
            search_filter |= (
                Q(name__icontains=kw) |
                Q(description__icontains=kw) |
                Q(location__icontains=kw) |
                Q(category__name__icontains=kw) |
                Q(best_time_to_visit__icontains=kw)
            )
        all_destinations = all_destinations.filter(search_filter).distinct()
        
    categories = Category.objects.all()

    return render(request, 'vahad_app/destinations.html', {
        'destinations': all_destinations,
        'categories': categories,
        'current_category': category_id,
        'search_query': query,
        'current_location': location
    })

def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    return render(request, 'vahad_app/destination_detail.html', {'destination': destination})

@login_required
def booking(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    if request.method == 'POST':
        booking_id = str(uuid.uuid4())[:8].upper()
        
        # New Fields
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        special_requests = request.POST.get('special_requests', '')
        
        if not customer_name or not email or not phone:
            messages.error(request, "Please fill in all required contact details.")
            return render(request, 'vahad_app/booking.html', {'destination': destination})
        
        travel_date_str = request.POST.get('travel_date')
        check_out_date_str = request.POST.get('check_out_date')
        
        if not travel_date_str:
             messages.error(request, "Please select a check-in date.")
             return render(request, 'vahad_app/booking.html', {'destination': destination})

        try:
            travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d').date()
            check_out_date = None
            if check_out_date_str:
                check_out_date = datetime.strptime(check_out_date_str, '%Y-%m-%d').date()
                if check_out_date <= travel_date:
                    messages.error(request, "Check-out date must be after check-in date.")
                    return render(request, 'vahad_app/booking.html', {'destination': destination})
        except ValueError:
            messages.error(request, "Invalid date format.")
            return render(request, 'vahad_app/booking.html', {'destination': destination})
            
        try:
            num_travelers = int(request.POST.get('num_travelers', 1))
            if num_travelers <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Invalid number of travelers.")
            return render(request, 'vahad_app/booking.html', {'destination': destination})
            
        hotel_type = request.POST.get('hotel_type')
        transport = request.POST.get('transport')
        
        # Accurate Backend Price Calculation
        multiplier = 1.0
        if hotel_type == 'Budget': multiplier = 0.8
        elif hotel_type == 'Luxury': multiplier = 2.5
        
        total_price = float(destination.price_estimate) * num_travelers * multiplier
        
        Booking.objects.create(
            user=request.user,
            destination=destination,
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            special_requests=special_requests,
            travel_date=travel_date,
            check_out_date=check_out_date,
            num_travelers=num_travelers,
            hotel_type=hotel_type,
            transport=transport,
            total_price=total_price,
            booking_id=booking_id,
            is_paid=False,
            booking_status="Pending"
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
    if not booking_obj.is_paid:
        if request.GET.get('pro') == 'true':
            from decimal import Decimal
            booking_obj.total_price += Decimal('2999.00')
        booking_obj.is_paid = True
        booking_obj.save()
    return render(request, 'vahad_app/confirmation.html', {'booking': booking_obj})

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    points = bookings.count() * 150
    return render(request, 'vahad_app/profile.html', {
        'bookings': bookings,
        'points': points
    })

def premium(request):
    return render(request, 'vahad_app/premium.html')

@login_required
def rewards(request):
    bookings_count = Booking.objects.filter(user=request.user).count()
    # Simple gamification logic
    points = bookings_count * 150
    
    # Determine level, next tier, and percentage progress
    if points <= 1000:
        level = "Explorer"
        next_tier = "1,000"
        points_pct = min(100, int((points / 1000) * 100))
    elif points <= 3000:
        level = "Voyager"
        next_tier = "3,000"
        points_pct = min(100, int(((points - 1000) / 2000) * 100))
    elif points <= 5000:
        level = "Globe Trotter"
        next_tier = "5,000"
        points_pct = min(100, int(((points - 3000) / 2000) * 100))
    else:
        level = "Vahad Legend"
        next_tier = "Max"
        points_pct = 100
    
    return render(request, 'vahad_app/rewards.html', {
        'points': points,
        'level': level,
        'bookings_count': bookings_count,
        'next_tier': next_tier,
        'points_pct': points_pct
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
    booking.booking_status = "Cancelled"
    booking.save()
    messages.success(request, "Booking cancelled successfully.")
    return redirect('profile')
