# Pynot

[![pypi-version]][pypi]

**Awesome Django configurable email notification system based on events,
and exporting an API REST to configure and read notifications.**

---

# Intelligenia

Pynot is developed by Intelligenia, a software development company
focused in Python&Django + Angular SPA. More info about us in [our web page][intelligenia-web]

# Overview

Pynot is a Django library that helps with the email or web notifications. It is event oriented,
so you will define events, then you will define notifications that should be sent for each event,
and finally you can fire the events inside your application code

Pynot provides 3 main characteristics:

* Events declaration
* Definition of the notifications of each event
* Event fire system
* User notification access

**Event definition system:** Using the project settings it is possible to declare
the events that will be fired in you application. Each event should declare the type of the input
parameters it will recibe on fire, thus, each notification of this event, will use these
parameters. A parameter is a DRF Serializer, so it is not just a primitive variable,
but it will be a complex object with nested objects.

**Definition of the notifications of each event:** Pynot implement an API REST using DRF.
Using this API you could implement a front end component in your application admin area, thus
the admin user, could see the events declared in your application, and create as many notification
types in an event as required. Using the API REST it is possible to get the allowed parameters
and help the user to configure the notifications using these parameters. So, **YES**, you just
have to declare the events, and the admin will create, delete, write or change the body notifications
using a web application, increasing the happyness of both: the developer and the product owner :)

**Event fire system:** Along your application code you will fire the events declared on Pynot,
this is the best part, because **it is just one line of code** where you fire an event,
and pass it the defined parameters, and Pynot will do the magic: going throw each notification type
of the event, instantiating the variables based on the parameters passed to it, and creating the
final user notifications, sending emails and creating the web notifications.

**User notification access:** Pynot could send emails and in-app notifications. In the case of in-app
notifications, Pynot implements an API REST that gives access to the notifications of the logged user.
Therefore, your application could implement a front end area to see notification, mark them as readed,
mark them as important, and many more, it is like an email inbox. The API REST is done, you just
need to implement the front end in your application.

# Requirements

* Python (3.5, 3.6, 3.7)
* Django (2.0, 2.1)

# Installation

Install using `pip`...

    pip install pynot

Add `'pynot'` to your `INSTALLED_APPS` setting.

    INSTALLED_APPS = (
        ...
        'pynot',
    )

Pynot needs to create some database models, so you have to execute the migrations

    ./manage.py migrate

In your urls.py it is necessary to give an access point to Pynot. In this example the access
point is named `'api/pynot/'` but it is up to you.

    urlpatterns = [
        ...
        url(r'api/pynot/', include('pynot.urls')),
        ...
    ]

And thats all, Pynot is working properly, but... you don't have any defined event yet.

# Example

We are going to configure 2 events, like `'registration'` event, and a `'new_offer`' event.
To do that, we need to declare the serializers, in this case, we have the next serializers:

    muapp.serializers.UserSerializer
    muapp.serializers.OfferSerializer

Therefore we can define the events in our `'settings.py'`, taking into account that the
`'registration'` event will receive the registered user as parameter, and a `'new_offer`' event
will receive the offer and a list of users. Todo that, we have to put the next in our settings

    PYNOT_SETTINGS = {
        'my_events_category': {
            'name': _('My Events Category Name'),
            'events': {
                'registration': {
                    'name': _("New registration"),
                    'description': _("Event fired when new registration happens"),
                    'parameters': {
                        'user': {'human_name': _("User"), 'serializer': 'myapp.serializers.UserSerializer'}
                    }
                },
                'new_offer': {
                    'name': _("New offer"),
                    'description': _("Event fired when new offers are published"),
                    'parameters': {
                        'offer': {'human_name': _("Offer"), 'serializer': 'myapp.serializers.OfferSerializer'}
                        'users': {'human_name': _("Users"), 'serializer': 'myapp.serializers.UserSerializer'}
                    }
                }
            }
        }
    }

With that deffinition is enough to have an API REST allowing the product owner to define the
required notifications, like the next:

* When a new registration occurs, 2 emails have to be sended, one to the user, and another one to
the company
* When a new offer is published, each user will receive an email and an in-app notification
with the offer


[pypi-version]: https://img.shields.io/pypi/v/pynot.svg
[pypi]: https://pypi.org/project/pynot/
[intelligenia-web]: https://www.intelligenia.us