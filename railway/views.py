from django.db.models import Count, F
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    TrainType,
    Station,
    Crew,
    Train,
    Route,
    Journey,
    Order,
    Ticket
)
from .serializers import (
    TrainTypeSerializer,
    StationSerializer,
    CrewSerializer,
    TrainSerializer,
    TrainWriteSerializer,
    RouteSerializer,
    RouteWriteSerializer,
    JourneySerializer,
    JourneyWriteSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    TicketSerializer
)
from .permissions import IsAdminOrReadOnly
from .pagination import JourneyPagination
from .filters import JourneyFilter


class TrainTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = [permissions.AllowAny]


class StationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [permissions.IsAdminUser]


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related('train_type')
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TrainWriteSerializer
        return TrainSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related('source', 'destination')
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RouteWriteSerializer
        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.select_related(
        'train',
        'route__source',
        'route__destination'
    ).prefetch_related(
        'crew'
    ).annotate(
        taken_tickets=Count('tickets', distinct=True),
    ).annotate(
        free_tickets=F('train__carriage_num') * F('train__places_in_carriage') - F('taken_tickets')
    )
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = JourneyPagination
    filterset_class = JourneyFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return JourneyWriteSerializer
        return JourneySerializer


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.select_related(
        'order',
        'journey__train',
        'journey__route__source',
        'journey__route__destination',
    )
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAdminUser]


class OrderViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'tickets__journey__train',
            'tickets__journey__route__source',
            'tickets__journey__route__destination'
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @action(detail=False, methods=['get'])
    def tickets(self, request):
        """
        Retrieve all tickets belonging to the authenticated user.
        """
        tickets = Ticket.objects.filter(order__user=request.user).select_related(
            'order',
            'journey__train',
            'journey__route__source',
            'journey__route__destination',
        )
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
