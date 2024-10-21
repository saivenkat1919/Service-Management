from typing import Any, Dict
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from SMS import settings
from django.contrib.auth.models import User
import datetime
from decimal import Decimal
from django.db.models import Sum
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
def home(self):
    return render(self,'html/home.html')
def register(request):
   
    if request.method == "POST":
        f = UsuserForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request,"User Created sucessfully")
        return redirect('/login')
    f = UsuserForm()
    return render(request,'html/signup.html',{'g':f})

def help(request):
    if request.method == "POST":
        sndr = request.POST['sn']
        sbj = request.POST['sb']
        m = request.POST['msg']
        t = settings.EMAIL_HOST_USER
        b = send_mail(sbj,m,t,[sndr])
        if b == 1:
            messages.success(request,"Mail has sent Successfully")
            return redirect('/helpdesk')
        else:
            messages.error(request,"Mail not sent")
            return redirect('/helpdesk')
    return render(request,'html/helpdesk.html')

def book(self):
    return render(self,'html/services.html')

def details(request):
    product = Product.objects.all()
    return render(request,'html/service_details.html',{'products':product})

def userlist(request): 
	c = User.objects.all()
	a = User.objects.all()
	n,m = {},{}
	if request.method == "POST":
		s = UslistForm(request.POST)
		if s.is_valid():
			s.save()
			messages.success(request,"User Created Successfully")
			return redirect('/usrlst')
		else:
			n[s] = s.errors
	for j in n.values():
		for v in j.items():
			m[v[0]] = v[1]
	s = UslistForm()
	return render(request,'html/userlist.html',{'w':s,'p':m.items(),'k':c})

def userupdate(request,h):
    t=User.objects.get(id=h)
    if request.method == "POST":
        z=UpForm(request.POST,instance=t)
        if z.is_valid():
            z.save()
            return redirect('/usrlst')
    z=UpForm(instance=t)
    return render(request,'html/userupd.html',{'s':z})

def serz(request,user_id):
    t=User.objects.get(id=user_id)
    if request.method == "POST":
        z=UpForm(request.POST,instance=t)
        if z.is_valid():
            z.save()
            return redirect('/usrlst')
    z=UpForm(instance=t)
    return render(request,'html/adminedit.html',{'s':z})

    
    

def userdelete(request,d):
    n=User.objects.get(id=d)
    if request.method == "POST":
        n1=UdForm(request.POST,instance=n)
        n.delete()
        return redirect('/usrlst')
    n1=UdForm(instance=n)
    return render(request,'html/userdel.html',{'a':n1})

def profile(request):
    try:
        service_provider =Service.objects.get(user=request.user)
    except Service.DoesNotExist:
        service_provider=None
        
    return render(request, "html/userprofile.html",{'service_provider': service_provider})


def changepassword(request):
    if request.method =="POST":
        n= Changepassword(user=request.user,data = request.POST)
        if n.is_valid():
            n.save()
            return redirect('/login')
    n = Changepassword(user=request)
    return render(request,'html/changepass.html',{'h':n})


def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'html/cart.html', {'cart_items': cart_items,'cart_total': cart_total})



    
def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        messages.success(request, "Already added in cart")
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(cart=cart, product=product)

    return redirect('view_cart')





def remove_from_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('view_cart')   



def checkout(request):
    cart_items = CartItem.objects.filter(cart=request.user.cart)  # Get cart items for the user
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
    
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()

            
            order = Order.objects.create(user=request.user, address=address, delivery_date=request.POST['delivery_date'])
            for item in cart_items:
                order.products.add(item.product)

            return redirect('order_confirmation',order_id=order.id)  
    else:
        address_form = AddressForm()

    context = {
        'address_form': address_form,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'html/checkout.html', context)



def order_confirmation(request,order_id):
    order = Order.objects.filter(user=request.user,id=order_id).latest('order_date')
    total_amount=Decimal(0.00)
    for item in order.products.all():
        total_amount+=item.price
    order.total_amount=total_amount
    order.save()
    cart_items =CartItem.objects.filter(cart__user=request.user,product__in = order.products.all())
    cart_items.delete()
    return render(request, 'html/order_confirmation.html', {'order': order})


