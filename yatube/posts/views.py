from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_object_or_404, redirect,
                              render)
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow, Like, Comment


def paginator(posts, request):
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    posts = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': paginator(posts, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    context = {
        'group': group,
        'posts': posts,
        'page_obj': paginator(posts, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists())
    context = {
        'author': author,
        'page_obj': paginator(posts, request),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    username = request.user
    form = PostForm(
        request.POST or None,
        request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = username
        post.save()
        return redirect('posts:profile', username=username)
    return render(request, 'posts/create_post.html', {'form': form})


#  Удаление постов
@login_required
def post_delete(request, post_id):
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    if user == post.author:
        post.delete()
        return redirect('posts:profile', user.username)
        # return redirect('posts:index')


@login_required
def post_edit(request, post_id):
    username = request.user
    post = get_object_or_404(Post, pk=post_id)
    if post.author != username:
        return redirect('posts:profile', username=request.user.username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    else:
        messages.info(request,
                      f'Ваш комментарий не опубликован, '
                      f'так как содержал запрещенные слова'
                      )
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author:
        Comment.objects.get(pk=pk).delete()
        return redirect('posts:post_detail', comment.post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user)
    context = {
        'page_obj': paginator(posts, request),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=username)
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)


@login_required
def like_post(request):
    user = request.user
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)

        if user != post.author:
            if user in post_obj.liked.all():
                post_obj.liked.remove(user)
            else:
                post_obj.liked.add(user)

            like, created = Like.objects.get_or_create(user=user, post_id=post_id)
            if not created:
                if like.value == 'Нравится':
                    like.value = 'Не нравится'
                else:
                    like.value = 'Нравится'
            like.save()
        return redirect('posts:index')


@login_required
def users_liked_post(request):
    user = request.user
    posts = User.objects.prefetch_related('liked_by').get(pk=user.pk).liked_by.all()
    context = {
        'page_obj': paginator(posts, request),
    }
    return render(request, 'posts/liked_post.html', context)
