from pyexpat.errors import messages
import random
from django.shortcuts import get_object_or_404, render
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
import math
from datetime import datetime, timedelta
import math, json
from django.core.mail import send_mail




def index(request):
    return render(request, 'index.html')


def aboutus(request):
    return render(request, 'aboutus.html')


def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        gender = request.POST.get('gender') 
        mobile = request.POST.get('phone')
        address = request.POST.get('address')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')


        if password1 != password2:
            messages.success(request, "Passwords do not match.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.success(request, "Username already exists.")
            return render(request, 'register.html')

        user = User.objects.create(
            first_name=firstname,
            last_name=lastname,
            username=username,
            email=email,
            mobile=mobile,
            address=address,
            gender=gender,
            password=make_password(password1) ,
            role='user'
        )
        user.save()
        messages.success(request, "Registration successful.")
        return redirect('login')

    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('index')


def user_home(request):
    return render(request,'user_home.html')


def admin_home(request):
    user=request.user
    return render(request, 'admin_home.html', {'user':user})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ Check if user is blocked
            if user.is_blocked == "yes":
                messages.error(request, "Your account has been blocked. Please contact support.")
                return redirect('login') 
            else:
                auth.login(request, user)
                if user.is_staff:
                    return redirect('admin_home')
                else:
                    return redirect('user_home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def user_profile(request):
    user = request.user
    vehicles = Vehicle.objects.filter(owner=user)
    return render(request, 'user_profile.html', {'user': user, 'vehicles': vehicles})


def rides(request):
    return render(request, 'rides.html')



@login_required
def edit_profile(request):
    user = request.user  

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.username = request.POST.get("username")
        user.gender = request.POST.get("gender")
        user.mobile = request.POST.get("mobile")
        user.address = request.POST.get("address")


        user.preferences = {
            "gender_pref": request.POST.get("gender_preference"),
            "smoking_pref": request.POST.get("smoking_preference"),
            "music_pref": request.POST.get("music_preference"),
            "chatting_pref": request.POST.get("chatting_preference"),
            "ac_pref": request.POST.get("ac_preference"),
            "pet_pref": request.POST.get("pet_preference"),
            "mask_pref": request.POST.get("mask_preference"),
            "luggage_pref": request.POST.get("luggage_preference"),
            "food_pref": request.POST.get("food_preference"),
            "child_pref": request.POST.get("child_preference"),
            "stopover_pref": request.POST.get("stopover_preference"),
            "speed_pref": request.POST.get("speed_preference"),
            "co_passenger_gender_pref": request.POST.get("copassenger_gender"),
            "ride_type": request.POST.get("ride_type"),
            "payment_pref": request.POST.get("payment_preference"),
            "noise_pref": request.POST.get("noise_preference"),
            "comfort_pref": request.POST.get("comfort_preference"),
            "pickup_flexibility": request.POST.get("pickup_flexibility"),
            "drop_flexibility": request.POST.get("drop_flexibility"),
            "detour_pref": request.POST.get("detour_preference"),
        }

        user.save()
        messages.success(request, "Profile & Preferences updated successfully!")
        return redirect("user_home")

    return render(request, "edit_profile.html", {"user": user, "preferences": user.preferences})




def available_rides(request):
    return render(request, 'available_rides.html')


def add_vehicle(request):
    if request.method=="POST":
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        type = request.POST.get('type')
        color = request.POST.get('color')
        license_plate = request.POST.get('vehicle_number')
        seats = request.POST.get('capacity')
        milaege = request.POST.get('mileage')
        segment = request.POST.get('vehicle_type')

        vehicle_reg = Vehicle.objects.create(
            owner_id=request.user.id,
            vehicle_number=license_plate,
            brand=brand,
            model=model,
            color=color,
            capacity=seats,
            vehicle_type=type,
            mileage = milaege,
            segment=segment,
        )
        vehicle_reg.save()
        return redirect(user_home)
    return render(request, 'add_vehicle.html')



def manage_user(request):
    return render(request, 'manage_user.html') 

def payment_management(request):
    return render(request, 'payment_management.html')

def ride_management(request):
    return render(request, 'ride_management.html')


def offer_ride(request):
    if request.method == "POST":
        locations = {
            "from": [request.POST.get("from_lat"), request.POST.get("from_lng")],
            "to": [request.POST.get("to_lat"), request.POST.get("to_lng")]
        }
        ride = Offer_ride(
            driver_id=request.user,
            locations=locations,
            route_data=request.POST.get("route_data"),
            date=request.POST.get("travel_date"),
            time=request.POST.get("travel_time"),
            available_seats=request.POST.get("ava_seats"),
            from_name=request.POST.get("from_name"),
            to_name=request.POST.get("to_name"),
            vehicle_id=request.POST.get("vehicle_id"),  
        )
        ride.save()

        return redirect("user_home")
    user = request.user
    vehicles = Vehicle.objects.filter(owner=user, vehicle_approval='approved')
    return render(request, "offer_ride.html", {"vehicles": vehicles})


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def parse_route(route_data):
    if not route_data:
        return []

    if isinstance(route_data, str): 
        try:
            route_data = json.loads(route_data)
        except Exception:
            return []

    route_points = []
    for entry in route_data:
        if isinstance(entry, dict): 
            route_points.append([float(entry.get("lat")), float(entry.get("lng"))])
        elif isinstance(entry, (list, tuple)) and len(entry) == 2:
            try:
                route_points.append([float(entry[0]), float(entry[1])])
            except Exception:
                continue
    return route_points



def is_point_near_route(point, route_data, threshold_km=0.3):
    route = parse_route(route_data)
    for lat, lng in route:
        if haversine(point[0], point[1], lat, lng) <= threshold_km:
            return True
    return False

def find_ride(request):
    if request.method == "POST":

        pickup_lat = float(request.POST.get("pickup_lat"))
        pickup_lng = float(request.POST.get("pickup_lng"))
        drop_lat = float(request.POST.get("drop_lat"))
        drop_lng = float(request.POST.get("drop_lng"))
        ride_date = request.POST.get("date")
        ride_time = request.POST.get("time")
        required_seats = int(request.POST.get("required_seats"))
        pickup_name = request.POST.get("pickup_place")
        drop_name = request.POST.get("drop_place")

        rider_preferences = request.user.preferences or {}

        ride_request = {
            "rider": request.user.id,
            "locations": {"pickup": [pickup_lat, pickup_lng], "drop": [drop_lat, drop_lng]},
            "required_seats": required_seats,
            "date": ride_date,
            "time": ride_time,
            "pickup_name": pickup_name,
            "drop_name": drop_name,
        }

        request.session["ride_request"] = ride_request

        ride_datetime = datetime.strptime(f"{ride_date} {ride_time}", "%Y-%m-%d %H:%M")
        time_lower = ride_datetime - timedelta(minutes=30)
        time_upper = ride_datetime + timedelta(minutes=30)
        fuel_price = 100  
        results = []

        for offer in Offer_ride.objects.all():
            route_points = parse_route(offer.route_data)
            if not route_points:
                continue

            pickup_ok = is_point_near_route((pickup_lat, pickup_lng), route_points)
            drop_ok = is_point_near_route((drop_lat, drop_lng), route_points)
            if not (pickup_ok and drop_ok):
                continue

            
            if offer.available_seats < required_seats:
                continue

            offer_datetime = datetime.combine(offer.date, offer.time)
            if not (time_lower <= offer_datetime <= time_upper):
                continue


            driver_preferences = offer.driver_id.preferences or {}


            match_count = 0
            total_checks = 0

            matched_preferences = {}
            unmatched_preferences = {}
            
            for key, rider_val in rider_preferences.items():
                if rider_val:
                    driver_val = driver_preferences.get(key)
                    total_checks += 1
                    if driver_val and str(rider_val).lower() == str(driver_val).lower():
                        match_count += 1
                        matched_preferences[key] = rider_val   
                    else:
                        unmatched_preferences[key] = {
                            "rider": rider_val,
                            "driver": driver_val if driver_val else "Not specified"
                            }



            total_distance = 0
            for i in range(len(route_points) - 1):
                total_distance += haversine(
                    route_points[i][0],
                    route_points[i][1],
                    route_points[i + 1][0],
                    route_points[i + 1][1],
                )

            match_percentage = (match_count / total_checks) * 100 if total_checks > 0 else 0
            if match_percentage < 65:
                continue
            
            
            if offer.vehicle.mileage > 0 and total_distance > 0: 
                total_cost = (total_distance / offer.vehicle.mileage) * fuel_price 
            else: 
                total_cost = 0 
            
            rider_distance = haversine(pickup_lat, pickup_lng, drop_lat, drop_lng) 
            if total_distance > 0: 
                seat_share = (rider_distance / total_distance) * total_cost 
                rider_share = min(round(seat_share * 1, 2), total_cost) 
            else: 
                rider_share = 0

            results.append({
                "offer_id": offer.id,
                "driver": f"{offer.driver_id.first_name} {offer.driver_id.last_name}",
                "vehicle": f"{offer.vehicle.brand} {offer.vehicle.model}",
                "ride_date": str(offer.date),
                "ride_time": str(offer.time),
                "time": str(ride_request["time"]),
                "date": str(ride_request["date"]),
                "available_seats": offer.available_seats,
                "driver_preferences": driver_preferences,
                "rider_preferences": rider_preferences,
                "match_percentage": round(match_percentage, 2),
                "route_data": route_points,
                "total_distance": round(total_distance, 2),
                "total_cost": round(total_cost, 2),
                "rider_distance": round(rider_distance, 2),
                "matched_preferences": matched_preferences,     
                "unmatched_preferences": unmatched_preferences,
                "rider_share": rider_share,
                "seats_selected": required_seats,
                "pickup_place": ride_request["pickup_name"],
                "drop_place": ride_request["drop_name"],
            })


        request.session["pickup"] = [pickup_lat, pickup_lng]
        request.session["drop"] = [drop_lat, drop_lng]
        request.session["rides"] = results

        return redirect("ride_results")

    return render(request, 'find_ride.html')



def ride_results(request):
    pickup = request.session.get("pickup", [])
    drop = request.session.get("drop", [])
    results = request.session.get("rides", [])

    return render(request, "ride_result.html", {
        "rides": results,
        "pickup": pickup,
        "drop": drop,
    })


@login_required

def accept_ride(request):
    if request.method == "POST":
        ride_id = request.POST.get("ride_id")
        offer = get_object_or_404(Offer_ride, id=ride_id)


        seats_requested = int(request.POST.get("seats_selected"))

        if offer.available_seats < seats_requested:
            messages.error(request, f"Sorry, only {offer.available_seats} seats available.")
            return redirect("find_ride")
        
        booking = BookedRide.objects.create(
            rider=request.user,
            ride=offer,
            driver=offer.driver_id,  
            vehicle=offer.vehicle,
            pickup_place=request.POST.get("pickup_place"),
            drop_place=request.POST.get("drop_place"),
            date=offer.date,
            time=offer.time,
            ride_date=offer.date,
            ride_time=offer.time,
            seats_booked=seats_requested,
            total_distance=request.POST.get("total_distance") or 0,
            rider_distance=request.POST.get("rider_distance") or 0,
            total_cost=request.POST.get("total_cost") or 0,
            rider_share=request.POST.get("rider_share") or 0,
            driver_status="Pending",
            rider_status = "Ready", 
        )

        offer.available_seats -= seats_requested
        offer.save()

        messages.success(request, "Ride booked successfully!")
        return redirect("rides")

    return redirect("find_ride")



def rides(request):
    bookings = BookedRide.objects.filter(rider=request.user, driver_status='Pending').select_related("ride", "vehicle", "driver")
    return render(request, 'rides.html',{"bookings":bookings})


@login_required
def driver_schedule(request):
    rides_data = (
        BookedRide.objects.filter(driver=request.user, driver_status="Driver Accepted")
        .select_related("rider", "driver", "vehicle", "ride")
        .order_by("-created_at")
    )

    return render(request, "driver_schedule.html", {"rides_data": rides_data})


@login_required
def rider_schedule(request):
    rides_data = (
        BookedRide.objects.filter(
            rider=request.user,
            rider_status__in=["Ready", "Riding"],   
            driver_status="Driver Accepted" 
        )
        .select_related("rider", "driver", "vehicle", "ride")
        .order_by("-created_at")
    )

    return render(request, "rider_schedule.html", {"rides_data": rides_data})



@login_required
def match(request):
    bookings = BookedRide.objects.filter(driver=request.user, driver_status='Pending').select_related("rider", "vehicle", "ride")
    return render(request, "match.html", {"bookings": bookings})


@login_required
def accept_rider(request, booking_id):

    if request.method == "POST":
        booking = get_object_or_404(BookedRide, id=booking_id)

        booking.driver_status = "Driver Accepted"
        booking.save()

        messages.success(request, f"✅ Rider {booking.rider.username} has been accepted.")
        return redirect("user_home")

    return redirect("user_home")


@login_required
def cancel_rider(request, booking_id):
    booking = get_object_or_404(BookedRide, id=booking_id, driver=request.user)
    
    cancel_reason = request.POST.get('cancel_reason', 'No reason provided.')
    
    booking.cancel_reason = cancel_reason
    booking.driver_status = "Cancelled"
    booking.rider_status = "Cancelled"
    booking.save()

 
    offer_ride = booking.ride 
    if offer_ride:
        offer_ride.available_seats += booking.seats_booked
        offer_ride.save()

    messages.success(request, "Ride cancelled successfully. Seats have been restored.")
    return redirect("user_home")



def start_ride(request, booking_id):
    booking = get_object_or_404(BookedRide, id=booking_id, rider=request.user)
    booking.rider_status = "Riding"
    booking.save()
    messages.success(request, "Ride started successfully 🚗💨")
    return redirect("rider_schedule")

def finish_ride(request, booking_id):
    booking = get_object_or_404(BookedRide, id=booking_id, rider=request.user)
    booking.rider_status = "Payment Pending"
    booking.driver_status="Payment Pending"
    booking.save()
    messages.success(request, "Ride finished successfully ✅")
    return redirect("wallet")



@login_required
def wallet_view(request):

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    due = BookedRide.objects.filter(rider=request.user, rider_status='Payment Pending')
    payments = Payment.objects.filter(user=request.user).order_by("-payment_date")[:10]
    return render(request, "wallet.html", {"wallet": wallet, "payments": payments, "due": due})

@login_required
def top_up_wallet(request):
    if request.method == "POST":
        amount_str = request.POST.get("topup_amount", "0").strip()
        try:
            amount = float(amount_str)
        except ValueError:
            messages.error(request, "Enter a valid amount.")
            return redirect("wallet")

        if amount <= 0:
            messages.error(request, "Top-up amount must be positive.")
            return redirect("wallet")

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.last_topup = amount  
        wallet.last_topup_date = datetime.now()  
        wallet.save()

        messages.success(
            request,
            f"Wallet topped up by ₹{amount:.2f}. "
            f"New balance: ₹{wallet.balance:.2f}"
        )
        return redirect("wallet")

    return redirect("wallet")

@login_required
def pay_for_ride(request, booking_id):
    booking = get_object_or_404(BookedRide, id=booking_id)

    # Ensure only the correct rider can pay
    if booking.rider != request.user:
        messages.error(request, "You are not allowed to pay for this booking.")
        return redirect("wallet")

    amount_due = float(booking.rider_share or 0.0)
    rider_wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Check wallet balance
        if rider_wallet.balance < amount_due:
            messages.error(
                request,
                f"Insufficient wallet balance. Please top-up ₹{amount_due - rider_wallet.balance:.2f}."
            )
            return redirect("wallet")

        # Deduct from rider wallet
        rider_wallet.balance -= amount_due
        rider_wallet.save()

        # Credit driver wallet
        driver = booking.driver
        driver_wallet, _ = Wallet.objects.get_or_create(user=driver)
        driver_wallet.balance += amount_due
        driver_wallet.last_topup = amount_due
        driver_wallet.last_topup_date = timezone.now()
        driver_wallet.save()

        # Record payment
        Payment.objects.create(
            ride=booking,
            user=request.user,
            amount_paid=amount_due,
            payment_mode="Wallet",
        )

        # ✅ Update statuses
        booking.driver_status = "Completed"
        booking.rider_status = "Completed"
        booking.save()

        # Success message
        messages.success(
            request,
            f"Payment of ₹{amount_due:.2f} successful. "
            f"Your new balance: ₹{rider_wallet.balance:.2f}. "
            f"Driver {driver.first_name} has been credited ₹{amount_due:.2f}."
        )

        return redirect("wallet")

    return render(
        request,
        "payment_confirm.html",
        {"booking": booking, "wallet": rider_wallet, "amount_due": amount_due},
    )



@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by("-payment_date")
    return render(request, "payment_history.html", {"payments": payments})


from django.db.models import Q

@login_required
def my_rides(request):
    # All rides where this user was involved and status is completed
    completed_rides = (
        BookedRide.objects.filter(
            Q(driver=request.user) | Q(rider=request.user),
            rider_status="Completed",
            driver_status="Completed"
        )
        .select_related("driver", "rider", "ride", "vehicle")
        .order_by("-ride_date", "-ride_time")
    )

    cancelled_rides = (
        BookedRide.objects.filter(
            Q(driver=request.user) | Q(rider=request.user),
            driver_status="Cancelled"
        )
        .select_related("driver", "rider", "ride", "vehicle")
        .order_by("-ride_date", "-ride_time")
    )

    context = {
        "completed_rides": completed_rides,
        "cancelled_rides": cancelled_rides,
    }
    return render(request, "my_rides.html", context)



@login_required
def rider_view(request):
    previous_rides = (
        BookedRide.objects.filter(
            rider=request.user,
            rider_status="Completed",
            driver_status="Completed" 
        )
        .select_related("driver", "ride", "vehicle")
        .order_by("-ride_date", "-ride_time")
    )

    paid_bookings = Payment.objects.filter(user=request.user).values_list("ride_id", flat=True)
    payment_pending = (
        BookedRide.objects.filter(
            rider=request.user,
            driver_status="Payment Pending",
            rider_status="Completed"
        )
        .exclude(id__in=paid_bookings)
        .select_related("driver", "ride", "vehicle")
        .order_by("-ride_date", "-ride_time")
    )

    cancelled_rides = (
        BookedRide.objects.filter(
            rider=request.user,
            driver_status="Cancelled"
        )
        .select_related("driver", "ride", "vehicle")
        .order_by("-ride_date", "-ride_time")
    )

    context = {
        "previous_rides": previous_rides,
        "payment_pending": payment_pending,
        "cancelled_rides": cancelled_rides,
    }
    return render(request, "rider_view.html", context)



@login_required
def submit_feedback(request, ride_id):
    ride = get_object_or_404(BookedRide, id=ride_id)

    if request.method == "POST":
        rating_value = request.POST.get("rating_value")
        comment = request.POST.get("comment", "")
        Feedback.objects.create(
            ride=ride,
            from_user=request.user,
            to_user=ride.driver,
            rating_value=rating_value,
            comment=comment
        )
        ride.rider_feedback='SUBMITTED'
        ride.save()
        
        return redirect("rider_view")

    return render(request, "feedback.html", {"ride": ride})


@login_required
def feedback_driver(request, ride_id):
    ride = get_object_or_404(BookedRide, id=ride_id)

    if request.method == "POST":
        rating_value = request.POST.get("rating_value")
        comment = request.POST.get("comment", "")
        Feedback.objects.create(
            ride=ride,
            from_user=request.user,
            to_user=ride.rider,
            rating_value=rating_value,
            comment=comment
        )
        ride.driver_feedback='SUBMITTED'
        ride.save()
        
        return redirect("my_rides")

    return render(request, "feedback_driver.html", {"ride": ride})

def manage_users(request):
    users = User.objects.filter(role='user') 
    return render(request, "manage_user.html", {"users": users})

@login_required
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = "yes"
    user.save()
    return redirect("manage_users")

@login_required
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = 'no'
    user.save()
    return redirect("manage_users")


def manage_vehicles(request):
    pending_vehicles = Vehicle.objects.filter(vehicle_approval='pending')
    approved_vehicles = Vehicle.objects.filter(vehicle_approval='approved')
    return render(request, 'manage_vehicles.html', {
        'pending_vehicles': pending_vehicles,
        'approved_vehicles': approved_vehicles
    })


@login_required
def approve_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == "POST":
        vehicle.vehicle_approval = "approved"
        vehicle.save()
        messages.success(request, f"Vehicle {vehicle.vehicle_number} approved successfully!")
        return redirect("manage_vehicles")

    return redirect("manage_vehicles")


def manage_rides(request):
    rides = BookedRide.objects.select_related("rider", "driver", "vehicle").all()
    return render(request, "manage_rides.html", {"rides": rides})

def manage_feedback(request):
    feedbacks = Feedback.objects.select_related("ride", "from_user", "to_user").order_by("-created_at")
    return render(request, "manage_feedback.html", {"feedbacks": feedbacks})


@login_required
def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)

    if request.method == "POST":
        vehicle.vehicle_number = request.POST.get("vehicle_number")
        vehicle.brand = request.POST.get("brand")
        vehicle.model = request.POST.get("model")
        vehicle.color = request.POST.get("color")
        vehicle.capacity = request.POST.get("capacity")
        vehicle.vehicle_type = request.POST.get("vehicle_type")
        vehicle.mileage = request.POST.get("mileage")
        vehicle.segment = request.POST.get("segment")
        vehicle.features = request.POST.get("features") 
        vehicle.vehicle_approval = "pending"
        vehicle.save()
        messages.success(request, "Vehicle updated successfully!")
        return redirect("user_profile")

    return render(request, "edit_vehicle.html", {"vehicle": vehicle})


@login_required
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully!")
    return redirect("user_profile")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))

            PasswordResetOTP.objects.create(user=user, otp=otp)

            send_mail(
                "Your OTP for Password Reset",
                f"Hello {user.first_name},\n\nYour OTP for password reset is: {otp}\nThis OTP is valid for 10 minutes.",
                "noreply@rideshare.com",
                [email],
                fail_silently=False,
            )

            request.session["reset_user_id"] = user.id
            messages.success(request, "OTP sent to your email.")
            return redirect("verify_otp")

        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")

    return render(request, "forgot_password.html")


