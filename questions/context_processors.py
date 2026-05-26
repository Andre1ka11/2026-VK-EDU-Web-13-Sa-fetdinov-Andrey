from django.db.models import Count
from .models import Tag
from core.models import Profile


def sidebar(request):
    popular_tags = (
        Tag.objects.annotate(q_count=Count('question'))
        .filter(q_count__gt=0)
        .order_by('-q_count')[:10]
    )
    top_users = (
        Profile.objects.select_related('user')
        .order_by('-rating')[:5]
    )
    return {
        'popular_tags': popular_tags,
        'top_users': top_users,
    }
