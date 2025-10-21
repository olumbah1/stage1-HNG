from django.urls import path
from .views import (
    StringsCollection,
    GetSpecificString,
    DeleteString,
    FilterByNaturalLanguage,
)

urlpatterns = [
    # Combined collection endpoint (supports GET and POST)
    path('strings', StringsCollection.as_view(), name='strings_no_slash'),
    path('strings/', StringsCollection.as_view(), name='strings_with_slash'),

    # Natural language filter
    path('strings/filter-by-natural-language', FilterByNaturalLanguage.as_view(), name='filter_by_nl'),

    # IMPORTANT: place the DELETE route before the generic GET route so it is matched first.
    path('strings/<path:string_value>/delete', DeleteString.as_view(), name='delete_string'),

    # Get a specific string (must come after the delete route)
    path('strings/<path:string_value>', GetSpecificString.as_view(), name='get_string'),
]
