from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
# Create your views here.

from django.views import View

from django.http.response import HttpResponseBadRequest
import re
from users.models import User
from django.db import DatabaseError

# 注册视图定义
class RegisterView(View):

    #通过get展示注册页面
    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):
        """
        1.接收数据
        2.验证数据
            2.1 参数是否齐全
            2.2 手机号格式是否正确
            2.3 密码是否符合格式
            2.4 密码和确认密码是否一致
            2.5 短信验证码是否和redis中的一致
        3.保存注册信息
        4.返回响应跳转到指定页面
        :param request:
        :return:
        """
        # 1.接收数据
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        sms_code = request.POST.get('sms_code')
        # 2.验证数据
        if not all ([mobile, password, password2, sms_code]):
            return HttpResponseBadRequest('缺少必要的参数')
        #     2.1 参数是否齐全
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号不符合规则')
        #     2.2 手机号格式是否正确
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位只由数字和字母组成的密码')
        #     2.3 密码是否符合格式
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        #     2.4 密码和确认密码是否一致
        redis_conn = get_redis_connection('default')
        redis_sms_code = redis_conn.get('sms:%s' % mobile)
        if redis_sms_code is None:
            return HttpResponseBadRequest('短信验证码已过期')
        #     2.5 短信验证码是否和redis中的一致
        if sms_code != redis_sms_code.decode():
            return HttpResponseBadRequest('短信验证码不一致')
        # 3.保存注册信息 (同样因为是操作数据库需要做异常捕获)
        try:
            user = User.objects.create_user(
                username=mobile,
                mobile=mobile,
                password=password,
            )
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('注册失败')

        # 实现状态保持
        from django.contrib.auth import login
        login(request, user)

        # 4.返回响应跳转到指定页面 redirect进行重定向 reverse通过命名空间获取视图所对应的路由
        response = redirect(reverse('home:index'))
        # 设置cookie信息，方便首页中用户信息展示的判断和用户信息的展示
        # 登陆状态，会话结束后自动过期
        response.set_cookie('is_login', True)
        # 用户名有效期设置为一个星期
        response.set_cookie('username', user.username, max_age=7*24*3600)

        return response

from django.http import HttpResponseBadRequest, HttpResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection


# 图片验证码视图定义
class ImageCodeView(View):

    def get(self, request):
        # 获取前端传递过来的参数
        uuid = request.GET.get('uuid')
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


from django.http.response import JsonResponse
from utils.response_code import RETCODE
import logging
logger = logging.getLogger('django')
from random import randint
from libs.yuntongxun.sms import CCP

class SmsCodeView(View):

    def get(self, request):
        """
        1.接收参数
        2.参数的验证
            2.1 验证参数是否齐全
            2.2 图片验证码的验证
                链接redis-》获取redis中的图片验证码
                判断图片验证码是否存在（redis数据具有时效性，有可能会过期）
                如果图片验证码未过期，我们获取到后就可以删除图片验证码
                比对图片验证码（记得处理大小写）
        3.生成短信验证码
        4.保存短信验证码到redis中
        5.发送短信
        6.返回响应
        :param request:
        :return:
        """
        # 1.接收参数（查询字符串形式传递来的）
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 2.参数的验证
        #     2.1 验证参数是否齐全
        if not all([mobile, image_code, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'error_message': '缺少必要参数'})
        #     2.2 图片验证码的验证
        #         链接redis -》获取redis中的图片验证码
        redis_conn = get_redis_connection('default')
        redis_image_code = redis_conn.get('image:%s' % uuid)
        #         判断图片验证码是否存在（redis数据具有时效性，有可能会过期）
        if redis_image_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'error_message': '图片验证码已过期'})
        #         如果图片验证码未过期，我们获取到后就可以删除图片验证码 (因为要做删除reids数据的操作，做个异常捕获同时记录日志)
        try:
            redis_conn.delete('img:%s' % uuid)
        except Exception as e:
            logger.error(e)
        #         比对图片验证码（记得处理大小写）redis的数据是bytes类型
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'error_message': '图片验证码错误'})
        # 3.生成短信验证码 随机六位
        sms_code = '%06d' % randint(0, 999999)
        # 为了后期比对方，可以将短信验证码记录到日志中
        logger.info(sms_code)
        # 4.保存短信验证码到redis中 电话做key，300s过期 短信验证码为value
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)
        # 5.调用容联云，发送短信
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 6.返回响应
        return JsonResponse({'code': RETCODE.OK, 'error_message': '短信发送成功'})