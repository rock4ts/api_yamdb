from rest_framework import viewsets

from api_yamdb.settings import admin_methods, moderator_methods
from .permissions import IsAdminOrSuperUser, IsModeratorOrAdminOrOwner


class AdminViewMixin(viewsets.GenericViewSet):
    """
    Generic viewset class that sets Admin level restrictions for
    'POST', 'PATCH', 'PUT' and 'DELETE' methods.
    """

    restricted_methods = admin_methods
    current_permission_class = IsAdminOrSuperUser

    def get_permissions(self):
        if self.request.method in self.restricted_methods:
            self.permission_classes = (self.current_permission_class,)
        return super().get_permissions()


class ModeratorViewMixin(AdminViewMixin):
    """
    Generic viewset class that sets Moderator/Owner level restrictions for
    'PATCH', 'PUT' and 'DELETE' methods.
    """

    restricted_methods = moderator_methods
    current_permission_class = IsModeratorOrAdminOrOwner
