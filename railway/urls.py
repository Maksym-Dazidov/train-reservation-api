from django.urls import path, include
from rest_framework.routers import DefaultRouter

from railway.views import (
    TrainTypeViewSet,
    StationViewSet,
    CrewViewSet,
    TrainViewSet,
    RouteViewSet,
    JourneyViewSet,
    TicketViewSet,
    OrderViewSet
)

router = DefaultRouter()

router.register('train-types', TrainTypeViewSet, basename='train-type')
router.register('stations', StationViewSet, basename='station')
router.register('crews', CrewViewSet, basename='crew')
router.register('trains', TrainViewSet, basename='train')
router.register('routes', RouteViewSet, basename='route')
router.register('journeys', JourneyViewSet, basename='journey')
router.register('tickets', TicketViewSet, basename='ticket')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = 'railway'
