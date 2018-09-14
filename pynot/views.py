# -*- coding: utf-8 -*-
"""
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import BaseFilterBackend, SearchFilter
from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models
from . import serializers


class CategoryView(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    Notification Category services

    list:
    Returns the list of any notification category

    retrieve:
    Returns a notification category. Each category has the list of events
    """
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def list(self, request, *args, **kwargs):
        models.PyNot.sync_settings()

        return super(CategoryView, self).list(request, args, kwargs)



class EventView(RetrieveModelMixin, GenericViewSet):
    """
    Notification Event services

    retrieve:
    Returns a notification event. Each event has the list of parameters
    """
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer


class EventNotificationView(RetrieveModelMixin, CreateModelMixin,
                            UpdateModelMixin, DestroyModelMixin,
                            GenericViewSet):
    """
    EventNotification services

    retrieve:
    Returns an notification event

    create:
    Create an EventNotification
    ```JSON
    {
      "event": "ForeignKey",
      "name": "string",
      "description": "string",
      "type": "(email, )",
      "subject": "string",
      "message": "string",
      "collective": "false",
      "recipients": [
        {"recipient":"an email, an user or a group",
         "type":"(email, user, group)"}
      ]
    }
    ```

    partial_update:
    Patch an EventNotification
    ```JSON
    {
      "event": "ForeignKey",
      "name": "string",
      "description": "string",
      "type": "(email, )",
      "subject": "string",
      "message": "string",
      "recipients": [
        {"recipient":"an email, an user or a group",
         "type":"(email, user, group)"}
      ]
    }
    ```

    update:
    Update an EventNotification
    ```JSON
    {
      "event": "ForeignKey",
      "name": "string",
      "description": "string",
      "type": "(email, )",
      "subject": "string",
      "message": "string",
      "recipients": [
        {"recipient":"an email, an user or a group",
         "type":"(email, user, group)"}
      ]
    }
    ```

    destroy:
    Destroy an EventNotification
    """
    queryset = models.EventNotification.objects.all()
    serializer_class = serializers.EventNotificationSerializer




class NotificationOwnerFilter(BaseFilterBackend):
    """
    A filter backend that limits results to those where the requesting user
    has read object level permissions.
    """
    def filter_queryset(self, request, queryset, view):
        """
        Filtro por perfil de usuario
        :param request:
        :param queryset:
        :param view:
        :return:
        """
        user = request.user
        if user and user.is_authenticated:
            return queryset.filter(users__id=user.id)
        return queryset.model.objects.none()

class NotificationView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    Notification services

    list:
    Returns the list of any notification
    """
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    filter_backends = [NotificationOwnerFilter, DjangoFilterBackend, SearchFilter]
    permission_classes = [IsAuthenticated]
    filter_fields = {
        'is_read':['exact'],
        'is_important':['exact'],
        'notification__event_notification__event_id':['exact'],
        'notification__event_notification__event__category_id':['exact'],
    }

    search_fields = ('notification__subject', 'notification__message')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read=True
        instance.save()
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def read_pending(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(is_read=False, users__id=request.user.id)
        return Response({"unread": self.queryset.count()})

    @action(detail=True, methods=['patch'])
    def important(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_important = not instance.is_important
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

