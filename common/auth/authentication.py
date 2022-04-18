from rest_framework import authentication

from common.models.user import BaseUser


class UserTokenAuthentication(authentication.BaseAuthentication):

    user_model = BaseUser

    def authenticate(self, request):
        token = request.headers.get('authorization', '')
        if not token.startswith('Bearer '):
            # Unsupported authorization method
            return None, None
        token = token[7:]
        user = self.user_model.get_user_by_token(token)
        return user, None
