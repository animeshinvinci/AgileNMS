from django.views.generic import ListView, DetailView
from django.http import HttpResponse
import json
import models


class APICheckListView(ListView):
    model = models.Check

    def render_to_response(self, context):
        return HttpResponse("Check list will go here")


class APICheckDetailView(DetailView):
    model = models.Check

    def render_to_response(self, context):
        return HttpResponse("Check will go here")

from django.conf.urls import patterns, url, include
urlpatterns = patterns("",
    url(r"^checks/$", APICheckListView.as_view()),
    url(r"^checks/(?P<pk>[0-9a-f]{32})/$", APICheckDetailView.as_view()),
)
