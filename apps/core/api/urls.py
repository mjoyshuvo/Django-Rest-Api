from django.conf.urls import url, include
from apps.core.auth.views import login_user, ChangePasswordView
from conf import settings

urlpatterns = [
    url(r'^v1/auth/login/$', login_user, name='login'),
    url(r'^v1/', include('apps.core.rbac.urls', 'rbac')),
    url(r'^v1/auth/change_password/', ChangePasswordView.as_view(), name='change_password'),
]
