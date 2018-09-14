# -*- coding: utf-8 -*-
"""
Urls API
"""
from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryView)
router.register(r'events', views.EventView)
router.register(r'eventnotifications', views.EventNotificationView)
router.register(r'notifications', views.NotificationView)

urlpatterns = [
	url(r'^', include(router.urls)),
]