def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user_id = request.session.get("reset_user_id")

        if not user_id:
            messages.error(request, "Session expired. Try again.")
            return redirect("forgot_password")

        user = get_object_or_404(User, id=user_id)
        otp_entry = PasswordResetOTP.objects.filter(user=user, otp=otp).order_by("-created_at").first()

        if otp_entry and not otp_entry.is_expired():
            request.session["otp_verified_user"] = user.id
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, "verify_otp.html")


def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        user_id = request.session.get("otp_verified_user")

        if not user_id:
            messages.error(request, "OTP verification required.")
            return redirect("forgot_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        user = get_object_or_404(User, id=user_id)
        user.set_password(new_password)
        user.save()

        messages.success(request, "Password reset successful. You can now login.")
        return redirect("login")

    return render(request, "reset_password.html")


def manage_payments(request):
    payments = Payment.objects.select_related('user', 'ride__vehicle').all().order_by('-payment_date')
    wallets = Wallet.objects.select_related('user').all().order_by('-balance')
    return render(request, 'manage_payments.html', {
        'payments': payments,
        'wallets': wallets
    })


def reject_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.status = "Rejected"
    vehicle.save()
    messages.warning(request, f"Vehicle {vehicle.vehicle_number} has been rejected.")
    return redirect('manage_vehicles')

@login_required
def chat_list(request):
    """Show all chat partners (active + past)."""
    user = request.user

    active_bookings = BookedRide.objects.filter(
        Q(rider=user) | Q(driver=user),
        driver_status="Driver Accepted"
    )

    active_partners = set()
    for b in active_bookings:
        active_partners.add(b.driver if b.rider == user else b.rider)

    all_messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).select_related("sender", "receiver")

    return render(request, "chat_list.html", {
        "active_partners": active_partners,
        "all_messages": all_messages,
    })


