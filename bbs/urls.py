"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path as url
from django.views.static import serve
from django.contrib import admin
from django.urls import path

from bbs import settings
from app import views

urlpatterns = [
    #后台管理
    url(r'^admin/', admin.site.urls),
    #暴露后端用户数据文件夹
    url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),
    #首页
    # url(r'^$', views.bbs_home,name='home'),
    url(r'^bbs/home/', views.bbs_home,name='bbs_home'),  
   
    # 注册
    url(r'^bbs/register/', views.bbs_register,name='bbs_register'),
    # 获取图片验证码
    url(r'^bbs/get_code/', views.bbs_get_code,name='bbs_get_code'),
    # 登陆
    url(r'^bbs/login/', views.bbs_login,name='bbs_login'),
    # 获取邮箱验证码
    url(r'^bbs/get_register_code/', views.bbs_register_email,name='bbs_register_email'),
    # 注销
    url(r'^bbs/logout/', views.bbs_logout,name='bbs_logout'),

     # 文章详情
    # url(r'^bbs/article/',views.bbs_article_detail),
    url(r'^bbs/article/(?P<article_id>\d+)/',views.article_detail),
    # 我的帖子
    url(r'^bbs/my_site/',views.bbs_my_site,name='bbs_my_site'),
    # 点赞
    url(r'^bbs/like/',views.bbs_like),
    # 评论
    url(r'^bbs/comment/', views.bbs_comment,name='bbs_comment'),
    # 删除文章
    url(r'^bbs/delete_article/', views.bbs_delete_article,name='bbs_delete_article'),
    # 添加文章
    url(r'^bbs/add_article/', views.bbs_add_article,name='bbs_add_article'),
    # 我的消息
    url(r'^bbs/new_comment/', views.comment_to_me,name='comment_to_me'),

    url(r'^bbs/add_myclass/',views.add_myclass,name='bbs_add_myclass'),    
    url(r'^bbs/search_class/',views.search_class,name='bbs_search_class'),   
    url(r'^bbs/AI_PIL/', views.AI_PIL, name='bbs_AI_PIL'),
    url(r'^bbs/new_comment/', views.comment_to_me, name='comment_to_me'),

    url(r'^bbs/person_msg/',views.person_msg,name='person_msg'),
    #修改头像
    url(r'^bbs/set_avatar/',views.set_avatar,name='set_avatar'),

    url(r'^bbs/send_message/', views.send_message, name='send_message'),#接口 实现发送私信
    url(r'^bbs/my_message/', views.my_message, name='my_message'),#接口实现我的私信
    #私信详情的url请记得放到最后面
    url(r'^bbs/message_detail/(?P<username>\w+)/',views.message_Detail),# 实现私信详情
    








]
