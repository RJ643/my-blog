from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Category, Tag


# 📌 [1] 메인 페이지 (게시글 리스트)
class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


# 📌 [2] 게시글 상세 페이지
class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


# 📌 [3] 카테고리별 게시글 리스트
def category_page(request, slug):
    print(f"📌 카테고리 slug: {slug}")  # ✅ 카테고리 slug 확인용 로그
    category = get_object_or_404(Category, slug=slug)
    print(f"✅ 가져온 카테고리: {category}")  # ✅ 카테고리 객체 확인

    post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,  # ✅ 템플릿에서 사용할 category 전달
        }
    )


# 📌 [4] 태그별 게시글 리스트
def tag_page(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    post_list = tag.post_set.all()  # ✅ 태그에 연결된 게시글 가져오기

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,  # ✅ 템플릿에 태그 값 전달
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )

class PostCreate(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category']

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/blog/')
