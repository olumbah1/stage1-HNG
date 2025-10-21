# analyzer/urls.py
from django.urls import path
from .views import (
    StringsCollection,
    GetSpecificString,
    DeleteString,
    FilterByNaturalLanguage,
)

urlpatterns = [
    # Combined collection endpoint (supports GET and POST for /strings and /strings/)
    path('strings', StringsCollection.as_view(), name='strings_no_slash'),
    path('strings/', StringsCollection.as_view(), name='strings_with_slash'),

    # Natural language filter
    path('strings/filter-by-natural-language', FilterByNaturalLanguage.as_view(), name='filter_by_nl'),

    # DELETE must come before the generic GET to avoid greedy matching
    path('strings/<path:string_value>/delete', DeleteString.as_view(), name='delete_string'),

    # Get a specific string (GET)
    path('strings/<path:string_value>', GetSpecificString.as_view(), name='get_string'),
]
