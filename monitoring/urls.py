from django.conf.urls import patterns, url, include
import views


urlpatterns = patterns("",
    url(r"^monitors/$", views.MonitorListView.as_view()),
    url(r"^monitors/(?P<pk>[0-9a-f]{32})/$", views.MonitorDetailView.as_view()),
    url(r"^problems/$", views.ProblemListView.as_view()),
    url(r"^problems/(?P<pk>[0-9a-f]{32})/$", views.ProblemDetailView.as_view()),
)
