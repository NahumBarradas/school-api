from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class ExpiringTokenAuthentication(TokenAuthentication):
    def expires_in(self, token):
        # Regresa el tiempo restante del token
        time_elapsed = timezone.now() - token.created
        left_time = timedelta(seconds = settings.Token_EXPIRED_AFTER_SECONDS) - time_elapsed
        return left_time

    def is_token_expired(self, token):
        # Regresa si es que el token sigue activo o expirado
        return self.expires_in(token) < timedelta(seconds = 0)

    def token_expire_handler(self, token):
        """
        Return
            * is_expired    : True si el token está activo, False si está expirado
            * token         : token nuevo o actual
        """
        is_expired = self.is_token_expired(token)
        if is_expired:
            user = token.user
            token.delete()
            token = self.get_model().objects.create(user = user)

        return token

    def authenticate_credentials(self, key):
        """
        Return
        * user      : Instancia de usuario que hace la petición
        * token     : token actual o nueva para el usuario
        * message   : Mensaje de error
        * expired   : True si el token sigue activo o False si ya expiró
        """
        user = None
        try:
            token = self.get_model().objects.select_related('user').get(key = key)
            token = self.token_expire_handler(token)
            user = token.user
        except self.get_model().DoesNotExist:
            pass

        return user