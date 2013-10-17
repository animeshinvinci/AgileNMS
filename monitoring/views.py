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



class GroupListView(ListView):
    model = models.Group


class GroupDetailView(DetailView):
    model = models.Group


class GroupCreateView(CreateView):
    model = models.Group
    form_class = forms.GroupForm


class GroupUpdateView(CreateView):
    model = models.Group
    form_class = forms.GroupForm


class GroupDeleteView(DeleteView):
    model = models.Group
    success_url = "/checks/groups/"



class ProblemListView(ListView):
    model = models.Problem


class ProblemDetailView(DetailView):
    model = models.Problem



class ReportListView(ListView):
    model = models.Report


class ReportDetailView(DetailView):
    model = models.Report


class ReportCreateView(CreateView):
    model = models.Report
    form_class = forms.ReportForm


class ReportUpdateView(UpdateView):
    model = models.Report
    form_class = forms.ReportForm


class ReportDeleteView(DeleteView):
    model = models.Report
    success_url = "/reports/"
