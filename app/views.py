import json
import os
import cv2

import random
import base64
import requests
from io import BytesIO, StringIO
from django.db import transaction
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count  # 计数，聚合函数
from django.db.models.functions import TruncMonth
from django.contrib import auth
from django.db.models import F
from bbs import settings #新增的
from PIL import Image, ImageDraw, ImageFont

from app.myforms import MyRegForm
from app import models
from bbs import settings



###########################################
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from django_filters.rest_framework.filterset import FilterSet
from django_filters import filters
from bs4 import BeautifulSoup
# pip install beautifulsoup4

####################################################################
from io import  BytesIO
from PIL_paste import *
from AI_img_api import *
from myrandom_code import *
from Send_mail import SendEmail


# 院庆日程
def schedule(request):
    return render(request, 'schedul/schedule.html')

# 登陆--Done
def bbs_login(request):
    # print(request.user.is_authenticated,request.user.username)
    response_dic = {'code': 1000, 'msg': '登陆成功'}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        if request.session.get('code') == code:
            user_obj = auth.authenticate(
                request, username=username, password=password)
            if user_obj:
                auth.login(request, user_obj)
                avatar = models.UserInfo.objects.filter(pk=user_obj.id).first().avatar
                base64_str='data:image/jpeg;base64,%s' % base64.b64encode(avatar.file.read()).decode()

                response_dic['data'] = {'username':username, 'email':user_obj.email,'avatar':base64_str,}
                response_dic['msg'] = '登录成功'
            else:
                response_dic['code'] = 2000
                response_dic['msg'] = '用户名或密码错误'
        else:
            response_dic['code'] = 3000
            response_dic['msg'] = '验证码错误'
        # print(response_dic)
        print(request.user.is_authenticated,request.user.username)

        return JsonResponse(response_dic)

# 获取随机的颜色  RGB
def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# 获取图片验证码--Done
def bbs_get_code(request):
    mycode_list = random_code()
    print(mycode_list[0])
    code_sum = str(eval(mycode_list[0]))
    print(code_sum)
    img_obj = mycode_list[2]
    # 传输正确验证码
    request.session['code'] = code_sum
    request.session.save()
    # 存在内存对象中
    output_buffer = BytesIO()
    img_obj.save(output_buffer, format='png')
    byte_data = output_buffer.getvalue()
    base64_str='data:image/jpeg;base64,%s' % base64.b64encode(byte_data).decode()
    response_dic = {'code':1001, 'data':base64_str}
    # print(response_dic)
    return JsonResponse(response_dic)

# 注册函数--Done
def bbs_register(request):
    # print(request.body)
    response_dic = {"code": 1000, "msg": 'success'}
    code = request.session.get("email_code")
    user_code = request.POST.get("email_code")
    if code != user_code:
        response_dic['code']=3000
        response_dic['message']='验证码错误'
        return JsonResponse(response_dic)
    form_obj = MyRegForm()
    if request.method == 'POST':
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            # avatar_obj = request.POST.get('avatar')
            # avatar_obj = request.FILES.get('avatar')
            avatar_obj = request.FILES.get('file')
            # print(request.FILES)
            print(avatar_obj)
            if avatar_obj:
                clean_data['avatar'] = avatar_obj
            # 数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
        else:
            # 校验不通过--添加错误原因
            response_dic['code'] = 2000
            response_dic['msg'] = "用户名或密码不合法！"
        print(response_dic)
    return JsonResponse(response_dic, safe=False)

# 发送注册邮箱验证码--Done
def bbs_register_email(request):
    email_dic = {"code":2000, "message":"fail"}
    if request.method=="POST":
        user_mail  = request.POST.get("email")
        print(user_mail)
        email_code = SendEmail(user_mail).send_email()
        email_dic['code']=1000
        email_dic['message']='success'
        email_code = str(email_code)
        request.session['email_code'] = email_code
        print(email_code)
    return JsonResponse(email_dic)


#接口实现主页
def bbs_home(request):
    # 查询本网站所有的文章数据展示到前端页面，这里可以使用分页器分页
    article_list = []
    response_dic = {'code': 1000, 'message':'success', 'data': {'article_list': article_list}}
    article_l = models.Article.objects.all().order_by('-create_time')

    for i in article_l:
        article_list.append({
            'article_url' : 'http://www.fzuprrxd.work/bbs/article/%s/' % i.id,
            'title': i.title,
            'desc': i.desc,
            'create_time': i.create_time.strftime("%Y-%m-%d"),
            'up_num' : i.up_num,
            'username' : i.user.username,
            'avatar':'http://www.fzuprrxd.work/media/%s' % i.user.avatar,
        })
    return JsonResponse(response_dic)

