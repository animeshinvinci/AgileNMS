from django.views.generic import ListView, DetailView
from django.http import Http404, HttpResponse
import json
import models


class MonitorListView(ListView):
    model = models.Monitor


class MonitorDetailView(DetailView):
    model = models.Monitor


class ProblemListView(ListView):
    model = models.Problem


class ProblemDetailView(DetailView):
    model = models.Problem
