from rest_framework.viewsets import ModelViewSet


class BaseSchoolViewSet(ModelViewSet):
    model = None

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()

        user = self.request.user

        if not user.is_authenticated or not hasattr(user, "counselor"):
            return self.model.objects.none()

        school = user.counselor.school

        return self.model.objects.filter(school=school)
