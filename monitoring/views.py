from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponse
import json
import models, forms


class CheckListView(ListView):
    model = models.Check


class CheckDetailView(DetailView):
    model = models.Check


class CheckCreateView(CreateView):
    model = models.Check
    form_class = forms.CheckForm


class CheckUpdateView(UpdateView):
    model = models.Check
    form_class = forms.CheckForm


class CheckDeleteView(DeleteView):
    model = models.Check
    success_url = "/checks/"


class ProblemListView(ListView):
    model = models.Problem


class ProblemDetailView(DetailView):
    model = models.Problem
