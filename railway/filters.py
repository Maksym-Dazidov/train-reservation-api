import django_filters
from .models import Journey


class JourneyFilter(django_filters.FilterSet):
    source = django_filters.CharFilter(
        field_name='route__source__name',
        lookup_expr='icontains'
    )
    destination = django_filters.CharFilter(
        field_name='route__destination__name',
        lookup_expr='icontains'
    )

    date = django_filters.DateFilter(
        field_name='departure_time',
        lookup_expr='date'
    )

    time_from = django_filters.TimeFilter(
        field_name='departure_time',
        lookup_expr='time__gte'
    )
    time_to = django_filters.TimeFilter(
        field_name='departure_time',
        lookup_expr='time__lte'
    )

    train_type = django_filters.CharFilter(
        field_name='train__train_type__name',
        lookup_expr='icontains'
    )

    free_tickets_gte = django_filters.NumberFilter(
        field_name='free_tickets',
        lookup_expr='gte',
        label='Free seats is greater than or equal to'
    )

    class Meta:
        model = Journey
        fields = []
