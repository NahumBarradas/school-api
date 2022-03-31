from rest_framework import status, authentication, exceptions
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import get_authorization_header

from apps.users.authentication import ExpiringTokenAuthentication

class Authentication(authentication.Authentication):
    user = None

    def get_user(self, request):
        """
        Return:
            * user       : User Instance or
            * Message    : Error Message or
            * None       : Corrupt Token
        """
        token  = get_authorization_header(request).split()
        if token:
            try:
                token = token[1].decode()
            except:
                return None

            token_expire = ExpiringTokenAuthentication()
            user = token_expire.authenticate_credentials(token)

            if user != None:
                self.user = user
                return user