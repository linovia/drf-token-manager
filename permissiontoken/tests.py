from __future__ import unicode_literals

import base64

from django.contrib.auth.models import User, Permission
from django.test import TestCase

from rest_framework import generics, status, HTTP_HEADER_ENCODING
from rest_framework.test import APIRequestFactory

from . import permissions, authentication
from .models import Token


factory = APIRequestFactory()


class RootView(generics.ListCreateAPIView):
    model = User
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.TokenPermissions]


class InstanceView(generics.RetrieveUpdateDestroyAPIView):
    model = User
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.TokenPermissions]

root_view = RootView.as_view()
instance_view = InstanceView.as_view()


def basic_auth_header(username, password):
    credentials = ('%s:%s' % (username, password))
    base64_credentials = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode(HTTP_HEADER_ENCODING)
    return 'Basic %s' % base64_credentials


class TokenPermissionsTests(TestCase):
    def setUp(self):
        User.objects.create_user('disallowed', 'disallowed@example.com', 'password')
        user = User.objects.create_user('permitted', 'permitted@example.com', 'password')
        self.token1 = Token.objects.create(user=user)
        self.token1.permissions.add(
            Permission.objects.get(codename='add_user'),
            Permission.objects.get(codename='change_user'),
            Permission.objects.get(codename='delete_user')
        )
        user = User.objects.create_user('updateonly', 'updateonly@example.com', 'password')
        self.token2 = Token.objects.create(user=user)
        self.token2.permissions.add(
            Permission.objects.get(codename='change_user'),
        )

    def test_has_create_permissions(self):
        request = factory.post('/', {'username': 'foobar', 'password': 'foobar'}, format='json',
                               HTTP_AUTHORIZATION='token ' + self.token1.key)
        response = root_view(request, pk=1)
        assert response.status_code == status.HTTP_201_CREATED

    def test_does_not_have_create_permissions(self):
        request = factory.post('/', {'username': 'foobar', 'password': 'foobar'}, format='json',
                               HTTP_AUTHORIZATION='token ' + self.token2.key)
        response = root_view(request, pk=1)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_token_user_is_inactive(self):
        self.token1.user.is_active = False
        self.token1.user.save()
        request = factory.post('/', {'username': 'foobar', 'password': 'foobar'}, format='json',
                               HTTP_AUTHORIZATION='token ' + self.token1.key)
        response = root_view(request, pk=1)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
