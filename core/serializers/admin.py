from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from core.models import ClassLevel, Counselor, School, SchoolYear


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        # The client derives its user object from the token alone (no
        # localStorage), so the username must travel in the claims.
        token["username"] = user.username
        # Lets the client tell a pure admin (is_staff, no Counselor row) apart
        # from a hybrid admin+counselor user, who should see both nav areas.
        token["has_counselor"] = hasattr(user, "counselor")
        return token


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    """Reads the refresh token from the httpOnly cookie, with body fallback."""

    refresh = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        from core.views.auth import REFRESH_COOKIE

        request = self.context["request"]
        attrs["refresh"] = attrs.get("refresh") or request.COOKIES.get(REFRESH_COOKIE, "")
        if not attrs["refresh"]:
            raise InvalidToken("לא נמצא טוקן רענון")
        return super().validate(attrs)


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"
        read_only_fields = ["created_at"]


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = "__all__"


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = "__all__"
        # The unique_active_school_year partial DB constraint is enforced
        # atomically by SchoolYearService.activate_year(). DRF 3.17+ auto-
        # generates a field-level UniqueValidator from it which would reject
        # valid activation requests before the service even runs — suppress it.
        extra_kwargs = {"is_active": {"validators": []}}


class CounselorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Counselor
        fields = ["id", "username", "password", "full_name", "school", "created_at"]
        read_only_fields = ["created_at"]


class ArchiveEntrySerializer(serializers.Serializer):
    """Uniform shape for a soft-deleted row of any of the 5 archivable
    entities — ArchiveService.serialize_list/serialize_one build the dicts
    this renders, since the 5 underlying models have no shared base
    serializer (a ModelSerializer wouldn't work across heterogeneous models).
    """

    id = serializers.IntegerField()
    entity_type = serializers.CharField()
    display_label = serializers.CharField()
    school_name = serializers.CharField()
    deleted_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    is_restorable = serializers.BooleanField()
    blocked_reason = serializers.CharField(allow_null=True)
