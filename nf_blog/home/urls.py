from django.urls import path
from home.views import IndexView, DetailView
urlpatterns = [
    # 首页展示路由
    path('', IndexView.as_view(), name='index'),

    # 文章详情展示路由
    path('detail/', DetailView.as_view(), name='detail'),
]