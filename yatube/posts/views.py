from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from posts.models import Group, Post, User
from posts.forms import PostForm
from posts.utils import paginating


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginating(request, post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group')
    page_obj = paginating(request, post_list)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.select_related('author', 'group')
    page_obj = paginating(request, user_posts)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {
        'form': form,
    }
    if not form.is_valid():
        form = PostForm()
        return render(request, 'posts/post_create.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=post_id)
