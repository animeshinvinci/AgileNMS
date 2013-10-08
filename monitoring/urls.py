from django.conf.urls import patterns, url, include
import views


urlpatterns = patterns("",
    url(r"^checks/$", views.CheckListView.as_view()),
    url(r"^checks/ok/$", views.CheckListView.as_view()),
    url(r"^checks/warning/$", views.CheckListView.as_view()),
    url(r"^checks/critical/$", views.CheckListView.as_view()),
    url(r"^checks/unknown/$", views.CheckListView.as_view()),
    url(r"^checks/disabled/$", views.CheckListView.as_view()),
    url(r"^checks/create/$", views.CheckCreateView.as_view()),
    url(r"^checks/(?P<pk>[0-9a-f]{32})/$", views.CheckDetailView.as_view()),
    url(r"^checks/(?P<pk>[0-9a-f]{32})/update/$", views.CheckUpdateView.as_view()),
    url(r"^checks/(?P<pk>[0-9a-f]{32})/delete/$", views.CheckDeleteView.as_view()),
)
