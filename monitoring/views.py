from django.views.generic import ListView, DetailView
from django.http import Http404, HttpResponse
import json
import models


class CheckListView(ListView):
    model = models.Check


class CheckDetailView(DetailView):
    model = models.Check


class ProblemListView(ListView):
    model = models.Problem


class ProblemDetailView(DetailView):
    model = models.Problem