# 注销
@login_required
def bbs_logout(request):
    auth.logout(request)
    print(request.user.username,'--logout')
    response_dic = {}
    response_dic['code'] = 1000
    response_dic['msg'] = 'success'
    return JsonResponse(response_dic)

#接口实现我的帖子
@login_required
def bbs_my_site(request):    
    article_list = []
    response_dic = {'code': 1000, 'message': "success", 'data': {'article_list': article_list}}
    username = request.user.username
    # username = 'user001' # 测试状态 默认登陆user001
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 获取站点文章
    article_l = models.Article.objects.filter(user_id=user_obj.id).order_by('-create_time')
    # 将文章加入文章列表
    for i in article_l:
        article_list.append({
            'article_url' : 'http://www.fzuprrxd.work/bbs/article/%s/' % i.id,
            'title': i.title,
            'desc': i.desc,
            'create_time': i.create_time.strftime("%Y-%m-%d"),
            'up_num' : i.up_num,
            'username' : i.user.username,
            'avatar':'http://www.fzuprrxd.work/media/%s' % i.user.avatar,
        })
    return JsonResponse(response_dic)



def article_detail(request,article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    if not article_obj:
        return render(request, 'errors.html')
    content_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())

# 点赞
def bbs_like(request):
    if request.method == "POST":
        print(request.user)
        response_dic = {'code': 1000, 'msg': ''}
        # 1、是否登录
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            article_obj = models.Article.objects.filter(pk=article_id).first()
            # 2、是否点自己
            if not article_obj.user == request.user:
                # 3、是否已经点过
                is_click = models.Like.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    # 4、操作数据库--记录数据，同步字段信息
                    with transaction.atomic():
                        # 给点赞+1
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num')+1)
                        response_dic['msg'] = '点赞成功^-^'                      
                    # 操作点赞点踩数据库
                    models.Like.objects.create(user=request.user, article=article_obj)
                else:
                    response_dic['code'] = 1001
                    response_dic['msg'] = '点过了哦^-^'  
            else:
                response_dic['code'] = 1002
                response_dic['msg'] = '不能给自己哦^-^'
        # 未登录
        else:
            response_dic['code'] = 1003
            response_dic['msg'] = '请先<a href="/login/">登录</a>'
        return JsonResponse(response_dic)

# 评论
@login_required
def bbs_comment(request):
    # 自己也可以评论自己
    if request.method == 'POST':
        response_dic = {'code': 1000, 'msg': ""}
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')
            # 操作评论表存储数据
            with transaction.atomic():
                models.Comment.objects.create(user=request.user, article_id=article_id, content=content, parent_id=parent_id)
            response_dic['msg'] = '评论成功'
            if parent_id:
                print("hello")
                receive_user = models.Comment.objects.filter(pk=parent_id).first().user
                # models.Message.objects.create(type='com', msg=article_id, send_user=request.user, receive_user=receive_user)
        else:
            response_dic['code'] = 1001
            response_dic['msg'] = '用户未登录'
    return JsonResponse(response_dic)


# 写文章
@login_required
def bbs_add_article(request):
    # print(request.user.username)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        # 获取文章内容
        soup = BeautifulSoup(content,'html.parser')
        #文章简介
        # desc = content[0:150]--截取文本150个
        desc = soup.text[0:150]
        article_obj= models.Article.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            user=request.user
        )

        # article_obj= models.Article.objects.create(
        #     title=title,
        #     content=str(soup),
        #     desc=desc,
        #     user=models.UserInfo.objects.filter(pk=1).first()
        # )#默认登陆状态user001

        response_dic = {"code": 1000, "msg": 'success'}
        return JsonResponse(response_dic)

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

@login_required
def set_avatar(request):
    response_dic = {'code':2000,'message':'fail','data':''}
    if request.method == 'POST':
        # print(request.FILES)
        file_obj = request.FILES.get('file')
        # file_dict  =  request.FILES
        # file_obj  = file_dict['file']
        #print(file_obj)
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        response_dic = {'code':1000,'message':'success','data':''}
    return JsonResponse(response_dic)



#删除文章
def bbs_delete_article(request):
    article_id = request.POST.get('article_id')
    print(article_id)
    print('article_id')
    models.Article.objects.filter(id=article_id).delete()
    response_dic = {'code': 1000, 'message': "success"}
    return JsonResponse(response_dic)


# 虚拟合影--Done
def AI_PIL(request):
    # print(request.body)
    if request.method == "POST":
        file_dict  =  request.FILES
        img  = file_dict['file']
        new_img = AI_img2nobg(img)
        # print(new_img)
        encode_str='data:image/jpeg;base64,%s' % new_img
        # print("AIAIIMG")
        return HttpResponse(encode_str)
    

