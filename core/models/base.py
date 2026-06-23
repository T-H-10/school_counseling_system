from django.db import models
from django.utils import timezone


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        if self.deleted_at:
            return
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class BaseQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)


class BaseManager(models.Manager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).alive()


class BaseModel(SoftDeleteModel):
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BaseManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
