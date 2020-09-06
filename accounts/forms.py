from django.forms import ModelForm
from .models import *

#registration page import things
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
#end registration import things
class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

#registrations form created
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

# start user setttings / user profile from
class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = '__all__'
		exclude = ['user']