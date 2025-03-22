from django.urls import path
from . import views
from .views import instant_logout

urlpatterns = [
    path('delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<path:slug>/', views.tag_page, name='tag_page'),
    path('category/<path:slug>/', views.category_page, name='category_page'),  # ✅ 변경: <slug:slug> → <path:slug>
    path('<int:pk>/new_comment/', views.new_comment),
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('', views.PostList.as_view(), name='post_list'),
    path('instant-logout/', instant_logout, name='instant_logout'),
]
