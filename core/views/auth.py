"""Cookie-based JWT auth: the refresh token lives in an httpOnly cookie.

The access token is returned in the response body (kept in frontend memory
only); the refresh token never reaches JavaScript. The cookie is scoped to
the auth path (``settings.REFRESH_COOKIE_PATH`` — ``/token`` in dev,
``/api/token`` behind the production proxy) so the browser sends it only to
the auth endpoints (refresh, logout) and it stays off every other request.
"""

from django.conf import settings
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.serializers.admin import CookieTokenRefreshSerializer, CustomTokenObtainPairSerializer

REFRESH_COOKIE = "refresh_token"


def _set_refresh_cookie(response, token):
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        max_age=int(jwt_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
        httponly=True,
        # Cloud is DEBUG=False behind HTTPS -> Secure. Desktop/hybrid may also
        # run with DEBUG=False but serve loopback HTTP with no TLS, where a
        # Secure cookie would never be sent back — settings.SECURE_COOKIES
        # accounts for that (see config/settings.py).
        secure=settings.SECURE_COOKIES,
        samesite="Lax",
        path=settings.REFRESH_COOKIE_PATH,
    )


def _move_refresh_to_cookie(response):
    """Strip the refresh token from the JSON body and set it as a cookie."""
    refresh = response.data.pop("refresh", None)
    if refresh:
        _set_refresh_cookie(response, refresh)
    return response


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        return _move_refresh_to_cookie(super().post(request, *args, **kwargs))


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "token_refresh"

    def post(self, request, *args, **kwargs):
        # Rotation puts a new refresh token in the body; move it to the cookie.
        return _move_refresh_to_cookie(super().post(request, *args, **kwargs))


class LogoutView(APIView):
    """Blacklist the refresh token and tell the browser to drop the cookie.

    No authentication required: the access token may already be expired when
    the user logs out, and the refresh token itself is the credential being
    revoked. A cross-site POST can't reach the victim's cookie (SameSite=Lax),
    so the worst an attacker can do here is log themselves out.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        token = request.COOKIES.get(REFRESH_COOKIE) or request.data.get("refresh")
        if token:
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                pass  # already expired/blacklisted — nothing left to revoke
        response = Response({"detail": "התנתקת בהצלחה"})
        response.delete_cookie(REFRESH_COOKIE, path=settings.REFRESH_COOKIE_PATH)
        return response
