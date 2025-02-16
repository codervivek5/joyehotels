from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (Amenities, Hotel, HotelBooking)
from django.db.models import Q
import razorpay
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Hotel


def home(request):

    return render(request, 'home.html')

# function for booking checking


def check_booking(start_date, end_date, uid, room_count):
    qs = HotelBooking.objects.filter(
        hotel__uid=uid,
        start_date__lte=start_date,
        end_date__gte=end_date,
    )

    if len(qs) >= room_count:
        return False

    return True

# Hotels page logic


def hotels(request):
    amenities_obj = Amenities.objects.all()
    hotel_obj = Hotel.objects.all()  # Initialize hotel_obj here

    # booking checking logic
    if request.method == 'POST':
        Check_in = request.POST.get('Check_in')
        Check_out = request.POST.get('Check_out')
        # hotel = Hotel.objects.get(uid=uid)

        if not check_booking(Check_in, Check_out,  hotel_obj.room_count):
            messages.warning(request, 'Hotel is already booked in these dates ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        HotelBooking.objects.create(
            hotel= hotel_obj, 
            user=request.user,
            start_date=Check_in, 
            end_date=Check_out, 
            booking_type='Pre Paid')

        messages.success(request, 'Your booking has been saved')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # query for sorting
    sort_by = request.GET.get('sort_by')

    if sort_by:
        sort_by = request.GET.get('sort_by')
        if sort_by == 'ASC':
            hotel_obj = hotel_obj.order_by('hotel_price')
        elif sort_by == 'DSC':
            hotel_obj = hotel_obj.order_by('-hotel_price')

    # query for search
    search = request.GET.get('search')

    if search:
        hotel_obj = hotel_obj.filter(
            Q(hotel_name__icontains=search) | Q(place__icontains=search) | Q(
                amenities__amenity_name__icontains=search)
        ).distinct()

    # query for Ameenities 
    amenities =  search = request.GET.getlist('amenities')
    print(amenities)

    if len(amenities):
        hotel_obj = hotel_obj.filter(amenities__amenity_name__in = amenities).distinct()

    context = {'amenities_obj': amenities_obj,
               'hotel_obj': hotel_obj,
               'sort_by': sort_by,
               'search': search
               }
    return render(request, 'hotels.html', context)


# hotel detail view....................................


def hotel_detail(request, uid):
    try:
        hotel_obj = Hotel.objects.get(uid=uid)
    except Hotel.DoesNotExist:
        hotel_obj = None

    if hotel_obj:
        # Calculate the total amount including GST
        gst_percentage = hotel_obj.gst_percentage
        gst_amount = (gst_percentage / 100) * hotel_obj.hotel_price
        total_amount = hotel_obj.hotel_price + gst_amount

        # Calculate the price to pay (after applying the instant discount)
        discount = hotel_obj.actual_price - hotel_obj.hotel_price

        # Make sure hotel_discount is not negative
        hotel_discount = max(discount, 0)

        context = {
            'hotel_obj': hotel_obj,
            'gst_percentage': gst_percentage,
            'hotel_discount': hotel_discount,
            'gst_amount': gst_amount,
            'total_amount': total_amount,

        }

        return render(request, 'hotel_detail.html', context)
    else:
        # Handle the case where the hotel with the given UID does not exist
        messages.error(request, "Hotel not found")
        # You can replace 'some_redirect_view' with an appropriate URL
        return redirect('/home')


# login view

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print("Username:", username)
        # print("Password:", password)

        user = authenticate(request, username=username, password=password)

        # print("User:", user)
        if user is not None:
            login(request, user)
            # Check if there's a 'next' parameter in the URL
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)  # Redirect to the 'next' URL
            return redirect('home')  # Default redirect after login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'error_message': messages.get_messages(request)})

# @login_required(login_url='home')  # Redirects authenticated users to the 'home' page


def register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.warning(request, "Passwords do not match!")
            # Redirect back to the registration page with the error message
            return redirect('/register')

        user_obj = User.objects.filter(username=username)

        if user_obj.exists():
            messages.error(request, "Username already exists!")
            # Redirect back to the registration page with the error message
            return redirect('/register')

        user = User.objects.create_user(
            username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Register successfully!")
        # Redirect to the login page after successful registration
        return redirect('/login')

    # Show the registration form for non-authenticated users
    return render(request, 'register.html')

# logout view


def logout_view(request):
    logout(request)
    return redirect('home')

# Contact us view


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        subject = request.POST.get('subject')
        message = request.POST.get('Message')

    return render(request, 'contact.html')


# _________Razorpay payment integration _______________
# Create a Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def payment(request, uid):
    try:
        hotel_obj = Hotel.objects.get(uid=uid)
    except Hotel.DoesNotExist:
        hotel_obj = None

    if hotel_obj:
        # Calculate the total amount including GST
        gst_percentage = hotel_obj.gst_percentage
        gst_amount = (gst_percentage / 100) * hotel_obj.hotel_price
        total_amount = hotel_obj.hotel_price + gst_amount

        # Calculate the price to pay (after applying the instant discount)
        discount = hotel_obj.actual_price - hotel_obj.hotel_price

        # Make sure hotel_discount is not negative
        hotel_discount = max(discount, 0)

        # Create a Razorpay order
        # Amount in paise (100 paise = ₹1)
        order_amount = int(total_amount * 100)
        order_currency = 'INR'
        # Replace with a unique order identifier
        order_receipt = f'order_{str(hotel_obj.uid)[:30]}'

        try:
            order = razorpay_client.order.create({
                'amount': order_amount,
                'currency': order_currency,
                'receipt': order_receipt,
                'payment_capture': 1,  # Auto-capture payment
            })
        except Exception as e:
            # Handle any errors that occur during Razorpay order creation
            messages.error(
                request, "An error occurred while processing your payment.")
            # Redirect to hotel detail page or an error page
            return redirect(reverse('hoteldetail', args=[uid]))

        context = {
            'hotel_obj': hotel_obj,
            'gst_percentage': gst_percentage,
            'hotel_discount': hotel_discount,
            'gst_amount': gst_amount,
            'uid': uid,  # Pass the UID here
            'total_amount': total_amount,
            # Pass the Razorpay order ID to the template
            'order_id': order['id'],
        }

        return render(request, 'success_payment.html', context)
    else:
        # Handle the case where the hotel with the given UID does not exist
        messages.error(request, "Hotel not found")
        return redirect(reverse('hotels'))


# def pay(request):
#     return render(request , 'success_payment.html')

# search functionality
def search_hotels(request):
    query = request.GET.get('q')  # Get the query from the search input
    if query:
        results = Hotel.objects.filter(
            Q(hotel_name__icontains=query) | 
            Q(place__icontains=query) | 
            Q(description__icontains=query)
        )
    else:
        results = Hotel.objects.none()  # Return no results if no query
    return render(request, 'search_results.html', {'results': results, 'query': query})
