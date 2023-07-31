from django.urls import path

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
]
