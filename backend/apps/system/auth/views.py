from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from common.responses.response import success_response, error_response
from apps.system.users.serializers import UserSerializer
from apps.system.menu.serializers import MenuSerializer
from apps.system.permission.serializers import PermissionSerializer
from apps.system.rbac.serializers import RoleDataScopeSerializer
from .serializers import LoginSerializer
from .services import AuthService

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AuthService.login_user(
            serializer.validated_data["username"],
            serializer.validated_data["password"],
        )
        if not user:
            return error_response(message="用户名或密码错误", code=400, status=400)
        token_data = AuthService.build_token_payload(user)
        return success_response({
            "username": user.username,
            "access": token_data["access"],
            "refresh": token_data["refresh"],
        }, message="login success")

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return success_response(message="logout success")

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(UserSerializer(request.user).data)

class MyMenusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        menus = AuthService.get_user_menus(request.user)
        return success_response(MenuSerializer(menus, many=True).data)

class MyPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = AuthService.get_user_permissions(request.user)
        return success_response(PermissionSerializer(permissions, many=True).data)

class MyDataScopesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scopes = AuthService.get_user_data_scopes(request.user)
        return success_response(RoleDataScopeSerializer(scopes, many=True).data)

class SessionInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(AuthService.build_session_info(request.user))

class RefreshTokenApiView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.validated_data, message="refresh success")
