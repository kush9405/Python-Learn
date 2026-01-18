from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer

import logging
logger = logging.getLogger('accounts')

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] # Anyone can sign up
    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"New user registered: {user.username} (ID: {user.id})")


