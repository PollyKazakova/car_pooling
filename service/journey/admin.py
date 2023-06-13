from django.contrib import admin
from .models import Profile, Location, Offer, Demand, RequestBoard, TripDetail, Trip

# Register your models here.
admin.site.register(RequestBoard)
admin.site.register(Location)
admin.site.register(Demand)
admin.site.register(Trip)
admin.site.register(TripDetail)


@admin.register(Offer)
class Offer(admin.ModelAdmin):
    list_display = ('driver', 'origin', 'destination', 'seats_needed',
                    'departure_time', 'created_at', 'is_full', 'is_ended')
    list_filter = ('id', 'driver', 'origin', 'destination', 'departure_time', 'is_full', 'is_ended')
    ordering = ('id',)
    read_only_fields = 'driver'


@admin.register(Profile)
class Profile(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('first_name', 'last_name', 'phone_number', 'profile_pic')
    list_filter = ('id', 'first_name', 'last_name')
    ordering = ('id',)
    read_only_fields = 'user'
