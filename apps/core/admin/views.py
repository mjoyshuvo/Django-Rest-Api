from django import forms
from django.forms.models import ModelForm, modelform_factory
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from conf import settings


def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[-1].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    return ip_address


@property
def admin_sidebar_menu(self):
    sidebar = []
    user_management_menu = [
        ['allowed', 'Users', reverse_lazy('admin:user:list'), 'zmdi-accounts-list-alt', []],
        ['allowed', 'Roles', reverse_lazy('admin:user:role_list'), 'zmdi-account-box', []]
    ]

    if self.request.user.role.id == 1:
        sidebar.append(['allowed', 'User Management', '#', 'zmdi-pin-account', user_management_menu])

        sidebar.append(
            ['allowed', 'Announcement', reverse_lazy('admin:announcement:view'), 'zmdi-surround-sound', []]
        )

    else:
        perm_list = self.request.session.get('permission_list')

        if 1 in perm_list:
            sidebar.append(['allowed', 'User Management', '#', 'zmdi-pin-account', user_management_menu])

    return sidebar


class AdminView(TemplateView):
    sidebar_menu = admin_sidebar_menu

