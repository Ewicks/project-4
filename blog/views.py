from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import CommentForm, PostForm
from django.core.paginator import Paginator


def TopicView(request, tops):
    topics_posts = Post.objects.filter(topics=tops)
    return render(request, 'topics.html', {
        'tops': tops, 'topics_posts': topics_posts})


class PostDetail(View):
    def get(self, request, pk, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, id=pk)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        template = "article_details.html"
        context = {
            "post": post,
            "comments": comments,
            "commented": False,
            "comment_form": CommentForm()
        }
        return render(request, template, context)

    def post(self, request, pk, *args, **kwargs):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, id=pk)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "article_details.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
            },
        )


class PostLike(View):
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('article-detail', args=[post.id]))


class PostList(ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "blog.html"
    paginate_by = 6
    ordering = ["-updated_on"]
    # ordering = ["-id"]


@login_required
def add_post(request):
    post_form = PostForm(request.POST or None, request.FILES)
    if request.method == "POST":
        if post_form.is_valid():
            post_form.instance.author = request.user
            post_form.save()
            return redirect("blog")
    template = "add_post.html"
    context = {
        "form": post_form,
    }
    return render(request, template, context)


@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    post_form = PostForm(instance=post)
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES, instance=post)
        if post_form.is_valid():
            post_form.save()
            return redirect("blog")
    template = "update_post.html"
    context = {
        'post': post,
        'form': post_form,
    }
    return render(request, template, context)


class DeletePostView(DeleteView):
    model = Post
    template_name = "delete_post.html"
    success_url = reverse_lazy('blog')


def about(request):
    """ A view to return the about page """
    return render(request, 'about.html')


def contact(request):
    """ A view to return the contact page """
    return render(request, 'contact.html')


def index(request):
    """ A view to return the blog page """
    return render(request, 'index.html')
