from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib import admin

class User(AbstractUser):
    c=[
        ('customer','customer'),
        ('Service provider','Service provider'),
    ]
    mble = models.CharField(max_length=10,null=True,blank=True)
    role_type=models.CharField(choices=c,default='customer',max_length=30)
    
class Service(models.Model):
    c=[
        ('Electrician','Electrician'),
        ('AC Technician','AC Technician'),
        ('Carpenter','Carpenter'),
        ('None','None'),
      ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    experience = models.PositiveIntegerField(default=0)
    field_type = models.CharField(choices=c,default='None',max_length=30)
    form = models.ImageField(upload_to='static/images/',null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} - {self.field_type}(Experience:{self.experience})'


class Approvals(models.Model):
    service = models.ForeignKey(Service,on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    
  
    
   
class Product(models.Model):
    category = [
        ('0', 'Eletric Service'),
        ('1', 'AC Service'),
        ('2','None'),
        ('3','Carpentering'),
    ]
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='static/images/',null=True, blank=True)
    category_type = models.CharField(choices=category, default="2", max_length=25)

    

    


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flat_address = models.CharField(max_length=100)





class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed','Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    products = models.ManyToManyField(Product)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
class AllocatedOrder(models.Model):
    service_provider=models.ForeignKey(Service,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    chosen_datetime=models.DateTimeField(null=True,blank=True)
    
    
    

class ReviewandRating(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    review = models.CharField(max_length=100)
    rating = models.PositiveIntegerField()
    order = models.ForeignKey(Order,on_delete=models.CASCADE,default=None,null=True)
    allo = models.ForeignKey(AllocatedOrder,on_delete=models.CASCADE,default =None,null=True)
