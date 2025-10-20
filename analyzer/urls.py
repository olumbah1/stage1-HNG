from django.urls import path
from .views import (
    CreateAnalyzeString,
    GetSpecificString,
    ListStrings,
    DeleteString
    )

urlpatterns = [

    path('strings', CreateAnalyzeString.as_view(), name='create_string'),

    path('strings/', ListStrings.as_view(), name='list_strings'),

    path('strings/<str:string_value>', GetSpecificString.as_view(), name='get_string'),

    path('strings/<str:string_value>/delete', DeleteString.as_view(), name='delete_string'),

]