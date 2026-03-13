from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class TrainType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Station(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Crew(TimeStampedModel):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, db_index=True)

    class Meta:
        ordering = ('last_name',)
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Train(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    carriage_num = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    places_in_carriage = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.PROTECT,
        related_name='trains'
    )

    @property
    def total_places(self):
        return self.places_in_carriage * self.carriage_num

    def __str__(self):
        return self.name


class Route(TimeStampedModel):
    source = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name='routes_from'
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name='routes_to'
    )
    distance = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(source=models.F('destination')),
                name='route_source_not_equal_destination',
            ),
            models.UniqueConstraint(
                fields=('source', 'destination'),
                name='unique_route_direction',
            )
        ]

    def __str__(self):
        return f'{self.source.name} -> {self.destination.name}'


class Journey(TimeStampedModel):
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name='journeys'
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.PROTECT,
        related_name='journeys'
    )
    crew = models.ManyToManyField(
        Crew,
        related_name='journeys'
    )
    departure_time = models.DateTimeField(db_index=True)
    arrival_time = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ('departure_time',)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(arrival_time__gt=models.F('departure_time')),
                name='arrival_after_departure'
            )
        ]

    def __str__(self):
        return f'{self.route} ({self.departure_time})'


class Order(TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'Order #{self.id}'


class Ticket(TimeStampedModel):
    carriage = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    seat = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('journey', 'carriage', 'seat'),
                name='unique_seat_per_journey',
            )
        ]

    def clean(self):
        super().clean()

        if not self.journey_id:
            return

        train = self.journey.train

        if self.carriage > train.carriage_num:
            raise ValidationError({
                "carriage": f"Carriage number cannot exceed {train.carriage_num}"
            })

        if self.seat > train.places_in_carriage:
            raise ValidationError({
                "seat": f"Seat number cannot exceed {train.places_in_carriage}"
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Ticket #{self.id}'
