from django.urls import path
from .views import LoginView, LogoutView, MeView, MyMenusView, MyPermissionsView, MyDataScopesView, SessionInfoView, RefreshTokenApiView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("my-menus/", MyMenusView.as_view(), name="auth-my-menus"),
    path("my-permissions/", MyPermissionsView.as_view(), name="auth-my-permissions"),
    path("my-data-scopes/", MyDataScopesView.as_view(), name="auth-my-data-scopes"),
    path("session-info/", SessionInfoView.as_view(), name="auth-session-info"),
    path("refresh-token/", RefreshTokenApiView.as_view(), name="auth-refresh-token"),
]
