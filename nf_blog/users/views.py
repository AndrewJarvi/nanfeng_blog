from django.shortcuts import render

# Create your views here.

from django.views import View

# 注册视图定义
class RegisterView(View):

    #通过get展示注册页面
    def get(self, request):

        return render(request, 'register.html')

from django.http import HttpResponseBadRequest, HttpResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

# 图片验证码视图定义
class ImageCodeView(View):

    def get(self, request):
        # 获取前端传递过来的参数
        uuid=request.GET.get('uuid')
        # 判断是是否获取到uuid：判断参数是否为None
        if uuid is None:
            return HttpResponseBadRequest('请求参数错误，无法获取uuid号')
        # 通过调用captcha获取验证码内容和验证码图片二进制数据
        text, image = captcha.generate_captcha()
        # 将图片验内容保存到redis中，通过default获取到0号库，并设置过期时间:300s
        redis_conn = get_redis_connection('default')
        redis_conn.setex('image:%s' % uuid, 300, text)
        # 返回响应，将生成的图片以content_type为image/jpeg的形式返回给请求
        return HttpResponse(image, content_type='image/jpeg')