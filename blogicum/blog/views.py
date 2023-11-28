from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProfileForm
from .models import Category, Post, User


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


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    # почему-то ищет auth в auth
    template_name = 'blog/user_form.html'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )

    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    # почему-то ищет auth/user_detail.html
    template_name = 'blog/user_detail.html'
    context_object_name = 'profile'
    paginate_by = 10

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = select_related_all_filtered().filter(
            author__username=self.kwargs.get('username')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class IndexListView(ListView):
    model = Post
    queryset = select_related_all_filtered()
    paginate_by = 10


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10
    category = None

    def get_queryset(self):
        print(self.kwargs.get('category'))
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
