from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.utils import timezone

from .models import Category, Post

INDEX_POSTS_LIMIT = 5


def select_related_all_filtered(model=Post.objects):
    return model.select_related(
        'location',
        'author',
        'category',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


class IndexListView(ListView):
    model = Post
    queryset = Post.objects.select_related(
        'location',
        'author',
        'category'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    ordering = '-pub_date'
    paginate_by = 10

# def index(request):
#     post_list = select_related_all_filtered()[:INDEX_POSTS_LIMIT]
#     return render(request, 'blog/index.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(
        select_related_all_filtered(),
        pk=post_id,
    )
    return render(
        request,
        'blog/detail.html',
        {'post': post},
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = select_related_all_filtered(category.posts)
    return render(
        request,
        'blog/category.html',
        {
            'post_list': post_list,
            'category': category,
        },
    )
