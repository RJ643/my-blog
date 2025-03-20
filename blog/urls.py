from django.urls import path
from . import views

urlpatterns = [
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<path:slug>/', views.tag_page, name='tag_page'),
    path('category/<path:slug>/', views.category_page, name='category_page'),  # ✅ 변경: <slug:slug> → <path:slug>
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('', views.PostList.as_view(), name='post_list'),
]
