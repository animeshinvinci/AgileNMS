from django.conf.urls import patterns, url, include
import views


urlpatterns = patterns("",
    url(r"^monitors/$", views.MonitorListView.as_view()),
    url(r"^monitors/(?P<pk>[0-9a-f]{32})/$", views.MonitorDetailView.as_view()),
    url(r"^monitors/(?P<monitor_pk>[0-9a-f]{32})/checks/$", views.CheckListView.as_view()),
    url(r"^monitors/(?P<monitor_pk>[0-9a-f]{32})/checks/ok/$", views.CheckListView.as_view()),
    url(r"^monitors/(?P<monitor_pk>[0-9a-f]{32})/checks/warning/$", views.CheckListView.as_view()),
    url(r"^monitors/(?P<monitor_pk>[0-9a-f]{32})/checks/critical/$", views.CheckListView.as_view()),
    url(r"^monitors/(?P<monitor_pk>[0-9a-f]{32})/checks/unknown/$", views.CheckListView.as_view()),
    url(r"^monitors/(?P<monitor_pk>[0-9a-f]{32})/checks/disabled/$", views.CheckListView.as_view()),
    url(r"^checks/$", views.CheckListView.as_view()),
    url(r"^checks/ok/$", views.CheckListView.as_view()),
    url(r"^checks/warning/$", views.CheckListView.as_view()),
    url(r"^checks/critical/$", views.CheckListView.as_view()),
    url(r"^checks/unknown/$", views.CheckListView.as_view()),
    url(r"^checks/disabled/$", views.CheckListView.as_view()),
    url(r"^checks/(?P<pk>[0-9a-f]{32})/$", views.CheckDetailView.as_view()),
    url(r"^problems/$", views.ProblemListView.as_view()),
    url(r"^problems/(?P<pk>[0-9a-f]{32})/$", views.ProblemDetailView.as_view()),
    url(r"^reports/$", views.ReportListView.as_view()),
    url(r"^reports/(?P<pk>[0-9a-f]{32})/$", views.ReportDetailView.as_view()),
)
