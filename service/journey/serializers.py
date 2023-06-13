from datetime import datetime
from rest_framework import serializers, status
from .models import Profile, Location, Offer, Demand, RequestBoard, TripDetail, Trip
from rest_framework.exceptions import ValidationError, MethodNotAllowed, NotAcceptable
from django.db.models import Q


# class TripSerializer(serializers.ModelSerializer):
#     users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#
#     class Meta:
#         model = Trip
#         fields = '__all__'
#
#
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        raise ValidationError(detail='This Profile cannot be created.')

    def update(self, instance, validated_data, many=True):
        if self.context['request'].user != instance.user:
            raise ValidationError(detail='You must be a user for editing this profile.')
        phone_number = validated_data.get('phone_number')
        last_name = validated_data.get('last_name')
        if phone_number is None:
            raise ValidationError(
                detail='The phone number must be provided.')
        else:
            instance.phone_number = phone_number
            instance.last_name = last_name
            instance.save()
        return instance

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = 'user'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class OfferSerializer(serializers.ModelSerializer):
    origin = serializers.JSONField(required=True)
    destination = serializers.JSONField(required=True)
    seats_needed = serializers.IntegerField()
    departure_time = serializers.TimeField()
    is_full = serializers.BooleanField()
    is_ended = serializers.BooleanField()

    driver = ProfileSerializer(read_only=True)
    origin = LocationSerializer()
    destination = LocationSerializer()

    def create(self, validated_data, many=True):
        now = datetime.datetime.now()
        departure_time = validated_data.get('departure_time')
        is_full = validated_data.get('is_full')
        is_ended = validated_data.get('is_ended')
        request = self.context['request']
        try:
            validated_data['driver'] = request.user.profile
        except Exception as e:
            raise ValidationError(detail='This user has no profile')

        for item in ['origin', 'destination']:
            _location = Location.objects.create(**validated_data.get(item))
            validated_data[item] = _location
        return Offer.objects.create(**validated_data)

    def update(self, instance, validated_data, many=True):
        instance.is_full = validated_data.get('is_full', instance.is_full)
        instance.is_ended = validated_data.get('is_ended', instance.is_ended)

        instance.save()
        return instance

    class Meta:
        model = Offer
        fields = '__all__'


class DemandSerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(required=True)
    origin = serializers.JSONField(required=True)
    destination = serializers.JSONField(required=True)
    distance = serializers.CharField(required=True)

    passenger = ProfileSerializer(read_only=True)
    origin = LocationSerializer()
    destination = LocationSerializer()

    def create(self, validated_data):
        request = self.context['request']
        if request and hasattr(request, 'user'):
            try:
                validated_data['passenger'] = request.user.profile
                existing_demand = Demand.objects.filter(
                    Q(passenger=validated_data['passenger']), Q(complete=False) & Q(canceled=False))
                if existing_demand.exists():
                    existing_demand = existing_demand.first()
                    raise NotAcceptable(
                        detail=f'User already has an active demand of id {existing_demand.id}')
            except Exception as e:
                print(e)
                raise ValidationError(
                    detail='User has no Profile')
            now = datetime.datetime.now()
            departure_date = validated_data['departure_time'].date()
            departure_time = validated_data['departure_time'].time()
            final_date_time = datetime.datetime.combine(
                departure_date, departure_time)

            if final_date_time < now:
                raise NotAcceptable(
                    detail='You can not book a ride for the previous dates.')
            for item in ['origin', 'destination']:
                a_location = Location.objects.create(
                    **validated_data.get(item))
                validated_data[item] = a_location
            return Demand.objects.create(**validated_data)
        raise ValidationError(
            detail='You must be a user to create a demand')

    class Meta:
        model = Demand
        fields = '__all__'


class RequestBoardSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        offer = validated_data['offer']
        if offer.is_full:
            raise ValidationError(detail='this offer is full')
        exist = RequestBoard.objects.filter(
            demand=validated_data['demand']).first()
        if exist:
            serializer = RequestBoardSerializer(exist)
            details = {'status': status.HTTP_400_BAD_REQUEST,
                       'message': 'User already has an existing request.Cancel request to make another',
                       'request_board': serializer.data}
            raise ValidationError(detail=details)
        return RequestBoard.objects.create(**validated_data)

    class Meta:
        model = RequestBoard
        fields = '__all__'


class TripDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripDetail
        fields = '__all__'


class TripSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        raise MethodNotAllowed(status.HTTP_405_METHOD_NOT_ALLOWED,
                               detail='Post request is not allowed in this field')

    class Meta:
        model = Trip
        fields = '__all__'
