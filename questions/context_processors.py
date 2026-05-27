from django.core.cache import cache
from django.db.models import Count
from .models import Tag
from .tasks import (
    POPULAR_TAGS_CACHE_KEY,
    BEST_MEMBERS_CACHE_KEY,
    update_popular_tags,
    update_best_members,
)


def _get_popular_tags():
    data = cache.get(POPULAR_TAGS_CACHE_KEY)
    if data is not None:
        return data
    # fallback: считаем из БД и кладём в кеш
    update_popular_tags()
    return cache.get(POPULAR_TAGS_CACHE_KEY) or []


def _get_best_members():
    data = cache.get(BEST_MEMBERS_CACHE_KEY)
    if data is not None:
        return data
    update_best_members()
    return cache.get(BEST_MEMBERS_CACHE_KEY) or []


def sidebar(request):
    return {
        'popular_tags': _get_popular_tags(),
        'top_users': _get_best_members(),
    }
