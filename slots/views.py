from django.shortcuts import render


from django.views.generic import (
    ListView,
    DetailView,
)

from .models import Slot

class SlotListView(ListView):
    model = Slot
    queryset = Slot.objects.all().order_by("-datetime")

class SlotDetailView(DetailView):
    model = Slot
