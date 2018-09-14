# -*- coding: utf-8 -*-
"""
Serializador para expedientes
"""
from drf_writable_nested import WritableNestedModelSerializer
from . import models

class DynamicFieldModelSerializer(WritableNestedModelSerializer):
    @classmethod
    def many_init(cls, *args, **kwargs):
        if hasattr(cls.Meta, 'fields_list'):
            kwargs["fields"] = cls.Meta.fields_list
        return super(DynamicFieldModelSerializer, cls).many_init(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class EventNotificationFireSimpleSerializer(DynamicFieldModelSerializer):
    """
    Notification event fire serializer
    """
    class Meta(object):
        model = models.EventNotificationFire
        fields = ('id', 'subject', 'message', 'creation_datetime')


class NotificationSerializer(DynamicFieldModelSerializer):
    """
    Notification event serializer
    """
    notification = EventNotificationFireSimpleSerializer()

    class Meta(object):
        model = models.Notification
        fields = ('id', 'notification', 'recipient', 'type',
                  'status', 'is_read', 'is_important')

class EventNotificationFireSerializer(DynamicFieldModelSerializer):
    """
    Notification event fire serializer
    """
    notifications = NotificationSerializer()

    class Meta(object):
        model = models.EventNotificationFire
        fields = ('id', 'notifications', 'subject', 'message')
        fields_list = ('id', 'subject', 'message')

class EventNotificationRecipientSerializer(DynamicFieldModelSerializer):
    """
    Notification event serializer
    """

    class Meta(object):
        model = models.EventNotificationRecipient
        fields = ('id', 'recipient', 'type', 'notification')
        read_only_fields = ('notification', )

class EventNotificationSerializer(DynamicFieldModelSerializer):
    """
    Notification event serializer
    """

    ## recipients
    recipients = EventNotificationRecipientSerializer(required=False,
                                                      many=True)

    class Meta(object):
        model = models.EventNotification
        fields = ('id', 'name', 'description', 'type', 'event', 'message',
                  'subject', 'recipients', 'collective')


class ParameterSerializer(DynamicFieldModelSerializer):
    """
    Notification event parameter serializer
    """

    class Meta(object):
        model = models.Parameter
        fields = ('id', 'name', 'human_name', 'data_body', 'data_email', 'data_user', 'data_group', 'data_file', 'event')

class EventSerializer(DynamicFieldModelSerializer):
    """
    Notification event serializer
    """

    ## parameters
    parameters = ParameterSerializer(required=False, many=True)

    ## notifications
    notifications = EventNotificationSerializer(required=False, many=True, fields=('id', 'name', 'description', 'type'))

    class Meta(object):
        model = models.Event
        fields = ('id', 'name', 'description', 'category', 'parameters', 'notifications')

class CategorySerializer(DynamicFieldModelSerializer):
    """
    Notification category serializer
    """

    ## events
    events = EventSerializer(required=False, many=True, fields=('id', 'name', 'description'))

    class Meta(object):
        model = models.Category
        fields = ('id', 'name', 'events')
        fields_list = ('id', 'name')