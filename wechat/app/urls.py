from django.urls import path
from .views import *

urlpatterns = [
    path('qr_img', qr_img, name='qr_img'),
    path('get_group_list', get_group_list, name='get_group_list'),
    path('create_group', create_group, name='create_group'),  # 添加群
    path('add_task', add_task, name='add_task'),  # 添加任务 审核
    path('delete_task', delete_task, name='delete_task'),  # 删除任务
    path('check_list', check_list, name='check_list'),  # 审核列表
    path('check', check, name='check'),  # 审核 管理员权限
    path('send', send, name='send'),  # 发送 所有人都有权限
    path('delete_group', delete_group, name='delete_group'),  # 删除群
    path('add_set', add_set, name='add_set'),  # 添加组
    path('delete_set', delete_set, name='delete_set'),  # 删除组
    path('edit_set', edit_set, name='edit_set'),  # 编辑组
    path('send_set', send_set, name='send_set'),  # 组发送
    path('upload',upload,name='upload'), # 上传

    path('add_friend',add_friend,name='add_friend'), # 添加好友


    path('wxMessage',wxMessage,name='wxMessage') # 微信采集消息
]
