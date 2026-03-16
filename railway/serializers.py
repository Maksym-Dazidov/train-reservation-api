from rest_framework import serializers
from django.db import transaction, IntegrityError

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


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ('id', 'name')


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ('id', 'name', 'latitude', 'longitude')


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ('id', 'first_name', 'last_name', 'full_name')
        read_only_fields = ('id', 'full_name')


class TrainSerializer(serializers.ModelSerializer):
    train_type = TrainTypeSerializer(read_only=True)
    total_places = serializers.IntegerField(read_only=True)

    class Meta:
        model = Train
        fields = ('id', 'name', 'carriage_num', 'places_in_carriage', 'total_places', 'train_type')


class RouteSerializer(serializers.ModelSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ('id', 'source', 'destination', 'distance')


class JourneySerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    taken_tickets = serializers.IntegerField(read_only=True)
    free_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            'id',
            'route',
            'train',
            'crew',
            'departure_time',
            'arrival_time',
            'taken_tickets',
            'free_tickets'
        )


class TrainWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ('id', 'name', 'carriage_num', 'places_in_carriage', 'train_type')


class RouteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('id', 'source', 'destination', 'distance')

    def validate(self, attrs):
        if attrs['source'] == attrs['destination']:
            raise serializers.ValidationError({
                'destination': 'Destination cannot be the same as source.'
            })

        if attrs['distance'] <= 0:
            raise serializers.ValidationError(
                {'distance': 'Distance must be positive.'}
            )

        return attrs


class JourneyWriteSerializer(serializers.ModelSerializer):
    crew = serializers.PrimaryKeyRelatedField(many=True, queryset=Crew.objects.all())

    class Meta:
        model = Journey
        fields = ('id', 'route', 'train', 'crew', 'departure_time', 'arrival_time')

    def validate(self, attrs):
        if attrs['arrival_time'] <= attrs['departure_time']:
            raise serializers.ValidationError(
                'Arrival time must be later than departure time.'
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        crew = validated_data.pop('crew')
        journey = Journey.objects.create(**validated_data)
        journey.crew.set(crew)
        return journey

    @transaction.atomic
    def update(self, instance, validated_data):
        crew = validated_data.pop('crew', None)
        journey = super().update(instance, validated_data)
        if crew is not None:
            journey.crew.set(crew)
        return journey


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'carriage', 'seat', 'journey', 'order', 'created_at', 'updated_at')
        read_only_fields = ('id', 'journey', 'order', 'created_at', 'updated_at')


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('carriage', 'seat', 'journey')

    def validate(self, attrs):
        train = attrs['journey'].train

        if attrs['carriage'] < 1:
            raise serializers.ValidationError(
                {'carriage': 'Carriage must be >= 1'}
            )

        if attrs['seat'] < 1:
            raise serializers.ValidationError(
                {'seat': 'Seat must be >= 1'}
            )

        if attrs['carriage'] > train.carriage_num:
            raise serializers.ValidationError(
                {'carriage': f'Max carriage number is {train.carriage_num}'}
            )

        if attrs['seat'] > train.places_in_carriage:
            raise serializers.ValidationError(
                {'seat': f'Max seat number is {train.places_in_carriage}'}
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'created_at', 'tickets')


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'tickets')

    def validate(self, attrs):
        if not attrs.get('tickets'):
            raise serializers.ValidationError(
                {'tickets': 'Order must contain at least one ticket'}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets')

        user = self.context['request'].user
        order = Order.objects.create(user=user)

        tickets = [
            Ticket(order=order, **ticket_data)
            for ticket_data in tickets_data
        ]

        try:
            Ticket.objects.bulk_create(tickets)
        except IntegrityError:
            raise serializers.ValidationError(
                {'tickets': 'Some seats are already taken.'}
            )

        return order