@login_required
def chat_room(request, user_id):
    """Display conversation with a specific user."""
    me = request.user
    other_user = get_object_or_404(User, id=user_id)

    active_booking = BookedRide.objects.filter(
        (Q(rider=me, driver=other_user) | Q(rider=other_user, driver=me)),
        driver_status="Driver Accepted"
    ).first()


    messages_qs = Message.objects.filter(
        Q(sender=me, receiver=other_user) | Q(sender=other_user, receiver=me)
    ).order_by("created_at")

    chat_locked = False
    if not active_booking:
        chat_locked = True

    return render(request, "chat_room.html", {
        "other_user": other_user,
        "messages": messages_qs,
        "active_booking": active_booking,
        "chat_locked": chat_locked,
    })


@login_required
def send_message(request, user_id):
    """Send message to another user if allowed."""
    sender = request.user
    receiver = get_object_or_404(User, id=user_id)

    active_booking = BookedRide.objects.filter(
        (Q(rider=sender, driver=receiver) | Q(rider=receiver, driver=sender)),
        driver_status="Driver Accepted"
    ).first()

    if not active_booking:
        messages.error(request, "Chat is locked. No active ride between you and this user.")
        return redirect("chat_room", user_id=receiver.id)

    if request.method == "POST":
        content = request.POST.get("message")
        if content.strip():
            Message.objects.create(
                sender=sender,
                receiver=receiver,
                booking=active_booking,
                content=content
            )
    return redirect("chat_room", user_id=receiver.id)
