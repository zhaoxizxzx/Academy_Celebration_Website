import json
import os
import random
from io import BytesIO, StringIO
from django.db import transaction
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count  # 计数，聚合函数
from django.db.models.functions import TruncMonth
from django.contrib import auth
from django.db.models import F
from bbs import settings#新增的
from PIL import Image, ImageDraw, ImageFont

from app.myforms import MyRegForm
from app import models


def login(request):
    response_dic = {'code': 1000, 'msg': ''}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # print(username)
        # 从session中获取code
        code = request.POST.get('code')
        # 1、验证码校验，内部统一转大小写
        if request.session.get('code').upper() == code.upper():
            # 2、校验应户名和密码是否正确--UserInfo
            user_obj = auth.authenticate(
                request, username=username, password=password)
            print(user_obj)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                response_dic['msg'] = '登录成功'
                response_dic['url'] = '/home/'
            else:
                response_dic['code'] = 2000
                response_dic['msg'] = '用户名或密码错误'
        else:
            response_dic['code'] = 3000
            response_dic['msg'] = '验证码错误'
        return JsonResponse(response_dic)

    return render(request, 'login.html')


def get_random_color():
    # 获取随机的颜色  RGB
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# 获取验证码


def get_code(request):
    img_obj = Image.new('RGB', (430, 35), get_random_color())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/222.ttf', 30)  # 字体样式
    # 写水机验证码   5位数，包含数字、小写字母、大写字母
    code = ''
    for i in range(5):
        randow_upper = chr(random.randint(65, 98))
        randow_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 从上面的三个里面随机选择一个
        tmp = random.choice([randow_upper, randow_lower, random_int])
        # 将产生的随机字符串写到图片上
        # '''一个一个去写入'''
        img_draw.text((i*45+30, 0), tmp, get_random_color(), img_font)
        # 拼接随机字符串
        code += tmp
    print(code)

    # 添加干扰点和线
    width = 320
    height = 35
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        img_draw.line((x1, y1, x2, y2), fill=get_random_color())

    for i in range(55):
        x = random.randint(0, width)
        y = random.randint(0, height)
        img_draw.point((x, y), fill=get_random_color())

    # 传输正确验证码
    request.session['code'] = code
    # 存在内存对象中
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())

# 注册函数


def register(request):
    form_obj = MyRegForm()
    response_dic = {"code": 1000, "msg": ''}
    if request.method == 'POST':
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        if form_obj.is_valid():
            # 保存合法数据

            # 获取普通数据
            clean_data = form_obj.cleaned_data
            # 将confirm_password删除
            clean_data.pop('confirm_password')
            # 获取头像数据
            avatar_obj = request.FILES.get('avatar')
            # 用户头像判断是否传值
            if avatar_obj:
                # 使用FileFild可以直接这样保存文件数据
                clean_data['avatar'] = avatar_obj
            # 数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            #创建个人站点(新增)
            new_blog = models.Blog.objects.create(site_name=clean_data['username'], site_theme=1,site_title=clean_data['username'] + '的个人站点')
            models.UserInfo.objects.filter(username=clean_data['username']).update(blog=new_blog)
            response_dic['url'] = '/login/'
        else:
            # 校验不通过--添加错误原因
            response_dic['code'] = 2000
            response_dic['msg'] = form_obj.errors
        return JsonResponse(response_dic, safe=False)

    return render(request, 'register.html', locals())


def home(request):
    # 查询本网站所有的文章数据展示到前端页面，这里可以使用分页器分页
    article_queryset = models.Article.objects.all()
    # print(article_queryset)
    return render(request, 'home.html', locals())

# 注销


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')

# 个人站点


def site(request, username, **kwargs):
    # 校验当前用户名是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 不存在返回404页面
    if not user_obj:
        return render(request, 'errors.html')

    # 用户存在，进入用户站点
    blog = user_obj.blog
    # 获取站点文章
    article_list = models.Article.objects.filter(blog=blog)
    # kwargs条件筛选 article_list
    if kwargs:
        # print(kwargs)     #{'condition': 'tag', 'param': '1'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags=param)
        else:
            year, month = param.split('-')  # 2018-11   2018.11  解压赋值
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    print(article_list)

    # pk--primary key
    # 1、取出当前站点的文章分类和及其文章数
    category_list = models.Category.objects.all().annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')#修改过
    # print(category_list)

    # 2、查询当前用户的标签及吧标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(
        count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
    # print(tag_list)

    # 3、按照年月来统计所有的文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')
    # print(date_list)

    return render(request, 'site.html', locals())

# 文章详情


def article_detail(request, username, article_id):
    # 应该先判断username，article_id传入的参数是否存在的，此刻先省略
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    if not article_obj:
        return render(request, 'errors.html')
    category_list = models.Category.objects.all().annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')#修改过
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')
    content_list = models.Comment.objects.filter(article=article_obj)

    return render(request, 'article_detail.html', locals())


# json.JSONEncoder
# 点赞点踩


