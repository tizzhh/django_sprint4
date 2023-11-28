from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from .forms import ProfileForm, PostForm
from .models import Category, Post, User


class RedirectMixin:
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


class ProfileUpdateView(LoginRequiredMixin, RedirectMixin, UpdateView):
    model = User
    form_class = ProfileForm
    # почему-то ищет auth в auth
    template_name = 'blog/user_form.html'

    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)


class ProfileDetailView(DetailView):
    model = User
    # почему-то ищет auth/user_detail.html
    template_name = 'blog/user_detail.html'
    context_object_name = 'profile'
    paginate_by = 10

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.username == self.kwargs.get('username'):
            context['page_obj'] = Post.objects.select_related(
                'location',
                'author',
                'category',
            ).filter(author__username=self.kwargs.get('username'))
        else:
            context['page_obj'] = select_related_all_filtered().filter(
                author__username=self.kwargs.get('username')
            )
        return context


class IndexListView(ListView):
    model = Post
    queryset = select_related_all_filtered()
    paginate_by = 10


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
        return select_related_all_filtered(self.category.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/post_form.html'

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))


class PostCreateView(LoginRequiredMixin, RedirectMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post

    def get_object(self):
        author = Post.objects.values('author__username').filter(
            id=self.kwargs.get('post_id')
        )[0]['author__username']
        if self.request.user.username == author:
            return get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return get_object_or_404(
            select_related_all_filtered(), pk=self.kwargs.get('post_id')
        )
