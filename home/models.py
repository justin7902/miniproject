from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, timezone
from django.utils import timezone


class User(AbstractUser):
    mobile = models.CharField(max_length=15,null=True, blank=True)
    address = models.CharField(max_length=200,null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    gender = models.CharField(
        null=True, max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other','Others')
        ]
    )
    role = models.CharField(max_length= 20, null=True)
    rating = models.FloatField(default=0.0)
    profile_created=models.DateField(auto_now=True)
    preferences = models.JSONField(default=dict)
    is_blocked = models.CharField(default='no')

    @property
    def imageURL(self):
        try:
            url = self.photo.url
        except:
            url = ''
        return  url


class Vehicle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    vehicle_number = models.CharField(max_length=20, unique=True)  
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30, blank=True, null=True)
    capacity = models.PositiveIntegerField(help_text="Number of passengers the vehicle can carry", default=4)
    vehicle_type = models.CharField(max_length=20)
    mileage = models.IntegerField(null=True)
    segment = models.CharField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    vehicle_approval = models.CharField(default='pending')

class Offer_ride(models.Model):
    driver_id = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True)
    locations = models.JSONField(default=dict) 
    available_seats = models.IntegerField(default=1) 
    route_data = models.JSONField(null=True, blank=True)  
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    from_name = models.CharField(null=True)
    to_name = models.CharField(null= True)
    def __str__(self):
        return f"Ride on {self.date} at {self.time}"   
    

class BookedRide(models.Model):
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booked_rides")
    ride = models.ForeignKey(Offer_ride, on_delete=models.CASCADE, related_name="accepted_rides")
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="driver_rides")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)

    pickup_place = models.CharField(max_length=50, null=True, blank=True)
    drop_place = models.CharField(max_length=50, null=True, blank=True)

    date = models.DateField()      
    time = models.TimeField()      
    ride_date = models.DateField() 
    ride_time = models.TimeField() 

    seats_booked = models.IntegerField(default=1)

    total_distance = models.FloatField(default=0)
    rider_distance = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    rider_share = models.FloatField(default=0)
    driver_status = models.CharField(null=True)
    rider_status = models.CharField(null=True)
    rider_feedback = models.CharField(null=True)
    driver_feedback = models.CharField(null=True)
    cancel_reason = models.CharField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)


    
    def __str__(self):
        return f"{self.rider.username} booked {self.ride.id} with {self.driver.username}"




class Payment(models.Model):
    ride = models.ForeignKey(BookedRide, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_paid = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user} paid {self.amount_paid}"


class Feedback(models.Model):
    ride = models.ForeignKey(BookedRide, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='feedback_given')
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='feedback_received')
    rating_value = models.FloatField(default=0.0)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} rated {self.to_user}: {self.rating_value}"


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    last_topup = models.FloatField(default=0)  
    last_topup_date = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.user.username} - Balance: ₹{self.balance}"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.email}"
    

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    booking = models.ForeignKey("BookedRide", on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"From {self.sender} to {self.receiver} about ride {self.booking.id if self.booking else 'N/A'}"