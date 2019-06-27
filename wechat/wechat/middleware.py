from django import http
from django.contrib.auth.models import User
from django.shortcuts import render
from wechat.settings import PERMISSION_WHITE_LIST
from django.utils.deprecation import MiddlewareMixin
import json
from django.shortcuts import render,redirect
from django.urls import reverse

MAX_REQUEST_PER_SECOND = 2  # 每秒访问次数


class MyPermission(MiddlewareMixin):

    def process_request(self,request):
        if request.path in PERMISSION_WHITE_LIST:
            return None
        # if 'static' in request.path:
        #     return None
        if 'admin' in request.path and request.user.is_superuser:
            return None
        if 'media' in request.path:
            return None
        try:
            url_str = json.loads(request.session['urls'])
        except:
            # 用户尚未分配权限
            return render(request, 'login.html')
        if request.path not in url_str:

            return redirect(reverse('forbidden'))
        return None