from django.views.generic import DetailView

from apps.core.admin.views import *
from apps.core.rbac.models import User


class UserManagementView(AdminView):
    template_name = 'core/user_management/users.html'


class AddUser(AdminView):
    template_name = 'core/user_management/add_user.html'


class EditUser(DetailView):
    sidebar_menu = admin_sidebar_menu
    template_name = 'core/user_management/edit_user.html'
    model = User


class RoleList(AdminView):
    template_name = 'core/user_management/role_list.html'


class department(AdminView):
    indicator = 'dept'
    sidebar_menu = admin_sidebar_menu
    template_name = 'core/user_management/department.html'

class branch(AdminView):
    indicator = 'branch'
    sidebar_menu = admin_sidebar_menu
    template_name = 'core/user_management/department.html'


class GroupList(AdminView):
    template_name = 'core/user_management/group_list.html'
