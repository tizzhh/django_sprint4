from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileForm
from .helpers import (CommentMixin, PostUpdateDeleteMixin,
                      ProfileRedirectMixin, select_related_all_filtered)
from .models import Category, Comment, Post, User
from blogicum.settings import PAGINATE_BY


class ProfileUpdateView(LoginRequiredMixin, ProfileRedirectMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'blog/user_form.html'

    def get_object(self):
        return self.request.user


class ProfileListView(ListView):
    template_name = 'blog/user_detail.html'
    paginate_by = PAGINATE_BY

    def get_user_obj(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        user_obj = self.get_user_obj()
        if self.request.user.username == user_obj.username:
            profile_posts = select_related_all_filtered(user_obj.posts)
        else:
            profile_posts = select_related_all_filtered(
                user_obj.posts, all_posts=False, comment_count=True
            ).order_by('-pub_date')
        return profile_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_obj()
        return context


class IndexListView(ListView):
    queryset = select_related_all_filtered(all_posts=False, comment_count=True)
    paginate_by = PAGINATE_BY
    ordering = ('-pub_date',)


class CategoryListView(ListView):
    template_name = 'blog/category_list.html'
    paginate_by = PAGINATE_BY
    # немного не понял, почему category = None - лишняя строка
    # я ведь обращаюсь к этой переменной в get_queryset
    # и в get_context_data.

    def get_category_obj(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

    def get_queryset(self):
        self.category = self.get_category_obj()
        return select_related_all_filtered(
            self.category.posts, all_posts=False, comment_count=True
        ).order_by('-pub_date')

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
        post = get_object_or_404(select_related_all_filtered(), pk=post_id)
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
