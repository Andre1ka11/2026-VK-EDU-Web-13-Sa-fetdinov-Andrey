import uuid
import os
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


def avatar_upload_path(instance, filename):
    from django.utils import timezone
    ext = os.path.splitext(filename)[1].lower()
    today = timezone.now().strftime('%Y/%m/%d')
    return f'avatars/{today}/{uuid.uuid4().hex}{ext}'


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path, blank=True, null=True, verbose_name='Аватар'
    )
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Нужен для того, чтобы Profile.save() вызывался при каждом сохранении User
# (например, при изменении email или username через форму профиля).
# Без этого сигнала profile.save() нужно вызывать вручную в каждом месте.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
