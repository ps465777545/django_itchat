from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
# Create your models here.

class groups_name(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='群名')
    users_num = models.IntegerField(blank=True,null=True,verbose_name='人数')
    owner = models.CharField(max_length=50,blank=True,null=True,verbose_name='群主')
    group_id = models.CharField(max_length=255,blank=True,null=True,verbose_name='群唯一id')
    user = models.ForeignKey(User,blank=True,null=True,verbose_name='关联用户',on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class grouping(models.Model):
    group_name = models.CharField(max_length=100,blank=True,null=True,verbose_name='分组名称')
    group = models.ManyToManyField(groups_name)
    user = models.ForeignKey(User, blank=True, null=True, verbose_name='关联用户', on_delete=models.CASCADE)
    def __str__(self):
        return self.group_name

# 任务
class task(models.Model):
    message = models.TextField(verbose_name='消息',blank=True, null=True,)
    message_type = models.CharField(max_length=10,verbose_name='消息类型',blank=True, null=True,default='文字')
    group_name = models.TextField(verbose_name='群组名字',blank=True, null=True,)
    status = models.CharField(max_length=10,default='待审核',verbose_name='任务状态')
    date = models.DateTimeField(default=datetime.now(),verbose_name='任务添加时间')
    typ = models.CharField(max_length=10,blank=True,null=True,verbose_name='任务类别')
    uuid_str = models.CharField(max_length=255, blank=True, null=True, verbose_name='唯一标识', db_index=True)
    user = models.ForeignKey(User, blank=True, null=True, verbose_name='关联用户', on_delete=models.CASCADE)
    def __str__(self):
        return self.message

class file(models.Model):
    uuid_str = models.CharField(max_length=255,blank=True,null=True,verbose_name='唯一标识',db_index = True)
    file_path = models.CharField(max_length=255,blank=True,null=True,verbose_name='文件路径')
    status = models.CharField(max_length=10, default='未发送',blank=True,null=True, verbose_name='任务状态')
    def __str__(self):
        return self.file_path


class UrlTable(models.Model):
    url = models.CharField(max_length=255,blank=True,null=True,verbose_name='路由')
    name = models.CharField(max_length=100,blank=True,null=True,verbose_name='路由名称')
    def __str__(self):
        return 'url：%s(%s)' % (self.url,self.name)

class Role(models.Model):
    role_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='角色名称')
    permission = models.ManyToManyField('UrlTable')

    def __str__(self):
        return '角色：%s' % self.role_name


class MyUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.ManyToManyField(Role)

    def __str__(self):
        return '用户：%s' % self.user


class wechat_friend(models.Model):
    friend_username = models.CharField(max_length=255,blank=True,null=True,verbose_name='好友账号')
    status = models.IntegerField(default=0,verbose_name='状态')  # 0 未添加  1 添加成功  2 添加失败  3 无该好友
    add_date = models.DateTimeField(default=datetime.now(),verbose_name='添加时间')
    def __str__(self):
        return '好友账号：%s' % self.friend_username

    class Meta:
        db_table = 'wechat_friend'