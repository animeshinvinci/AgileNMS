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
    url(r"^checks/groups/$", views.GroupListView.as_view()),
    url(r"^checks/groups/create/$", views.GroupCreateView.as_view()),
    url(r"^checks/groups/(?P<pk>[a-z0-9-]+)/$", views.GroupDetailView.as_view()),
    url(r"^checks/groups/(?P<pk>[a-z0-9-]+)/update/$", views.GroupUpdateView.as_view()),
    url(r"^checks/groups/(?P<pk>[a-z0-9-]+)/delete/$", views.GroupDeleteView.as_view()),
    url(r"^checks/(?P<pk>\d+)/$", views.CheckDetailView.as_view()),
    url(r"^checks/(?P<pk>\d+)/update/$", views.CheckUpdateView.as_view()),
    url(r"^checks/(?P<pk>\d+)/delete/$", views.CheckDeleteView.as_view()),
    url(r"^problems/$", views.ProblemListView.as_view()),
    url(r"^problems/(?P<pk>\d+)/$", views.ProblemDetailView.as_view()),
    url(r"^reports/$", views.ReportListView.as_view()),
    url(r"^reports/create/$", views.ReportCreateView.as_view()),
    url(r"^reports/(?P<pk>\d+)/$", views.ReportDetailView.as_view()),
    url(r"^reports/(?P<pk>\d+)/update/$", views.ReportUpdateView.as_view()),
    url(r"^reports/(?P<pk>\d+)/delete/$", views.ReportDeleteView.as_view()),
)