def up_or_down(request):
    if request.method == "POST":
        # 后台要返回的数据
        response_dic = {'code': 1000, 'msg': ''}

        # 1、是否登录
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            article_obj = models.Article.objects.filter(pk=article_id).first()
            is_up = request.POST.get('is_up')
            # 将is_up字符串转为python数据类型--bool
            is_up = json.loads(is_up)
            # 2、是否点自己
            if not article_obj.blog.userinfo == request.user:
                # 3、是否已经点过
                is_click = models.UpAndDown.objects.filter(
                    user=request.user, article=article_obj)
                if not is_click:
                    # 4、操作数据库--记录数据，同步字段信息
                    with transaction.atomic():
                        if is_up:
                            # 给点赞+1
                            models.Article.objects.filter(
                                pk=article_id).update(up_num=F('up_num')+1)
                            response_dic['msg'] = '点赞成功^-^'
                        else:
                            # 给点踩+1
                            models.Article.objects.filter(
                                pk=article_id).update(down_num=F('down_num')+1)
                            response_dic['msg'] = '点踩成功'
                    # 操作点赞点踩数据库
                    models.UpAndDown.objects.create(
                        user=request.user, article=article_obj, is_up=is_up)
                else:
                    response_dic['code'] = 1001
                    response_dic['msg'] = '点过了哦^-^'  # 你可以做的更详细，写出具体是点了赞还是点了踩
            else:
                response_dic['code'] = 1002
                response_dic['msg'] = '不能给自己哦^-^'
        # 未登录
        else:
            response_dic['code'] = 1003
            response_dic['msg'] = '请先<a href="/login/">登录</a>'
        return JsonResponse(response_dic)


# 评论
def comment(request):
    # 自己也可以评论自己
    if request.method == 'POST':
        response_dic = {'code': 1000, 'msg': "", 'pname':""}
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_obj = models.Comment.objects.filter(pk=parent_id).first().user
                # print(type(parent_username))
                response_dic['pname'] = '@'+parent_obj.username+' '
            # 操作评论表存储数据
            with transaction.atomic():
                models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                models.Comment.objects.create(user=request.user, article_id=article_id, content=content, parent_id=parent_id)
            response_dic['msg'] = '评论成功'
        else:
            response_dic['code'] = 1001
            response_dic['msg'] = '用户未登录'
    return JsonResponse(response_dic)

@login_required
def backend(request):
    # 获取当前用户的全部文章
    article_list = models.Article.objects.filter(blog=request.user.blog)
    return render(request,'backend/backend.html',locals())

from bs4 import BeautifulSoup
# pip3 install beautifulsoup4
@login_required
def add_articel(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')

        # 获取文章内容
        soup = BeautifulSoup(content,'html.parser')
        # 获取所有的html标签
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                # 删除标签
                tag.decompose()

        #文章简介
        # desc = content[0:150]--截取文本150个
        desc = soup.text[0:150]
        article_obj= models.Article.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog
        )

        #文章和标签的关系表是我们自己创建的，无法使用set、clear、remove、add
        #自己去操作关系表，一次可能插入多条数据，我们需要使用批量插入 bulk_create()
        article_obj_list = []
        for i in tag_id_list:
            tag_article_obj = models.Article2Tag(article=article_obj,tag_id=i)
            article_obj_list.append(tag_article_obj)
        #批量插入数据
        models.Article2Tag.objects.bulk_create(article_obj_list)
        #跳转到用户后台文章管理的展示页
        return redirect('/backend/')

    category_list = models.Category.objects.all()#修改过
    tags_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request,'backend/add_article.html',locals())

def upload_image(request):
     response={
         "error" : 0,
         "url" : None}
     file_obj = request.FILES.get('imgFile')
     with open('media/article_img/'+file_obj.name,'wb') as f:
         for line in file_obj:
             f.write(line)
         response['url']='/media/article_img/'+file_obj.name
         return JsonResponse(response)
    # // 成功时
    # {
    #     "error": 0,
    #     "url": "http://www.example.com/path/to/file.ext"
    # }
    # // 失败时
    # {
    #     "error": 1,
    #     "message": "错误信息"
    # }
    # back_dic = {'error': 0, }
     #用户写文章上传的图片也算静态文件，应该放到media文件夹下
     # if request.method == 'POST':
     #     #获取上传的文件对象
     #     file_obj = request.FILES.get('imgFile')
     #     # print(request.FILES)
     #     #手动拼接存储存储文件的路径
     #     file_dir = os.path.join(settings.BASE_DIR,'media','article_img')
     #     #优化操作，先判断是否存在，如果不存在，自动创建文件
     #     if not os.path.isdir(file_dir):
     #         os.mkdir(file_dir)
     #     #拼接图片的完整路径
     #     file_path = os.path.join(file_dir,file_obj.name)
     #     with open(file_path,'wb') as f:
     #         for line in file_obj:
     #             f.write(line)
     #
     #     #为什么不直接用file_path，file_path  返回  /bbs/media
     #     back_dic['url'] = '/media/article_img/%s'%file_obj.name
     #
     # return JsonResponse(back_dic)

@login_required
def set_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)   #数据库不会自动加avatar前缀
        #1/自己手动加前缀
        #2/换一种方式更新
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        return redirect('/home/')
    blog = request.user.blog
    username = request.user.username
    return render(request,'set_avatar.html',locals())

#删除文章(新增)
def delete_article(request):
    nid = request.GET.get('nid')
    models.Article.objects.filter(id=nid).delete()
    return redirect("/backend/")