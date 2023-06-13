from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, OfferViewSet, DemandViewSet, RequestBoardViewSet, TripViewSet, \
    RegisterView, LoginView


router = DefaultRouter()
router.register('profile', ProfileViewSet, basename='profile')
router.register('trip', TripViewSet, basename='trip')
router.register('offer', OfferViewSet, basename='offer')
router.register('demand', DemandViewSet, basename='demand')
router.register('request_board', RequestBoardViewSet, basename='request_board')
router.register('register', RegisterView, basename='register')
router.register('login', LoginView, basename='login')

urlpatterns = [
    path('', include(router.urls)),
]
