from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from .forms import CommentForm
from .models import Comment, Post


class PostUpdateDeleteMixin:
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author != request.user:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']},
                )
            )
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def get_object(self):
        return get_object_or_404(
            Comment, pk=self.kwargs.get('comment_id'), author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs.get('post_id')}
        )


class ProfileRedirectMixin:
    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


def select_related_all_filtered(
    model=Post.objects, all_posts=True, comment_count=False
):
    qs = model.select_related(
        'location',
        'author',
        'category',
    )
    if not all_posts:
        qs = qs.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    if comment_count:
        qs = qs.annotate(comment_count=Count('comments'))

    return qs
