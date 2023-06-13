from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, MethodNotAllowed, ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Profile, Offer, Demand, RequestBoard, TripDetail, Trip
from .serializers import ProfileSerializer, OfferSerializer, DemandSerializer, RequestBoardSerializer, \
    TripDetailsSerializer, TripSerializer
from rest_framework import status
from rest_framework.response import Response


# Create your views here.
# class TripViewSet(viewsets.ModelViewSet):
#     queryset = Trip.objects.all()
#     serializer_class = TripSerializer
#
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     search_fields = ['trip_name']
#     filterset_fields = ['trip_name', 'start_point', 'end_point', 'departure_date', 'transport_type']
#     ordering_fields = ['departure_date']
#     pagination_class = pagination.PageNumberPagination
#
#     @action(detail=False, methods=['get'])
#     def my_trips(self, request):
#         user = request.user
#         trips = Trip.objects.filter(users=user)
#         serializer = TripSerializer(trips, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     @action(detail=False, methods=['post'])
#     def join_trip(self, request):
#         trip_id = request.data.get('trip_id')
#         user = request.user
#
#         try:
#             trip = Trip.objects.get(pk=trip_id)
#         except Trip.DoesNotExist:
#             return Response({'message': 'Поездка не существует.'}, status=status.HTTP_404_NOT_FOUND)
#
#         if trip.users.filter(pk=user.pk).exists():
#             return Response({'message': 'Вы уже присоединены к этой поездке.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if trip.available_seats <= 0:
#             return Response({'message': 'Нет доступных мест в этой поездке.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         trip.users.add(user)
#         trip.available_seats -= 1
#         return Response({'message': 'Вы успешно присоединились к поездке.'}, status=status.HTTP_200_OK)
#
#
# class UserProfileViewSet(viewsets.ModelViewSet):
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OfferSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = self.request.user.profile
        return queryset.filter(driver=profile)

    def post(self, request, profile, *args, **kwargs):
        return self.create(request, profile, *args, **kwargs)


class DemandViewSet(viewsets.ModelViewSet):
    queryset = Demand.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DemandSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        id = self.request.query_params.get('id')
        if id:
            object = Demand.objects.filter(pk=int(id))
            if object.exists():
                return object
            raise NotFound(detail='Demand with that ID does not exists.')
        return Demand.objects.filter(passenger=profile)

    def post(self, request, profile, *args, **kwargs):
        return self.create(request, profile, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('Delete', detail='You can not delete a demand.')


class RequestBoardViewSet(viewsets.ModelViewSet):
    queryset = RequestBoard.objects.all()
    serializer_class = RequestBoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        demand = self.request.query_params.get('demand')
        status = self.request.query_params.get('status')
        offer = self.request.query_params.get('offer')
        if status and demand:
            options = ["PE", "AC", "DE"]
            status = "PE" if 'p' in status.lower() else status
            status = "AC" if 'a' in status.lower() else status
            status = "DE" if 'd' in status.lower() else status
            if status not in options:
                raise ValidationError(detail={"error": "invalid stautus"})
            return RequestBoard.objects.filter(demand__pk=int(demand), status=status)
        if demand:
            return RequestBoard.objects.filter(demand__pk=int(demand))
        if offer:
            return RequestBoard.objects.filter(offer__pk=int(offer))
        return RequestBoard.objects.all()

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        return self.create(request, profile, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TripDetailViewSet(viewsets.ModelViewSet):
    queryset = TripDetail.objects.all()
    serializer_class = TripDetailsSerializer
    permission_classes = [IsAuthenticated]


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        offer_id = self.request.query_params.get('offer')
        if offer_id:
            offer_id = int(offer_id)
            return Trip.objects.filter(offer__id=offer_id).all()
        profile = self.request.user.profile
        return Trip.objects.filter(offer__driver=profile).all()

    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed(status.HTTP_400_METHOD_NOT_ALLOWED, detail='Post request is not allowed in this field.')


class RegisterView(viewsets.ModelViewSet):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'message': 'Username already exists.'},
                            status=status.HTTP_409_CONFLICT)

        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)

        user.save()
        token.save()

        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class LoginView(viewsets.ModelViewSet):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not User.objects.filter(username=username).exists():
            return Response({'message': 'Username does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

        user = User.objects.get(username=username)

        if not user.check_password(password):
            return Response({'message': 'Incorrect password'},
                            status=status.HTTP_401_UNAUTHORIZED)

        token = Token.objects.get(user=user)

        return Response({'token': token.key}, status=status.HTTP_200_O)
