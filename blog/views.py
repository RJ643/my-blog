from django.core.handlers.exception import response_for_exception
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from traitlets.config.manager import recursive_update
from django.utils.text import slugify

from .models import Post, Category, Tag
from django.core.exceptions import PermissionDenied

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
    tag = get_object_or_404(Tag, slug=slugify(slug, allow_unicode=True))
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

class PostCreate(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',',';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return  response
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category','tags']

    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate,self).dispatch(request,*args, **kwargs)
        else:
            raise PermissionDenied