#班级搜索 创建班级
def add_myclass(request):      #接口实现添加班级
    if request.method == 'POST':
        if len(request.user.name):
            user = request.user
            name = user.name
            #Student_ID= request.POST.get('Student_ID')#学号可以注释掉
            campus = request.POST.get('region')
            grade = request.POST.get('grade')
            major = request.POST.get('profession')
            education = request.POST.get('degree')
            Class = request.POST.get('Class')
            if models.OfficialList.objects.filter(name=name,campus=campus,major=major,education=education,Class=Class).exists():
                if models.ClassesRecode.objects.filter(name=name,campus=campus,major=major,education=education,Class=Class).exists():
                    response_dic = {'code': 1004, 'message': "该认证信息已存在"}
                else:
                    class_name = campus+grade+major+education+Class
                    models.ClassesRecode.objects.update_or_create(name=name,campus=campus,grade=grade,major=major,education=education,Class=Class,class_name=class_name,user=user)
                    models.UserInfo.objects.filter(id=request.user.id).update(alumnus=1)
                    response_dic = {'code': 1000, 'message': "success"}
            else:
                response_dic = {'code': 1003, 'message': "认证失败"}
        else:
            response_dic = {'code': 1001, 'message': "姓名不能为空"}


        return JsonResponse(response_dic)


def search_class(request):     #接口实现班级搜索
    if request.method == 'POST':
        if request.user.alumnus:
            name = request.POST.get('name')
            campus = request.POST.get('campus')
            grade = request.POST.get('grade')
            major = request.POST.get('major')
            education = request.POST.get('education')
            Class = request.POST.get('Class')
            class_name = campus+grade+major+education+Class
            # print(class_name)
            class_list = []
            if len(name):
                if models.ClassesRecode.objects.filter(class_name=class_name,name=name).exists():
                    class_l = models.ClassesRecode.objects.filter(class_name=class_name,name=name)
                    for i in class_l:
                        class_list.append({
                            'name': i.name,
                            'username': i.user.username,
                            'email' : i.user.email

                        })
                    response_dic = {'code': 1000, 'message': "success", 'data': {'class_list': class_list}}
                else: 
                    response_dic = {'code': 1002, 'message': "查无此人"}
            else:
                if models.ClassesRecode.objects.filter(class_name=class_name).exists():
                    class_l = models.ClassesRecode.objects.filter(class_name=class_name)

                    for i in class_l:
                        class_list.append({
                            'name': i.name,
                            'username': i.user.username,
                            'email' : i.user.email
                        })
                # class_list = [1,2,3]
                    response_dic = {'code': 1000, 'message': "success", 'data': {'class_list': class_list}}
                else:
                    response_dic = {'code': 1003, 'message': "查无此班"}
        else:
            response_dic = {'code': 1001, 'message': "未认证为校友"}
        return JsonResponse(response_dic)

