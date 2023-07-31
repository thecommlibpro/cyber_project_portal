from django.urls import path, include

from . import views

urlpatterns = [
    path(
        "",
        views.SlotListView.as_view(),
        name="slot-list"
    ),
    path(
        "slot/<int:pk>",
        views.SlotDetailView.as_view(),
        name="slot-detail"
    ),
    path("select2/", include("django_select2.urls")),
]
