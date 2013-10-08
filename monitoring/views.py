from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponse
import json
import models


class CheckListView(ListView):
    model = models.Check


class CheckDetailView(DetailView):
    model = models.Check


class CheckCreateView(CreateView):
    model = models.Check


class CheckUpdateView(UpdateView):
    model = models.Check


class CheckDeleteView(DeleteView):
    model = models.Check
    success_url = "/checks/"
