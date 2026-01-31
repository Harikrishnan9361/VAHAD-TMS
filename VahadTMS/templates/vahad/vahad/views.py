from django.shortcuts import render

def index(request):
    return render(request, 'vahad/index.html')

def destinations(request):
    return render(request, 'vahad/destinations.html')

def booking(request):
    return render(request, 'vahad/booking.html')

def payment(request):
    return render(request, 'vahad/payment.html')

def confirmation(request):
    return render(request, 'vahad/confirmation.html')

def about(request):
    return render(request, 'vahad/about.html')

def login_view(request):
    return render(request, 'vahad/login.html')

def register_view(request):
    return render(request, 'vahad/register.html')

def my_bookings(request):
    return render(request, 'vahad/my_bookings.html')

