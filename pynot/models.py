# -*- coding: utf-8 -*-
"""
Notifications models
"""
from __future__ import unicode_literals
import json
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings

from . import tasks

class SingletonModel(models.Model):
	"""
	Modelo Singleton
	"""
	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		"""
		Sólo tendrá una tupla
		:param args:
		:param kwargs:
		:return:
		"""
		self.pk = 1
		super(SingletonModel, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		"""
		No se puede eliminar
		:param args:
		:param kwargs:
		:return:
		"""
		pass

	@classmethod
	def load(cls):
		"""
		Carga la instancia, como método de clase
		:return:
		"""
		obj, created = cls.objects.get_or_create(pk=1)
		return obj

NOTIFICATION_STATUS_TYPE = (
    ("pending", _("Pendiente")),
    ("in_process", _("Procesando")),
    ("complete", _("Completado")),
    ("error", _("Error")),
)

RECIPIENT_TYPE = (
    ("email", _("Correo electrónico")),
    ("user", _("Usuario")),
    ("group", _("Grupo")),
)

class CommonModelManager(models.Manager):
    """
    Obtiene el listado de elementos que no han sido eliminados
    """

    def get_queryset(self):
        """
        Sólo las instancias que no estén borradas
        """
        return super(CommonModelManager, self)\
            .get_queryset().filter(is_erased=False)


class CommonModel(models.Model):
    """
    Modelo abstracto para entidades del sistema que soporten borrado lógico
    """

    class Meta(object):
        """
        Metainformación sobre el modelo común
        """
        abstract = True
        ordering = ['creation_datetime']

    ## Fecha de creación del objeto
    creation_datetime = models.DateTimeField(
        verbose_name=_("Fecha de creación del objeto"), default=timezone.now)

    ## Fecha de última actualización del objeto
    last_update_datetime = models.DateTimeField(
        verbose_name=_("Fecha de última actualización del objeto"))

    is_erased = models.BooleanField(
        default=False,
        verbose_name=_("¿Borrado?"),
        help_text=_("Si lo marca se borrará el elemento."))

    ## Obtiene los objetos obviando los eliminados. Es el manager por defecto
    objects = CommonModelManager()

    ## Para consultar los objetos eliminados
    all_objects = models.Manager()

    def update(self, **kwargs):
        """
        Actualiza tanto a nivel de base de datos como a nivel de objeto
        los datos que se le pasan como parámetros
        :param kwargs:
        """
        self.__class__.objects.filter(id=self.id).update(**kwargs)
        for key in kwargs.keys():
            self.set_attribute(key, kwargs[key])

    def save(self, *args, **kwargs):
        """
        Guarda el objeto en BD, en realidad lo único que hace es actualizar
        los datetimes.
        El datetime de actualización se actualiza siempre,
        el de creación sólo al guardar de nuevas.
        :param kwargs:
        :param args:
        """
        # Datetime con el momento actual en UTC
        now_datetime = timezone.now()
        # El datetime de actualización es la fecha actual
        self.last_update_datetime = now_datetime
        # Llamada al constructor del padre
        super(CommonModel, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Casting a unicode
        :return:
        """
        return "{0}".format(self.id)

    def get_class(self):
        """
        Obtiene el objeto class del objeto actual
        :return:
        """
        return self.__class__

    def get_class_name(self):
        """
        Obtiene el nombre de la clase del objeto actual
        :return:
        """
        return self.__class__.__name__

    def get_attribute(self, field):
        """
        Obtiene un atributo del objeto actual
        :param field:
        :return:
        """
        return self.__getattribute__(field)

    def set_attribute(self, field, value):
        """
        Establece un atributo del objeto actual
        :param field:
        :param value:
        :return:
        """
        return self.__setattr__(field, value)

    def has_attribute(self, field):
        """
        Informa si el objeto tiene un atributo
        :param field:
        :return:
        """
        return field in self.__dict__

    def get_as_dict(self):
        """
        Obtiene los atributos del objeto como diccionario
        :return:
        """
        return self.__dict__

    def meta(self):
        """
        Obtiene la metainformación de objetos de este modelo
        :return:
        """
        return self._meta

    def delete(self, *args, **kwargs):
        """
        Ejecuta el borrado lógico de esta entidad
        """
        self.is_erased = True
        self.save()

    def delete_from_db(self):
        """
        Ejecuta el borrado en base de datos
        """
        super(CommonModel, self).delete(using=None)

    def local_creation_datetime(self):
        """
        Obtiene la fecha y hora de creación local
        :return:
        """
        return timezone.localtime(self.creation_datetime)

    def local_last_update_datetime(self):
        """
        Obtiene la fecha y hora de última actualización local
        :return:
        """
        return timezone.localtime(self.last_update_datetime)

    def is_related_to(self, user):
        """
        Tiene permiso sobre este objeto el usuario
        :param user: usuario
        :return:
        """
        return False

    @classmethod
    def get_table_name(cls):
        """
        Obtiene el nombre de la tabla asociada al modelo
        :return:
        """
        return cls._meta.db_table

    @classmethod
    def get_all_field_names(cls):
        """
        Obtiene los nombres de los campos de un modelo dado
        :return:
        """
        return [f.name for f in cls._meta.get_fields()]

    @classmethod
    def get_all_field_names_verbose(cls):
        """
        Obtiene los nombres de los campos de un modelo dado
        :return:
        """
        fields = {}
        for f in cls._meta.get_fields():
            if hasattr(f, 'verbose_name'):
                fields[f.name] = "{} ({})".format(f.verbose_name,
                                                cls._meta.verbose_name.title())
        return fields


def get_class(class_name):
    parts = class_name.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


class Config(SingletonModel):
    email_template = models.TextField(_("Email template"), default="{{ message }}")


class PyNot(object):
    @classmethod
    def sync_settings(cls):
        for category_slug in settings.PYNOT_SETTINGS:
            category, created = Category.objects.get_or_create(slug=category_slug)
            new_name = settings.PYNOT_SETTINGS[category_slug]["name"]
            if category.name != new_name:
                category.name = new_name
                category.save()

            event_config = settings.PYNOT_SETTINGS[category_slug]["events"]
            for event_slug in event_config:
                event, created = Event.objects.get_or_create(
                    category=category,
                    slug=event_slug
                )
                new_name = event_config[event_slug]["name"]
                new_description = event_config[event_slug]["description"]
                if event.name!=new_name or event.description!=new_description:
                    event.name = new_name
                    event.description = new_description
                    event.save()

                parameters_config = event_config[event_slug]["parameters"]
                for parameter_slug in parameters_config:
                    parameter, created = Parameter.objects.get_or_create(
                        name=parameter_slug,
                        event=event
                    )
                    new_name = parameters_config[parameter_slug]["human_name"]
                    new_serializer = parameters_config[parameter_slug]["serializer"]
                    if parameter.name != new_name or parameter.description != new_description:
                        parameter.human_name = new_name
                        parameter.serializer = new_serializer
                        parameter.save()

    @classmethod
    def event(cls, slug):
        if not Event.objects.filter(slug=slug).exists():
            cls.sync_settings()
        if not Event.objects.filter(slug=slug).exists():
            raise Exception(_("No existe ningún evento con el slug indicado: ")+slug)

        return Event.objects.get(slug=slug)

class Category(CommonModel):
    """
    Notification Category
    """
    ## Slug
    slug = models.CharField(max_length=128, unique=True)

    ## Category name
    name = models.CharField(max_length=128, default=slug)


class Event(CommonModel):
    """
    Notification Event
    """

    ## Slug
    slug = models.CharField(max_length=128, unique=True)

    ## Event name
    name = models.CharField(max_length=128, default=slug)

    ## Event name
    description = models.TextField(default="")

    ## Event category
    category = models.ForeignKey(Category,
                                 on_delete=models.PROTECT,
                                 related_name="events")

    @staticmethod
    def expand_params(params, prefix=""):
        expanded={}
        for field in params:
            if isinstance(params[field], dict):
                ## if this field is a dict, we need to expand it
                expanded = dict(expanded, **Event.expand_params(params[field],
                                                          prefix + field + "."))
            elif isinstance(params[field], list):
                ## if this field is a list, we need to join each item
                expanded_list = None
                for data in params[field]:
                    if isinstance(data, dict):
                        expanded_item = Event.expand_params(data,
                                                        prefix + field + ".")
                        ## as we going to join the items, we need each item has to
                        ## be a tuple
                        for param in expanded_item:
                            if not isinstance(expanded_item[param], tuple):
                                expanded_item[param] = (expanded_item[param],)

                        if expanded_list is None:
                            expanded_list = expanded_item
                        else:
                            for param in expanded_list:
                                expanded_list[param] = expanded_list[param] + \
                                                       expanded_item[param]
                if expanded_list:
                    expanded = dict(expanded, **expanded_list)
            else:
                expanded[prefix + field]=params[field].__str__()

        return expanded

    def fire(self, **kwargs):
        data = {}
        for param in self.parameters.all():
            if param.name not in kwargs:
                raise Exception("The event {} needs a serializer param named {}"
                                .format(self.name, param.name))

            if isinstance(kwargs[param.name], models.Model):
                kwargs[param.name] = get_class(param.serializer)(kwargs[param.name])

            data[param.name]=json.loads(json.dumps(kwargs[param.name].data))

        expanded = Event.expand_params(data)

        ## Fire each event notification passing the expanded parameters
        for notification in self.notifications.all():
            notification.fire(expanded)
        return True


class Parameter(CommonModel):
    """
    Notification Event Parameter
    """
    ## Parameter name
    name = models.CharField(max_length=128)

    ## Human name
    human_name = models.CharField(max_length=128, default=name)

    ## Serializer needed to this parameter
    serializer = models.TextField(default='')

    ## Parameter event
    event = models.ForeignKey(Event,
                              on_delete=models.PROTECT,
                              related_name="parameters")

    @staticmethod
    def get_schema(serializer, obj_type):
        fields = serializer.get_fields()

        data = {}
        for field in fields:
            data_field = {"human_name": field}

            if hasattr(serializer.Meta, 'extra_fields_human_name') and \
                    field in serializer.Meta.extra_fields_human_name:
                data_field = {"human_name":
                                serializer.Meta.extra_fields_human_name[field]}

            exclude_field = False

            if type(fields[field]).__name__ == "ListSerializer":
                if obj_type=='body':
                    exclude_field = True
                else:
                    data_field["data"] = \
                        Parameter.get_schema(fields[field].child, obj_type)
                    if len(data_field["data"]) == 0:
                        exclude_field = True
            elif hasattr(fields[field], "get_fields"):
                data_field["data"] = \
                    Parameter.get_schema(fields[field], obj_type)
                if len(data_field["data"]) == 0:
                    exclude_field = True
            elif obj_type == 'email':
                if type(fields[field]).__name__ != 'EmailField' and \
                        (not hasattr(serializer.Meta, 'extra_fields_email')
                        or not field in serializer.Meta.extra_fields_email):
                    exclude_field = True
            elif obj_type == 'user':
                if not hasattr(serializer.Meta, 'extra_fields_user') \
                        or not field in serializer.Meta.extra_fields_user:
                    exclude_field = True
            elif obj_type == 'group':
                if not hasattr(serializer.Meta, 'extra_fields_group') \
                        or not field in serializer.Meta.extra_fields_group:
                    exclude_field = True
            elif obj_type == 'file':
                if not hasattr(serializer.Meta, 'extra_fields_file') \
                        or not field in serializer.Meta.extra_fields_file:
                    exclude_field = True

            if not exclude_field:
                data[field] = data_field

        return data

    @property
    def data_body(self):
        return Parameter.get_schema(get_class(self.serializer)(), 'body')

    @property
    def data_email(self):
        return Parameter.get_schema(get_class(self.serializer)(), 'email')

    @property
    def data_user(self):
        return Parameter.get_schema(get_class(self.serializer)(), 'user')

    @property
    def data_group(self):
        return Parameter.get_schema(get_class(self.serializer)(), 'group')

    @property
    def data_file(self):
        return Parameter.get_schema(get_class(self.serializer)(), 'file')


class EventNotification(CommonModel):
    """
    Notification linked to an event
    """
    ## Notification name
    name = models.CharField(max_length=128)

    ## Notification description
    description = models.TextField(default="")

    ## Notification type
    type = models.CharField(max_length=128, default="email")

    ## Collective notification
    collective = models.BooleanField(
        default=False,
        verbose_name=_("Collective notification"),
        help_text=_("Every user recipient is owner of the same notification."))

    ## Event
    event = models.ForeignKey(Event,
                                 on_delete=models.PROTECT,
                                 related_name="notifications")

    ## Subject
    subject = models.TextField(default='')

    ## Message
    message = models.TextField()

    def fire(self, data):
        subject = self.subject
        message = self.message
        recipient_emails = ()
        recipient_users = ()
        recipient_groups = ()
        files = ()

        for field in data:
            if not isinstance(data[field], tuple):
                subject = subject.replace(field, data[field])
                message = message.replace(field, data[field])

        for recipient in self.recipients.all():
            found = False
            for field in data:
                if recipient.recipient == field:
                    found = True
                    if not isinstance(data[field], tuple):
                        recipient_list = (data[field], )
                    else:
                        recipient_list = data[field]

                    if recipient.type == "email":
                        recipient_emails = recipient_emails + recipient_list
                    elif recipient.type == "user":
                        recipient_users = recipient_users + recipient_list
                    elif recipient.type == "group":
                        recipient_groups = recipient_groups + recipient_list

            if not found and recipient.recipient.find("@"):
                if recipient.type == "email":
                    recipient_emails = recipient_emails + (recipient.recipient, )

        for file in self.files.all():
            for field in data:
                if file.file == field:
                    if not isinstance(data[field], tuple):
                        files_list = (data[field], )
                    else:
                        files_list = data[field]

                    files = files + files_list

        ## Here we have completed message, recipient_emails, recipient_users and
        ## recipient_groups
        fire = EventNotificationFire.objects.create(event_notification=self,
                                    subject=subject,
                                    message=message)

        for file in files:
            EventNotificationFireFile.objects.create(path=file, fire=fire)

        for email in recipient_emails:
            notification = Notification.objects.create(notification=fire,
                                        recipient=email,
                                        type='email')

            tasks.send_email.delay(notification.id)

        for group in recipient_groups:
            users = get_user_model().objects.filter(groups__id=group)\
                .values_list('id', flat=True)
            recipient_users = recipient_users + tuple(users)

        if self.collective:
            # We add every recipient as aowner of the same notification
            notification = Notification.objects.create(notification=fire,
                                                       status='complete')
            notification.users.add(recipient_users)
        else:
            # each recipient has a single notification
            for user in recipient_users:
                notification = Notification.objects.create(notification=fire,
                                                           status='complete')
                notification.users.add(user)


class EventNotificationRecipient(CommonModel):

    ## String representing the recipient
    recipient = models.CharField(max_length=256)

    ## Type of the recipient
    type = models.CharField(max_length=64, choices=RECIPIENT_TYPE)

    ## Related notification
    notification = models.ForeignKey(EventNotification,
                              on_delete=models.CASCADE,
                              related_name="recipients")


class EventNotificationFile(CommonModel):

    ## String representing the file
    file = models.CharField(max_length=256)

    ## Related notification
    notification = models.ForeignKey(EventNotification,
                              on_delete=models.CASCADE,
                              related_name="files")


class EventNotificationFire(CommonModel):
    ## Related event notification
    event_notification = models.ForeignKey(EventNotification,
                                           on_delete=models.CASCADE,
                                           related_name="fires")

    ## Subject
    subject = models.TextField(default='')

    ## Message
    message = models.TextField()


class EventNotificationFireFile(CommonModel):

    ## String representing the file
    path = models.CharField(_("path"), max_length=1024)

    ## Related notification
    fire = models.ForeignKey(EventNotificationFire,
                              on_delete=models.CASCADE,
                              related_name="files")


class Notification(CommonModel):
    ## Related event notification
    notification = models.ForeignKey(EventNotificationFire,
                                     on_delete=models.CASCADE,
                                     related_name="notifications", default=1)

    ## String representing the recipient, when the recipient is not an user
    recipient = models.CharField(max_length=256,
                                 null=True,
                                 default=None)

    ## Type of the recipient, when the recipient is not an user
    type = models.CharField(max_length=64,
                            choices=RECIPIENT_TYPE,
                            null=True,
                            default=None)

    ## Related user
    users = models.ManyToManyField(get_user_model(),
                             related_name="notifications")

    ## Status
    status = models.CharField(max_length=64,
                              choices=NOTIFICATION_STATUS_TYPE,
                              default='pending')

    ## Reading status
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Has been read"),
        help_text=_("The notification has been read."))

    ## Important notification
    is_important = models.BooleanField(
        default=False,
        verbose_name=_("Is important"),
        help_text=_("The notification is important."))