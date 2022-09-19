from django.shortcuts import render
from django.views import View
from home.models import Article, ArticleCategory
from django.http.response import HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse
from home.models import Comment
# Create your views here.


class IndexView(View):

    def get(self, request):
        """
        1.获取所有分类信息
        2.接收用户点击的分类id
        3.根据分类id进行分类的查询
        4.获取分页参数
        5.根据分类信息查询文章数据
        6.创建分页器：实现分页
        7.分页处理
        8.组织数据传递给模板
        :param request:
        :return:
        """
        # 1.获取所有分类信息
        categories = ArticleCategory.objects.all()
        # 2.接收用户点击的分类id
        cat_id = request.GET.get('cat_id', 1)
        # 3.根据分类id进行分类的查询
        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')
        # 4.获取分页参数
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 10)
        # 5.根据分类信息查询文章数据
        articles = Article.objects.filter(category=category)
        # 6.创建分页器：实现分页
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(articles, per_page=page_size)
        # 7.分页处理
        try:
            page_articles = paginator.page(page_num)
        except EmptyPage as e:
            return HttpResponseNotFound('empty page')
        # 总页数参数
        total_page = paginator.num_pages
        # 8.组织数据传递给模板
        context = {
            'categories': categories,
            'category': category,
            'articles': page_articles,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }
        return render(request, 'index.html', context=context)


class DetailView(View):

    def get(self, request):
        """
        1.接收文章id信息（通过查询字符串）
        2.根据文章id进行文章数据查询
        3.查询分类数据
        4.获取分页请求参数
        5.根据文章信息查询评论数据
        6.创建分页器
        7.进行分页处理
        8.组织模板数据
        :param request:
        :return:
        """
        # 1.接收文章id信息（通过查询字符串）
        id = request.GET.get('id')
        # 2.根据文章id进行文章数据查询
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            return render(request, '404.html')
        else:
            # 浏览量增加
            article.total_views += 1
            article.save()
        # 3.查询分类数据
        categories = ArticleCategory.objects.all()
        # 获取热点数据：浏览量前十
        hot_articles = Article.objects.order_by('-total_views')[:9]
        # 4.获取分页请求参数
        page_size = request.GET.get('page_size', 10)
        page_num = request.GET.get('page_num', 1)
        # 5.根据文章信息查询评论数据
        comments = Comment.objects.filter(article=article).order_by('-created')
        # 获取评论总数
        total_count = comments.count()
        # 6.创建分页器
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(comments, page_size)
        # 7.进行分页处理
        try:
            page_comments = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        # 总页数
        total_page = paginator.num_pages
        # 8.组织模板数据
        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_articles': hot_articles,
            'total_count': total_count,
            'comments': page_comments,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }
        return render(request, 'detail.html', context=context)

    def post(self, request):
        """
        1.接收用户信息
        2.判断用户是否登录
         2.1 登录用户可以接收form数据
            2.1.1 接收评论数据
            2.1.2 验证文章是否存在
            2.1.3 保存评论数据
            2.1.4 修改文章的评论数量
         2.2 未登录用户则跳转到登陆页面
        :param request:
        :return:
        """
        # 1.接收用户信息
        user = request.user
        # 2.判断用户是否登录
        if user and user.is_authenticated:
            # 2.1 登录用户可以接收form数据
            # 2.1.1 接收评论数据
            id = request.POST.get('id')
            content = request.POST.get('content')
            # 2.1.2 验证文章是否存在
            try:
                article = Article.objects.get(id=id)
            except Article.DoesNotExist:
                return HttpResponseNotFound('没有此此文章')
            # 2.1.3 保存评论数据
            Comment.objects.create(
                content=content,
                article=article,
                user=user
            )
            # 2.1.4 修改文章的评论数量
            article.comments_count += 1
            article.save()
            # 刷新当前页面(用的页面重定向，也可以ajax)
            path = reverse('home:detail') + '?id={}'.format(article.id)
            return redirect(path)
        else:
            # 2.2 未登录用户则跳转到登陆页面
            return redirect(reverse('users:login'))
