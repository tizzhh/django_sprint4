from django.contrib import admin
from django.db.models import Count

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'text',
        'created_at',
        'author',
    )
    list_editable = ('text',)
    search_fields = ('post__title',)
    list_filter = (
        'created_at',
        'author',
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        'description',
        'slug',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = (
        'created_at',
        'is_published',
    )
    inlines = (PostInline,)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = (
        'created_at',
        'is_published',
    )
    inlines = (PostInline,)


class PostAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(comment_count=Count('comments'))

    def comment_count(self, instance):
        return instance.comment_count

    comment_count.short_description = 'Количество комментариев'

    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
        'comment_count',
    )
    list_editable = (
        'is_published',
        'category',
    )
    search_fields = ('title',)
    list_filter = (
        'category',
        'author',
        'created_at',
        'location',
        'is_published',
    )
    inlines = (CommentInline,)


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Comment, CommentAdmin)
