from django.shortcuts import render

# Create your views here.

from django.views import View

# 注册视图定义
class RegisterView(View):

    #通过get展示注册页面
    def get(self, request):

        return render(request, 'register.html')