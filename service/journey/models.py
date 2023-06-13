from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# class UserProfile(models.Model):
#     # id
#     user_id = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar = models.CharField(max_length=200)
#     about = models.CharField(max_length=500)


# class Trip(models.Model):
#     trip_name = models.CharField(max_length=200)
#     start_point = models.CharField(max_length=200)
#     end_point = models.CharField(max_length=200)
#     departure_date = models.DateTimeField()
#     transport_type = models.CharField(max_length=200)
#     available_seats = models.IntegerField()
#
#     users = models.ManyToManyField(User, related_name='trips_users', blank=True)


class Profile(models.Model):
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, default='sample.jpg', null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f'{self.first_name}'


class Location(models.Model):
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)


class Offer(models.Model):
    driver = models.ForeignKey(Profile, related_name='driver_profile', on_delete=models.CASCADE)
    origin = models.ForeignKey(Location, related_name='offer_origin', on_delete=models.CASCADE)
    destination = models.ForeignKey(Location, related_name='offer_destination', on_delete=models.CASCADE)
    seats_needed = models.IntegerField()
    departure_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_full = models.BooleanField(default=False)
    is_ended = models.BooleanField(default=False)

    def __str__(self):
        return f'Offer by {self.driver} to {self.destination}'


class Demand(models.Model):
    passenger = models.ForeignKey(Profile, related_name='trip_passenger', on_delete=models.CASCADE)
    origin = models.ForeignKey(Location, related_name='demand_origin', on_delete=models.CASCADE)
    destination = models.ForeignKey(Location, related_name='demand_destination', on_delete=models.CASCADE)
    available_seats = models.IntegerField()
    departure_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    distance = models.CharField(max_length=255)
    complete = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)

    def __str__(self):
        return f'Demand by {self.passenger} for {self.destination}'


class RequestBoard(models.Model):
    PENDING = 'PE'
    ACCEPTED = 'AC'
    DENIED = 'DE'
    REQUEST_STATUS = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (DENIED, "Denied"),
    ]
    offer = models.ForeignKey(Offer, related_name='requests', on_delete=models.CASCADE)
    status = models.CharField(choices=REQUEST_STATUS, max_length=2)
    demand = models.ForeignKey(Demand, related_name='my_request', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.demand.passenger.user.username} request to {self.offer.driver.user.username}'


class TripDetail(models.Model):
    request = models.ForeignKey(RequestBoard, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    demand = models.ForeignKey(Demand, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.offer.driver.user.username}'s trip to {self.offer.destination.name}"


class Trip(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    start_time = models.TimeField(null=True)
    stop_time = models.TimeField(null=True)

    def __str__(self):
        return f'Trip to {self.offer.destination}'
