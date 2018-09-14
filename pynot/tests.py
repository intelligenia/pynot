from django.test import TestCase

from pynot.models import *
from pynot.factories import *
from rest_assured.testcases import *
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import serializers



class CategoryTestCase(ReadRESTAPITestCaseMixin, 
                        BaseRESTAPITestCase):
    base_name = 'category'
    factory_class = CategoryFactory
    lookup_field = 'id'
    attributes_to_check = ['id', 'name']

    def setUp(self):
        admin=get_user_model().objects.create_superuser(
            email="admin@example.com", password="admin")
        token = Token.objects.get_or_create(user=admin)[0].key
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}
        self.client.credentials(**headers)

        models.PyNot.sync_settings()

        super(CategoryTestCase, self).setUp()


class EventTestCase(DetailAPITestCaseMixin, 
                        BaseRESTAPITestCase):
    base_name = 'event'
    factory_class = EventFactory
    lookup_field = 'id'
    attributes_to_check = ['id', 'name', 'description']

    def setUp(self):
        admin=get_user_model().objects.create_superuser(
            email="admin@example.com", password="admin")
        token = Token.objects.get_or_create(user=admin)[0].key
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}
        self.client.credentials(**headers)

        super(EventTestCase, self).setUp()

class ParameterTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name')
        extra_fields_human_name = {'id':'ID',
                                   'name':'Nombre'}
        extra_fields_email = ('name',)


class EventTestSerializer(serializers.ModelSerializer):
    parameters = ParameterTestSerializer(many=True)

    class Meta:
        model = Event
        fields = ('id', 'name', 'description', 'parameters')
        extra_fields_human_name = {'id':'ID',
                                   'name':'Nombre',
                                   'description':u'Descripción',
                                   'parameters':u'Parámetros'}
        extra_fields_group = ('id',)


class CategoryTestSerializer(serializers.ModelSerializer):

    events = EventTestSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'events')
        extra_fields_human_name = {'name':'Nombre',
                                   'events':'Eventos'}
        extra_fields_email = ('name',)
        extra_fields_user = ('id',)


class ParameterTestCase(TestCase):
    category = None
    event = None
    parameter = None
    notification = None

    def setUp(self):
        self.category = CategoryFactory.create(name='cat_name')

        self.event = EventFactory.create(category=self.category,
                                         name='event_name',
                                         slug='slug_event')

        event = EventFactory.create(category=self.category,
                                    name='event_name2')

        self.parameter = ParameterFactory.create(event=self.event,
            serializer='pynot.tests.CategoryTestSerializer',
            name='param_name',
            human_name='Categoria')
        parameter = ParameterFactory.create(event=event,
            serializer='pynot.tests.CategoryTestSerializer',
            name='param_name2',
            human_name='Parametro 2')
        parameter = ParameterFactory.create(event=event,
            serializer='pynot.tests.CategoryTestSerializer',
            name='param_name3',
            human_name='Parametro 3')

        self.notification = EventNotificationFactory.create(event=self.event,
            name='Mensaje de alta de usuario',
            message='El nombre de la categoria es param_name.name')

        EventNotificationRecipientFactory.create(
            notification=self.notification, recipient='test@test.com',
            type='email')
        EventNotificationRecipientFactory.create(
            notification=self.notification, recipient='param_name.events.parameters.name',
            type='email')
        EventNotificationRecipientFactory.create(
            notification=self.notification, recipient='1',
            type='user')
        EventNotificationRecipientFactory.create(
            notification=self.notification, recipient='2',
            type='user')

    def test_get_serializer_data_body(self):

        data_body = self.parameter.data_body
        self.assertEqual(data_body["id"]["human_name"], "id")
        self.assertTrue('events' not in data_body)

    def test_get_serializer_data_emails(self):

        data_email = self.parameter.data_email
        self.assertTrue("id" not in data_email)
        self.assertEqual(data_email["events"]["data"]["parameters"]\
                             ["data"]["name"]["human_name"], "Nombre")

    def test_get_serializer_data_users(self):
        data_user = self.parameter.data_user
        self.assertTrue("name" not in data_user)
        self.assertTrue("id" in data_user)

    def test_get_serializer_data_groups(self):
        data_group = self.parameter.data_group
        self.assertTrue("id" not in data_group)
        self.assertEqual(data_group["events"]["data"]["id"]["human_name"],
                         "ID")

    def test_fire(self):

        self.event.fire(param_name=CategoryTestSerializer(self.category))
        self.assertEqual(models.EventNotificationFire.objects.all().count(), 1)
        self.assertEqual(models.Notification.objects.all().count(), 6)
        self.event.fire(param_name=self.category)
        self.assertEqual(models.EventNotificationFire.objects.all().count(), 2)
        self.notification.collective = True
        self.notification.save()
        PyNot.event('slug_event').fire(param_name=self.category)
        self.assertEqual(models.EventNotificationFire.objects.all().count(), 3)
        self.assertEqual(models.Notification.objects.all().count(), 17) # 6 + 6 + 5 (collective one)



class EventNotificationTestCase(DetailAPITestCaseMixin,
                                WriteRESTAPITestCaseMixin,
                                BaseRESTAPITestCase):
    base_name = 'eventnotification'
    factory_class = EventNotificationFactory
    lookup_field = 'id'
    attributes_to_check = ['id', 'name', 'subject', 'message']
    create_data = {'name' : 'Test notification',
                   'subject' : 'Test notification',
                   'message' : 'Test notification'}
    update_data = {'name': 'Test notification updated',
                   'subject': 'Test notification updated',
                   'message': 'Test notification updated',
                   'recipients': []}

    def setUp(self):
        admin=get_user_model().objects.create_superuser(
            email="admin@example.com", password="admin")
        token = Token.objects.get_or_create(user=admin)[0].key
        headers = {'HTTP_AUTHORIZATION': 'Token ' + token}
        self.client.credentials(**headers)

        super(EventNotificationTestCase, self).setUp()


    def get_create_data(self):
        data = self.create_data
        data['event']=self.object.event_id

        return data

