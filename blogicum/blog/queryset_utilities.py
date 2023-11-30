from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_posts(model=Post.objects, only_published=False, comment_count=False):
    qs = model.select_related(
        'location',
        'author',
        'category',
    )
    if only_published:
        qs = qs.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    if comment_count:
        qs = qs.annotate(comment_count=Count('comments')).order_by('-pub_date')

    return qs