def order_history(request, user_id):
    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user,status="Pending").order_by('-order_date')

    return render(request, 'html/userorders.html', {'user': user, 'orders': orders,})

def cancel_order(request, order_id):
    
    order = Order.objects.get(id=order_id)
    order.status = 'Cancelled'
    order.delete()
    messages.success(request, 'Order has been cancelled.')
    
    
    return redirect('services')

def complete_order(request,order_id):
    order = Order.objects.get(id=order_id)
    order.status='Completed'
    order.save()
    return render(request,'html/fdform.html',{'order':order})

    
def feedbackform(request, order_id):
    order = Order.objects.get(id=order_id)
    service_providers = AllocatedOrder.objects.filter(order=order)

    if request.method == "POST":
        f = rarform(request.POST)
        if f.is_valid():
            for service_provider in service_providers:
                feedback = f.save(commit=False)
                feedback.user = request.user
                feedback.order = order
                feedback.allo = service_provider
                feedback.save()
            return redirect('/thanks')

    else:
        f = rarform()

    return render(request, 'html/feedform.html', {'f': f, 'order': order, 's': service_providers})


def service_requests(request):
    service_requests=Order.objects.filter(status='Pending')
    return render(request,'html/service_requests.html',{'service_requests':service_requests})


def add_services(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Service added successfully")
        return redirect('all')
    else:
        form = ProductForm()

    return render(request, 'html/addservices.html', {'form': form})


#Dividing services based on categories
def ac_services(request):
    product =Product.objects.filter(category_type="1")
    return render(request,"html/acservices.html",{'product':product})
def eletrical_service(request):
    product = Product.objects.filter(category_type="0")
    return render(request,'html/eletricalservice.html',{'product':product})
def carpenter_service(request):
    product = Product.objects.filter(category_type="3")
    return render(request,'html/Carpenterservice.html',{'product':product})
def all_services(request):
    services =Product.objects.all()
    return render(request,'html/allservices.html',{'s':services})

def service_form(request):
    try:
        service_provider =Service.objects.get(user=request.user)
    except ObjectDoesNotExist:
        service_provider=None
    if service_provider and service_provider.is_approved:
        return render(request,'html/already_approved.html')
    if request.method == 'POST':
        g = Serviceform(request.POST, request.FILES)
        if g.is_valid():
            service=g.save(commit=False)
            service.user = request.user
            service.save()
            return redirect('submitted')
    else:
        g = Serviceform()  
    
    return render(request, 'html/servicerapproval.html', {'form': g})

def submitted(request):
    return render(request,'html/submitted.html')

            
    

def pending_submissions(request):
    pending_services = Service.objects.filter(is_approved= False)
    return render(request,'html/pending_submissions.html',{'pending_services':pending_services})

def approve_service(request, service_id):
    service = Service.objects.get(pk=service_id)

    if request.method == 'POST':
        if 'approve' in request.POST:
            service.is_approved=True
            service.save()
            Approvals.objects.create(service=service,is_approved=True)
            return redirect('pending_submissions')
        elif 'dont_approve' in request.POST:
            service.delete()
            user=service.user
            return redirect('pending_submissions')
    return render(request, 'html/approve_service.html', {'service': service})


def approved_service_providers(request,order_id):
    approved_service_providers = Service.objects.filter(is_approved=True)
    return render(request,'html/approvedusers.html',{'f':approved_service_providers})
    


    
def bookings(request, user_id):
    try:
        service_provider = Service.objects.get(user_id=user_id, is_approved=True)
    except Service.DoesNotExist:
        service_provider = None
        
    if service_provider is None or not service_provider.is_approved:
        approval_message = "You need to get approved to start taking bookings."
        bookings = []  
    else:
        approval_message = None
        bookings = AllocatedOrder.objects.filter(
            service_provider=service_provider,
            order__status__in=['Pending']
        )

    return render(request, 'html/bookings.html', {
        'bookings': bookings,
        'service_provider': service_provider,
        'approval_message': approval_message,
    })


def update_profile(request):
    if request.method == 'POST':
        form = Updateprofile(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('pf')  
    else:
        form = Updateprofile(instance=request.user)  

    return render(request, 'html/userupd.html', {'s': form})





def allocate_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    approved_service_providers = Service.objects.filter(is_approved=True)

    if request.method == "POST":
        form = AllocationForm(request.POST)
        if form.is_valid():
            selected_provider_ids = form.cleaned_data['selected_providers']
            selected_providers = []

            for selected_provider_id in selected_provider_ids:
                try:
                    selected_provider = Service.objects.get(pk=selected_provider_id.id)
                except ObjectDoesNotExist:
                    messages.error(request, 'Invalid service provider selected.')
                    return redirect('service_requests')

                
                if AllocatedOrder.objects.filter(order=order, service_provider=selected_provider).exists():
                    messages.error(request, f'{selected_provider.user.username} is already allocated to this Booking.')
                else:
                    selected_providers.append(selected_provider)

                    
                    allocated_order, created = AllocatedOrder.objects.get_or_create(
                        order=order,
                        service_provider=selected_provider,
                    )

                    if not created:
                        allocated_order.service_provider = selected_provider
                        allocated_order.save()

            if selected_providers:
                
                subject = 'Your Service Request Allocation Notification'
                message = 'Your service request has been allocated to the following service providers:'
                from_email = 'suhas8706@example.com'  
                recipient_list = [order.user.email]  

                
                mobile_numbers = [selected_provider.user.mble for selected_provider in selected_providers]
                provider_details = []
                for selected_provider in selected_providers:
                    provider_details.append(f'- {selected_provider.user.username}')

                
                context = {'user': order.user, 'provider_details': provider_details, 'order': order, 'phone_numbers': mobile_numbers}
                html_message = render_to_string('html/allocation_email.html', context)

                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

                
                messages.success(request, 'Allocated successfully!')


            allocated_providers = AllocatedOrder.objects.filter(order=order).select_related('service_provider')
            
            return render(request, 'html/allocate_order.html', {
                'order': order,
                'approved_service_providers': approved_service_providers,
                'form': form,
                'allocated_providers': allocated_providers,
            })

    else:
        form = AllocationForm()

    allocated_providers = AllocatedOrder.objects.filter(order=order).select_related('service_provider')

    return render(request, 'html/allocate_order.html', {
        'order': order,
        'approved_service_providers': approved_service_providers,
        'form': form,
        'allocated_providers': allocated_providers,
    })


def unallocate_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    allocated_orders = AllocatedOrder.objects.filter(order=order)
    if allocated_orders.exists():
        allocated_orders.delete()
        messages.success(request, 'Booking unallocated successfully!')
    else:
        messages.error(request, 'Booking is not currently allocated.')
    
    return redirect('service_requests')

    
def select_datetime(request, order_id):
    allocated_order =AllocatedOrder.objects.get(pk=order_id)

    if request.method == "POST":
        form = DateTimeSelectionForm(request.POST)
        if form.is_valid():
            chosen_datetime = form.cleaned_data['chosen_datetime']
            allocated_order.chosen_datetime = chosen_datetime  # Update AllocatedOrder with selected datetime
            allocated_order.save()

            
            subject = 'Service Appointment Scheduled'
            message = f'Your service provider will arrive on  {chosen_datetime} for your booking.'
            from_email = 'suhas8706@example.com'  # Update with your email
            recipient_list = [allocated_order.order.user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return redirect('bookings', user_id=allocated_order.service_provider.user.id)
    else:
        form = DateTimeSelectionForm()

    return render(request, 'html/select_datetime.html', {'form': form})
def feedbacks(request):
    reviews = ReviewandRating.objects.all()
    return render(request,'html/feedbacks.html',{'f':reviews})
    
    
def servi(request, user_id):
    try:
        service_provider = Service.objects.get(user_id=user_id)
    except Service.DoesNotExist:
        service_provider = None

    booking_reviews = []

    if service_provider:
        allocated_orders = AllocatedOrder.objects.filter(service_provider=service_provider)

        for allocated_order in allocated_orders:
            reviews = ReviewandRating.objects.filter(order=allocated_order.order, allo=allocated_order)
            booking_reviews.append({
                'order': allocated_order.order,
                'reviews': reviews,
            })

    return render(request, 'html/servicereviews.html', {'service_provider': service_provider, 'booking_reviews': booking_reviews})

    
    
    
    
    
    
def Thanks(request):
    return render(request,'html/thanks.html')
