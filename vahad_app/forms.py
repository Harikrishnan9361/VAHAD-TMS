from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone', 'profile_photo']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['full_name']
        if commit:
            user.save()
            profile = user.userprofile
            profile.phone = self.cleaned_data['phone']
            if self.cleaned_data['profile_photo']:
                profile.profile_photo = self.cleaned_data['profile_photo']
            profile.save()
        return user
