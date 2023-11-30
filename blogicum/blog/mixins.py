from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .forms import CommentForm
from .models import Comment, Post


class PostUpdateDeleteMixin:
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != request.user:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': post.id},
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
