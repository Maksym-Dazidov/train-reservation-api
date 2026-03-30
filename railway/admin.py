from django.contrib import admin

from railway.models import (
    TrainType,
    Station,
    Crew,
    Train,
    Route,
    Journey,
    Order,
    Ticket
)


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    ordering = ("name",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    ordering = ("name",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "created_at")
    search_fields = ("first_name", "last_name")
    list_filter = ("created_at",)
    ordering = ("last_name",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "train_type",
        "carriage_num",
        "places_in_carriage",
        "total_places_display",
        "created_at",
    )
    search_fields = ("name",)
    list_filter = ("train_type",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("train_type",)
    list_select_related = ("train_type",)

    def total_places_display(self, obj):
        return obj.total_places

    total_places_display.short_description = "Total places"


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "destination",
        "distance",
        "created_at",
    )
    list_filter = ("source", "destination")
    search_fields = (
        "source__name",
        "destination__name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    autocomplete_fields = ("source", "destination")
    list_select_related = ("source", "destination")


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "train",
        "departure_time",
        "arrival_time",
        "created_at",
    )
    list_filter = ("departure_time", "train")
    search_fields = (
        "route__source__name",
        "route__destination__name",
        "train__name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("route", "train", "crew")
    filter_horizontal = ("crew",)
    list_select_related = ("route__source", "route__destination", "train")


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("user__email",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)
    list_select_related = ("user",)
    inlines = [TicketInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "journey",
        "order",
        "carriage",
        "seat",
        "created_at",
    )
    list_filter = ("journey",)
    search_fields = (
        "journey__route__source__name",
        "journey__route__destination__name",
        "order__user__email",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("journey", "order")
    list_select_related = ("journey", "order")
