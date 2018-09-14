# coding=utf-8
from celery import shared_task
from .utils.util_email import send_email

@shared_task(bind=True, name='pynot.tasks.send_email')
def send_email(self, not_id):
    """
    Marca el Order como "fallido"
    :param self: task  tarea celery
    :param order_id: int  id del Order
    :return: void
    """

    print( "pynot.tasks.send_email: not_id={0}. Retry={1}".format(not_id, self.request.retries))

    # Importar modelos dentro de la función que se va a encolar para evitar dependencias circulares
    from pynot.models import Notification, Config

    try:
        print("pynot.tasks.send_email (not_id={0}): Notification.objects.get".format(not_id))
        notification = Notification.objects.get(pk=not_id)
        if notification.type=='email' and notification.status=='pending':
            print("pynot.tasks.send_email (not_id={0}): email and pending".format(not_id))
            notification_fire = notification.notification
            subject = notification_fire.subject
            message = notification_fire.message
            print("pynot.tasks.send_email (not_id={0}): send_email".format(not_id))
            send_email(to_email=notification.recipient,
                       subject=subject,
                       template=Config.load().email_template,
                       context={'message':message},
                       smtp_config_name='pynot')
            print("pynot.tasks.send_email (not_id={0}): sended".format(not_id))
            notification.status='completed'
            notification.save()
            print("pynot.tasks.send_email (not_id={0}): status completed".format(not_id))

        print("pynot.tasks.send_email (not_id={0}): END".format(not_id))

    except Exception as e:
        print("pynot.tasks.send_email (not_id={0}): Exception({1})".format(not_id, e))
        self.retry(countdown=10, max_retries=120, exc=Exception())
