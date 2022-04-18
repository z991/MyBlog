from blog.models.account import MSAccount
from common.auth.authentication import UserTokenAuthentication as _Base


class UserTokenAuthentication(_Base):
    user_model = MSAccount