# 修改个人信息
def person_msg(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        models.UserInfo.objects.filter(username=request.user.username).update(username=username,name=name,email=email)
        class_list=models.ClassesRecode.objects.filter(user=request.user)
        for i in class_list:
            models.ClassesRecode.objects.filter(id=i.id).update(name=name)
        response_dic = {'code': 1000, 'message': 'success'}
    else:
        class_list = []
        person_list = {
            'username': request.user.username,
            'name': request.user.name,
            'email': request.user.email
        }
        avatar = models.UserInfo.objects.filter(id=request.user.id).first().avatar
        response_dic = {'code': 1001, 'message': "success",'data': {'person_list':person_list,'class_list': class_list},'avatar':'http://www.fzuprrxd.work/media/%s' % avatar}
        class_l = models.ClassesRecode.objects.filter(user=request.user)
        for i in class_l:
            class_list.append({
                'region': i.campus,
                'grade': i.grade,
                'profession': i.major,
                'degree': i.education,
                'Class': i.Class
            })
    return JsonResponse(response_dic)

# 我的评论--Done
def comment_to_me(request):
    user_obj = request.user
    # user_obj = models.UserInfo.objects.filter(pk=1).first() #测试版
    username = user_obj.username
    user_id = user_obj.id
    
    com_to_me = []
    # 我的文章
    article_list = models.Article.objects.filter(user_id=user_id)

    for i in article_list:
        # 该文章的所有评论
        comment_list1 = models.Comment.objects.filter(article_id=i.id)
        for j in comment_list1:
            if j.parent_id == None:
                comment_user = models.UserInfo.objects.filter(id=j.user_id).first()
                com_to_me.append({
                'comment_id' : j.id,
                'comment_content': j.content,
                'comment_user' : comment_user.username,
                'article_title': models.Article.objects.filter(id=j.article_id).first().title,
                'avatar':'http://www.fzuprrxd.work/media/%s' % comment_user.avatar,
                'create_time': j.create_time.strftime("%Y-%m-%d"),
                'article_url' :'http://www.fzuprrxd.work/bbs/article/%s/' % j.article_id
                })

    comment_list2 = models.Comment.objects.filter(user_id=user_id)
    for k in comment_list2:
        comment_list3 = models.Comment.objects.filter(parent_id=k.id)
        for l in comment_list3:
            comment_user = models.UserInfo.objects.filter(id=l.user_id).first()
            com_to_me.append({
                'comment_id': l.id,
                'comment_content' : l.content,
                'comment_user' : comment_user.username,
                'article_title': models.Comment.objects.filter(id=l.parent_id).first().content,
                'avatar':'http://www.fzuprrxd.work/media/%s' % comment_user.avatar,
                'create_time': l.create_time.strftime("%Y-%m-%d"),
                'article_url' :'http://www.fzuprrxd.work/bbs/article/%s/' % l.article_id
            })
    com_to_me2 = sorted(com_to_me, key=lambda tm: (tm["comment_id"]), reverse=True)
    response_dic = {'code': 1000, 'message': 0, 'data': {'com_to_me': com_to_me2}}
    return JsonResponse(response_dic)



#发送私信，输入收信人用户名，以及要发送的消息即可，POST
def send_message(request):
    response_dic = {'code': 1000, 'message': ''}
    send_user = request.user
    receive_name = request.POST.get('receive_username')
    receive_user = models.UserInfo.objects.filter(username=receive_name).first()
    cnt = models.UserInfo.objects.filter(username=receive_user).count()
    if cnt:
        msg = request.POST.get('msg')
        models.message.objects.create(send_user=send_user,msg=msg,receive_user=receive_user)
        response_dic['message'] = '发送成功'
    else:
        response_dic['code'] = 2000
        response_dic['message'] = '用户不存在'
    return JsonResponse(response_dic)

from django.db.models import Q
#我的私信，GET请求，查看所有给我发送的私信
def my_message(request):
    host = request.user
    my_msg = models.message.objects.filter(receive_user_id=host.id)
    my_msg_list = []

    for i in my_msg:
        time1 = i.create_time.replace(microsecond=0)
        time = str(time1)
        my_msg_list.append({
            'send_user' : i.send_user.username,
            'msg': i.msg,
            'msg_id' : i.id,
            'create_time': time
        })
    my_msg_list2 = sorted(my_msg_list, key=lambda tm: (tm["msg_id"]), reverse=True)
    response_dic = {'code': 1000, 'message': 0, 'data': {'my_msg_list': my_msg_list2}}
    return JsonResponse(response_dic)

def message_Detail(request,username):#私信详情，具备回复功能，GET请求可以看到我和username所对应的用户的全部私信记录，POST请求可以发送给该用户的消息
    print('hehe')
    msg_detail = []
    host = request.user
    guest = models.UserInfo.objects.filter(username=username).first()
    if request.method == 'GET':
        msg_list = models.message.objects.filter(Q(send_user_id=host.id,receive_user_id=guest.id)|Q(send_user_id=guest.id,receive_user_id=host.id))
        for i in msg_list:
            time1 = i.create_time.replace(microsecond=0)
            time = str(time1)
            msg_detail.append({
                'send_user': i.send_user.username,
                'msg': i.msg,
                'receive_user' : i.receive_user.username,
                'msg_id': i.id,
                'create_time' : time
            })
        msg_detail2 = sorted(msg_detail, key=lambda tm: (tm["msg_id"]), reverse=True)
        response_dic = {'code': 1000, 'message': 0, 'data': {'msg_detail': msg_detail2}}
        return JsonResponse(response_dic)
    else:
        response_dic2 = {'code': 1000, 'message': 0}
        msg = request.POST.get('msg')
        models.message.objects.create(send_user=host, msg=msg, receive_user=guest)
        response_dic2['message'] = '发送成功'
    return JsonResponse(response_dic2)


def bbs_get_avatar(request):
    if not request.user.is_authenticated:
        return HttpResponse('please login')
    avatar = models.UserInfo.objects.filter(pk=request.user.id).first().avatar
    base64_str='data:image/jpeg;base64,%s' % base64.b64encode(avatar.file.read()).decode()
    return HttpResponse(base64_str)
