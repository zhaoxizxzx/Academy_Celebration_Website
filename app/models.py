from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import admin
#用户表
class UserInfo(AbstractUser):
    avatar = models.FileField(upload_to='avatar/',default='avatar/default.png',verbose_name='用户头像')
    #给avatar字段传文件对象，文件存储在avatar路径下，avatar值保存的是文件路径
    create_time = models.DateField(auto_now_add=True)
    name = models.CharField(verbose_name='姓名',max_length=32)
    alumnus = models.BooleanField(verbose_name='校友认证',default=False)
    class Meta:
        verbose_name_plural = '用户管理'
        # verbose_name = '用户表'

#文章表
class Article(models.Model):
    
    title = models.CharField(verbose_name='文章标题',max_length=64)
    desc = models.CharField(verbose_name='文章简介',max_length=255)
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    up_num = models.BigIntegerField(verbose_name='点赞数',default=0)

    #外键字段
    user = models.ForeignKey(verbose_name='文章作者',to='UserInfo',on_delete = models.CASCADE)
   
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = '文章管理'

#点赞表
class Like(models.Model):
    user = models.ForeignKey(to='UserInfo',on_delete = models.CASCADE)
    article = models.ForeignKey(to='Article',on_delete = models.CASCADE)
    class Meta:
        verbose_name_plural = '点赞情况'

#评论表
class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo',on_delete = models.CASCADE)
    article = models.ForeignKey(to='Article',on_delete =  models.CASCADE)
    content = models.CharField(verbose_name='评论',max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    #自关联
    parent = models.ForeignKey(to='self',null=True,blank = True, on_delete =  models.CASCADE)
    def __str__(self):
        return self.content
    class Meta:
        verbose_name_plural = '评论管理'

#班级搜索表
class ClassesRecode(models.Model):
    name = models.CharField(verbose_name='姓名',max_length=32)
    Student_ID = models.CharField(verbose_name='学号',max_length=32)
    campus = models.CharField(verbose_name='校区',max_length=32)
    grade = models.CharField(verbose_name='年级',max_length=32)
    major = models.CharField(verbose_name='专业',max_length=32)
    education = models.CharField(verbose_name='学历',max_length=32)
    Class = models.CharField(verbose_name='班级',max_length=32)
    class_name = models.CharField(verbose_name='班级名',max_length=256)
#外键

    user = models.ForeignKey(to='UserInfo',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.class_name+'  '+self.name
    class Meta:
        verbose_name_plural = '班级管理'


# class Message(models.Model):
#     # 'com'/'msg'
#     type = models.CharField(verbose_name='类型',max_length=32)
#     msg = models.CharField(verbose_name='内容', max_length=255)
#     send_user = models.ForeignKey(verbose_name='发送者',related_name='send_user',to='UserInfo', on_delete =  models.CASCADE)
#     receive_user = models.ForeignKey(verbose_name='接收者',related_name='receive_user',to='UserInfo', on_delete =  models.CASCADE)
#     create_time =  models.DateTimeField(verbose_name='私信时间',auto_now_add=True)
# 私信表
class message(models.Model):
    msg = models.CharField(verbose_name='内容', max_length=255)
    send_user = models.ForeignKey(to='UserInfo',null=True, on_delete=models.SET_NULL,related_name='send_user')
    receive_user = models.ForeignKey(to='UserInfo',null=True, on_delete=models.SET_NULL,related_name='receive_user')
    create_time =  models.DateTimeField(verbose_name='私信时间',auto_now_add=True)

#官方名单
class OfficialList(models.Model):
    name = models.CharField(verbose_name='姓名',max_length=32)
    campus = models.CharField(verbose_name='校区',max_length=32)
    grade = models.CharField(verbose_name='年级',max_length=32)
    major = models.CharField(verbose_name='专业',max_length=32)
    education = models.CharField(verbose_name='学历',max_length=32)
    Class = models.CharField(verbose_name='班级',max_length=32)
    def __str__(self):
        return self.education+self.campus+self.grade+self.major+self.Class+self.name
    class Meta:
        verbose_name_plural = '官方名单'
    #python manage.py makemigrations
    #python manage.py migrate