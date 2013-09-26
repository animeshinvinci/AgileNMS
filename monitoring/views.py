from django.views.generic import ListView, DetailView
import models


class CheckListView(ListView):
    model = models.Check


class CheckDetailView(DetailView):
    model = models.Check


from django.conf.urls import patterns, url, include
urlpatterns = patterns("",
    url(r"^checks/$", CheckListView.as_view()),
    url(r"^checks/(?P<pk>[0-9a-f]{32})/$", CheckDetailView.as_view()),
)
