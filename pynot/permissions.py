from rest_framework.permissions import BasePermission


class IsNotificationOwner(BasePermission):
	"""
	Allows access only to notification owner
	"""

	def has_object_permission(self, request, view, obj):
		return obj.users.filter(user=request.user).exists()