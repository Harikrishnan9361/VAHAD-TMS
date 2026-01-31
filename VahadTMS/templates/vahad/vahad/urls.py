from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    path('destinations.html', views.destinations, name='destinations'),
    path('booking.html', views.booking, name='booking'),
    path('payment.html', views.payment, name='payment'),
    path('confirmation.html', views.confirmation, name='confirmation'),
    path('about.html', views.about, name='about'),
    path('login.html', views.login_view, name='login'),
    path('register.html', views.register_view, name='register'),
    path('my_bookings.html', views.my_bookings, name='my_bookings'),
]
