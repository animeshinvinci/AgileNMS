from django.views.generic import ListView, DetailView
from django.http import Http404, HttpResponse
import json
import models


class CheckListView(ListView):
    model = models.Check


class CheckDetailView(DetailView):
    model = models.Check
