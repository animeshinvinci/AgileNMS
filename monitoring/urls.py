from django.conf.urls import patterns, url, include
import views


urlpatterns = patterns("",
    url(r"^checks/$", views.CheckListView.as_view()),
    url(r"^checks/(?P<pk>[0-9a-f]{32})/$", views.CheckDetailView.as_view()),
    url(r"^problems/$", views.ProblemListView.as_view()),
    url(r"^problems/(?P<pk>[0-9a-f]{32})/$", views.ProblemDetailView.as_view()),
)
