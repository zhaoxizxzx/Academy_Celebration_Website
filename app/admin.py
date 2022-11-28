from django.contrib import admin
from app import models

admin.site.site_title = "后台管理"

admin.site.site_header = "后台管理"

admin.site.index_title = "后台管理"
#admin注册表
admin.site.register(models.UserInfo)
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article)
admin.site.register(models.Article2Tag)
admin.site.register(models.UpAndDown)
admin.site.register(models.Comment)
admin.site.register(models.ClassesRecode)
