from django.contrib import admin

from .models import Group, Post, Comment, Follow, Like, BadWords


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text', 'title',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_per_page = 15


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description',)
    search_fields = ('text',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'
    list_per_page = 15


@admin.register(Comment)
class GroupComment(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'text', 'pub_date',)
    list_editable = ('text', 'author',)
    search_fields = ('text', 'author__username',)
    list_filter = ('pub_date',)
    list_per_page = 15
    empty_value_display = '-пусто-'


@admin.register(Follow)
class GroupFollow(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user__username', 'author__username',)
    list_per_page = 30


@admin.register(Like)
class GroupLike(admin.ModelAdmin):
    list_display = ('user', 'post', 'value',)
    search_fields = ('user__username', 'post__text',)
    list_per_page = 30


@admin.register(BadWords)
class GroupBadWords(admin.ModelAdmin):
    list_display = ('word',)
    search_fields = ('word',)
    list_per_page = 50
    empty_value_display = '-пусто-'
