import factory
from . import models
import json

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

    name = factory.Faker('word',locale='es_ES')
    slug= factory.Faker('word',locale='es_ES')

class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Event

    name = factory.Faker('word',locale='es_ES')
    slug = factory.Faker('word',locale='es_ES')
    description = factory.Faker('sentence',locale='es_ES')

    @factory.lazy_attribute
    def category(self):
        return CategoryFactory.create()

class ParameterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Parameter

    name = factory.Faker('word',locale='es_ES')
    human_name = factory.Faker('word',locale='es_ES')
    serializer = ''

    @factory.lazy_attribute
    def event(self):
        return EventFactory.create()


class EventNotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventNotification

    name = factory.Faker('word',locale='es_ES')
    subject = factory.Faker('sentence',locale='es_ES')
    message = factory.Faker('sentence',locale='es_ES')

    @factory.lazy_attribute
    def event(self):
        return EventFactory.create()

class EventNotificationRecipientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventNotificationRecipient

    recipient = ""
    type = factory.Iterator(models.RECIPIENT_TYPE)

    @factory.lazy_attribute
    def notification(self):
        return EventNotificationFactory.create()