from django.conf.urls import url, include
from .views import DashboardView
from django.shortcuts import redirect
from conf import settings


def go_to(self):
    return redirect(settings.LOGIN_URL)


urlpatterns = [
    url(r'^$', go_to),
    url(r'^login/', include('apps.core.auth.urls', 'auth')),
    url(r'^api/', include('apps.core.api.urls', 'api')),
    url(r'^$', DashboardView.as_view(), name='dashboard'),
]
