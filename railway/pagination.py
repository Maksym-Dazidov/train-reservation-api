from rest_framework.pagination import PageNumberPagination


class JourneyPagination(PageNumberPagination):
    page_size = 5
