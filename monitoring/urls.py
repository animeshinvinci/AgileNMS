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
    url(r"^problems/$", views.ProblemListView.as_view()),
    url(r"^problems/(?P<pk>[0-9a-f]{32})/$", views.ProblemDetailView.as_view()),
    url(r"^reports/$", views.ReportListView.as_view()),
    url(r"^reports/create/$", views.ReportCreateView.as_view()),
    url(r"^reports/(?P<pk>[0-9a-f]{32})/$", views.ReportDetailView.as_view()),
    url(r"^reports/(?P<pk>[0-9a-f]{32})/update/$", views.ReportUpdateView.as_view()),
    url(r"^reports/(?P<pk>[0-9a-f]{32})/delete/$", views.ReportDeleteView.as_view()),
)
