from django.shortcuts import render,redirect
from django.http import HttpResponse
#create multiple from we can use
from  django.forms import inlineformset_factory
# Create your views here.
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
#filter is used for search all the items in customer
from .filters import OrderFilter
#register and login 
from django.contrib.auth.forms import UserCreationForm

#import flash masseges
from django.contrib import messages
#import authentication
from django.contrib.auth import authenticate, login, logout
#login authentication . without login an annonymus user can not see the dashboard
from django.contrib.auth.decorators import login_required

from .decorators import unauthenticated_user, allowed_users, admin_only

from django.contrib.auth.models import Group
#from django.views.decorators.csrf import csrf_exempt

@unauthenticated_user
#@csrf_exempt
def registerPage(request):
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			#here we can authenticate user and admin
			group = Group.objects.get(name='customer')
			user.groups.add(group)
			#flash messages
			messages.success(request,'Account is created for ' + username)
			return redirect('login')
	context = {'form':form}
	return render(request, 'accounts/register.html',context)

@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request,user)
			return redirect('home')
		else:
			messages.info(request, 'username and password is incorrect')
	context = {}
	return render(request, 'accounts/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
	#view all the order
	orders = request.user.customer.order_set.all()
	#view the total order 
	total_orders = orders.count()
	#view the total delivered
	delivered = orders.filter(status='Delivered').count()
	#view the total pending
	pending = orders.filter(status='Pending').count()
	context = {'orders':orders, 'total_orders':total_orders, 'delivered':delivered, 'pending':pending}
	return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
	# view the from table and data in database
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	#submission of the from table into database
	if request.method == "POST":
		form = CustomerForm(request.POST, request.FILES, instance=customer)
		if form.is_valid():
			form.save()
	context = {'form': form}
	return render(request, 'accounts/account_settings.html',context)


@login_required(login_url='login')
@admin_only
def home(request):
	#view the all orders in model
	orders = Order.objects.all()
	#view the all customer in model
	customers = Customer.objects.all()

	#view total_cutomer in models
	total_cutomers = customers.count()
	#view total_orders in models
	total_orders = orders.count()

	# total delivered
	delivered = orders.filter(status='Delivered').count()

	#total pending
	pending = orders.filter(status='Pending').count()

	context = {'orders':orders, 'customers':customers, 'total_cutomers':total_cutomers,
	'total_orders':total_orders, 'delivered':delivered, 'pending':pending }
	return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
	#view the all products in model
	products = Product.objects.all()
	return render(request, 'accounts/products.html',{'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
	#get primary key into customer
	customer = Customer.objects.get(id=pk_test)
	#get orders 
	orders = customer.order_set.all()
	orders_count = orders.count()

	# fiter is userd for search the items products status all those things
	myfilter = OrderFilter(request.GET, queryset=orders)
	orders = myfilter.qs

	context = {'customer':customer, 'orders':orders,'orders_count':orders_count, 'myfilter':myfilter}
	return render(request, 'accounts/customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
	OrderFormset =inlineformset_factory(Customer, Order, fields=('product','status'), extra=10)
	customer = Customer.objects.get(id=pk)

	formset = OrderFormset(queryset=Order.objects.none(),instance=customer)
	#form = OrderForm(initial={'customer':customer})

	if request.method == 'POST':
		#print('Printing POST:', request.POST)
		#form = OrderForm(request.POST)
		formset = OrderFormset(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')
	context = {'formset':formset}
	return render(request, 'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
	#view the value in from field
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)

	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		order.delete()
		return redirect('/')
	context = {'item': order}
	return render(request, 'accounts/delete.html',context)

