from django.contrib import admin
from .models import Hotel , HotelBooking,HotelImages,Amenities

# Register your models here.
admin.site.register(Hotel)
admin.site.register(HotelBooking)
admin.site.register(HotelImages)
admin.site.register(Amenities)