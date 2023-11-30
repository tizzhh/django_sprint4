from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, CustomUserForm, PostForm, ProfileForm
from .mixins import CommentMixin, PostUpdateDeleteMixin, ProfileRedirectMixin
from .models import Category, Comment, Post, User
from .queryset_utilities import get_posts


class ProfileUpdateView(LoginRequiredMixin, ProfileRedirectMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'blog/user_form.html'

    def get_object(self):
        return self.request.user


class ProfileListView(ListView):
    template_name = 'blog/user_detail.html'
    paginate_by = settings.PAGINATE_BY

    def get_user_obj(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        user_obj = self.get_user_obj()
        if self.request.user.username == user_obj.username:
            profile_posts = get_posts(user_obj.posts, comment_count=True)
        else:
            profile_posts = get_posts(
                user_obj.posts, only_published=True, comment_count=True
            )
        return profile_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_obj()
        return context


class IndexListView(ListView):
    queryset = get_posts(only_published=True, comment_count=True)
    paginate_by = settings.PAGINATE_BY
    ordering = ('-pub_date',)


class CategoryListView(ListView):
    template_name = 'blog/category_list.html'
    paginate_by = settings.PAGINATE_BY
    # неправильно сформулировал вопрос про category = None
    # у меня же нет такого аттрибута класса,
    # поэтому я решил его задать, ведь
    # на 70 строчке я его менял, хотя он не объявлен.
    # вот что мне не очень понятно.
    # Как я понял, питон позволяет создавать
    # дополнительные аттрибуты при вызове методов.

    def get_category_obj(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

    def get_queryset(self):
        category = self.get_category_obj()
        return get_posts(
            category.posts, only_published=True, comment_count=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category_obj()
        return context


class PostDeleteView(LoginRequiredMixin, PostUpdateDeleteMixin, DeleteView):
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/post_form.html'


class PostUpdateView(PostUpdateDeleteMixin, UpdateView):
    form_class = PostForm


class PostCreateView(LoginRequiredMixin, ProfileRedirectMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    def get_object(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(get_posts(), pk=post_id)
        if self.request.user != post.author and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()
        ):
            raise Http404
        return post

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
    ...


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    ...


class AuthUserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserForm
    success_url = reverse_lazy('blog:index')
