from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from yatube.settings import POSTS_ON_PAGE
from .models import Group, Post, User
from .forms import PostForm


def get_page_context(queryset, request):
    paginator = Paginator(queryset, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


def index(request):
    context = get_page_context(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(get_page_context(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {
        'author': author,
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.all().count()
    context = {
        'post': post,
        'post_count': post_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    form = PostForm(request.POST or None)
    context = {
        'groups': groups,
        'form': form,
    }
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    groups = Group.objects.all()
    form = PostForm(instance=post)
    context = {
        'form': form,
        'groups': groups,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)
