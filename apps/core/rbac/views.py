import operator
import re
from collections import OrderedDict
from functools import reduce
from django.utils.dateparse import parse_date
from datetime import datetime
from django.db.models import Q, Count
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from apps.core.admin.views import get_ip_address
from apps.core.api.Pagination import LargeResultsSetPagination
from apps.core.api.viewset import CustomViewSetForQuerySet
from apps.core.api.validators import UniqueNameValidator
from apps.core.api.permission import GreenOfficeApiBasePermission
from django.utils import timezone
from apps.core.rbac.models import User, Role, Permission


class UserSerializer(serializers.ModelSerializer):
    slug_regex = re.compile(r'^[-a-zA-Z0-9_.]{4,50}$')

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())], required=True)
    username = serializers.RegexField(validators=[UniqueNameValidator(queryset=User.objects.all(), lookup='iexact')],
                                      regex=slug_regex,
                                      error_messages={
                                          'invalid': 'Username can contain alphanumeric, underscore and period(.). '
                                                     'Length: 4 to 50'
                                      })
    is_active = serializers.BooleanField(default=True)
    role_name = serializers.ReadOnlyField(source='role.name')
    group = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ['user_permissions', 'is_superuser', 'groups']
        read_only_fields = ('id', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        skip_list = ['is_active', 'is_superuser', 'position',
                     'status', 'replaced_by', 'expiry_date', 'role_id']
        for attr, value in validated_data.items():
            if instance.id == 1 and attr in skip_list:
                continue
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class UserViewSet(CustomViewSetForQuerySet):
    permission_classes = [GreenOfficeApiBasePermission]
    serializer_class = UserSerializer
    pagination_class = LargeResultsSetPagination
    model = User
    change_keys = {
        'role_name': 'role__name',
        'username': 'username',
    }
    search_keywords = ['username', 'first_name',
                       'last_name', 'email', 'role__name', 'status']
    permission_id = [1, 3, 25, ]

    def list(self, request, *args, **kwargs):
        queryset = self.model.objects.all()
        search = self.request.query_params.get('search[value]', None)
        column_id = self.request.query_params.get('order[0][column]', None)

        # search
        if search and search is not None and self.search_keywords is not None:
            search_logic = []

            for entity in self.search_keywords:
                search_logic.append(Q(**{entity + '__icontains': search}))

            queryset = queryset.filter(reduce(operator.or_, search_logic))

        # ascending or descending order
        if column_id and column_id is not None:
            column_name = self.request.query_params.get(
                'columns[' + column_id + '][data]', None)

            if self.change_keys is not None:
                for key in self.change_keys:
                    if column_name == key:
                        column_name = self.change_keys.get(key)

            if column_name != '':
                order_dir = '-' if self.request.query_params.get(
                    'order[0][dir]') == 'desc' else ''
                queryset = queryset.order_by(order_dir + column_name)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == 1:
            return Response(OrderedDict([
                ('detail', 'Superuser deleting prohibited.')
            ]), status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(default=True)
    code = serializers.RegexField(required=True,
                                  regex=re.compile(r'^[a-zA-Z0-9_]+$'),
                                  validators=[UniqueValidator(queryset=Role.objects.all())])
    permission_name = serializers.StringRelatedField(
        source='permission', many=True, read_only=True)
    user_count = serializers.StringRelatedField(
        source='user.count', read_only=True)

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'modified_at')


class RoleViewSet(CustomViewSetForQuerySet):
    permission_classes = [GreenOfficeApiBasePermission]
    serializer_class = RoleSerializer
    pagination_class = LargeResultsSetPagination
    model = Role
    change_keys = {
        'permission_name': 'permission__name',
        'user_count': 'user',
    }
    search_keywords = ['name']
    permission_id = [1, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        if int(self.kwargs.get('pk')) == 1:
            return Response({
                'errors': 'You can not update the detail of this role.'
            }, status=404)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance = self.get_object()
            serializer = self.get_serializer(instance)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.id == 1:
            return Response({
                'errors': 'You can not delete this role.'
            }, 404)

        user = instance.user.count()

        if user > 0:
            return Response({
                'errors': 'This role has already {0} user(s).'.format(user)
            }, 404)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        if self.model is None:
            raise AssertionError('CustomViewSetForQuerySet need to include a model')

        queryset = self.model.objects.filter()
        search = self.request.query_params.get('search[value]', None)
        column_id = self.request.query_params.get('order[0][column]', None)

        # search
        if search and search is not None and self.search_keywords is not None:
            search_logic = []
            print(search)

            for entity in self.search_keywords:
                search_logic.append(Q(**{entity + '__icontains': search}))

            queryset = queryset.filter(reduce(operator.or_, search_logic))

        # ascending or descending order
        if column_id and column_id is not None:

            column_name = self.request.query_params.get('columns[' + column_id + '][data]', None)
            print(column_name)

            if self.change_keys is not None:
                for key in self.change_keys:
                    if column_name == key:
                        column_name = self.change_keys.get(key)

            if column_name != '':
                order_dir = '-' if self.request.query_params.get('order[0][dir]') == 'desc' else ''
                if column_name == 'user_count':
                    print("ok")
                else:
                    queryset = queryset.order_by(order_dir + column_name).annotate(total=Count('user')).order_by(
                        order_dir + 'total')

        return queryset


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class PermissionViewSet(CustomViewSetForQuerySet):
    permission_classes = [GreenOfficeApiBasePermission]
    serializer_class = PermissionSerializer
    pagination_class = LargeResultsSetPagination
    model = Permission
    search_keywords = ['name']
    permission_id = [1, ]

    def get_queryset(self):
        if self.model is None:
            raise AssertionError(
                'CustomViewSetForQuerySet need to include a model')
        queryset = self.model.objects.filter().order_by('name')

        return queryset

