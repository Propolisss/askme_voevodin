from app.models import Tag, Profile
from django.core.cache import cache


def common_context(request):
    tags = cache.get('tags')
    members = cache.get('members')

    return {
        'tags': tags,
        'members': members
    }
