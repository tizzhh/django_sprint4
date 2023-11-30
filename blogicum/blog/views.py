from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post, User


class CommentMixin:
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


class ProfileUpdateView(LoginRequiredMixin, ProfileRedirectMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user_form.html'

    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/user_detail.html'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.username == self.kwargs.get('username'):
            profile_posts = Post.objects.select_related(
                'location',
                'author',
                'category',
            )
        else:
            profile_posts = select_related_all_filtered()
        profile_posts = (
            profile_posts.filter(author__username=self.kwargs.get('username'))
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )
        return profile_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs.get('username')
        )
        return context


class IndexListView(ListView):
    model = Post
    queryset = select_related_all_filtered().annotate(
        comment_count=Count('comments')
    )
    paginate_by = 10
    ordering = ['-pub_date']


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category_list.html'
    paginate_by = 10
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True,
        )
        return (
            select_related_all_filtered(self.category.posts)
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/post_form.html'

    def get_object(self):
        return get_object_or_404(
            Post, pk=self.kwargs.get('post_id'), author=self.request.user
        )


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm

    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs.get('post_id'))

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs.get('post_id')},
                )
            )
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, ProfileRedirectMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        author = (
            Post.objects.values('author__username').filter(pk=post_id).first()
        )
        if author and self.request.user.username == author['author__username']:
            return get_object_or_404(Post, pk=post_id)
        return get_object_or_404(select_related_all_filtered(), pk=post_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    comment_post = None

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.comment_post
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.comment_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.comment_post.id}
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    model = Comment
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_form.html'
