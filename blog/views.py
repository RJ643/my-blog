from django.core.handlers.exception import response_for_exception
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from traitlets.config.manager import recursive_update
from django.utils.text import slugify
from django.contrib.auth import logout

from .models import Post, Category, Tag, Comment
from .forms import CommentForm
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

        comment_form = CommentForm()
        comment_form.fields['content'].widget.attrs.update({
            'placeholder': 'Join the discussion and leave a comment!',
            'class': 'form-control',
            'rows': '3'
        })
        context['comment_form'] = comment_form
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

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super().form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip().replace(',', ';')  # 쉼표를 세미콜론으로 변환
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)  # name만 기준으로 검색

                    if is_tag_created:  # 새로 생성된 태그일 경우에만 slug 설정
                        tag.slug = slugify(t, allow_unicode=True)

                        # 중복된 slug 방지 로직 추가
                        original_slug = tag.slug
                        count = 1
                        while Tag.objects.filter(slug=tag.slug).exists():
                            tag.slug = f"{original_slug}-{count}"
                            count += 1

                        tag.save()

                    self.object.tags.add(tag)

            return response
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category','tags']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = ';'.join(tags_str_list)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate,self).dispatch(request,*args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate,self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',',';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t,allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response

def instant_logout(request):
        """GET 요청만으로 즉시 로그아웃하는 뷰"""
        logout(request)
        return redirect('/blog')  # 로그아웃 후 홈으로 이동 (필요에 따라 변경 가능)
def new_comment(request,pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def delete_comment(request, pk):
    comment = get_object_or_404(Comment,pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied