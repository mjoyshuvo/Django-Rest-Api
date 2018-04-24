from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('role', RoleViewSet, base_name='role')
router.register('permission', PermissionViewSet, base_name='permission')
router.register('user', UserViewSet, base_name='user')

urlpatterns = [
    url(r'^', include(router.urls)),
]
