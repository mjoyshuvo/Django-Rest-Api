from django.conf.urls import url, include

urlpatterns = [
    url(r'^user/', include('apps.core.user_management.urls', 'user')),
]
