from django.urls import path

from blog.views.account import LoginView, AccountManageView
from blog.views.index import IndexView
from common.helper import rest_urls

urlpatterns = [
    path('account/login', LoginView.as_view()),
    *rest_urls('account/manage', AccountManageView, actions=['reset_password']),
    path('index', IndexView.as_view())
]