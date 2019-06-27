"""wechat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from app import urls
from app.views import do_login, do_logout, forbidden
from django.contrib.staticfiles.views import serve
from django.views.generic.base import RedirectView
from .settings import MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', serve, {"path": "image/favicon.ico"}),
    path('app/', include(urls)),
    path('login', do_login, name='do_login'),  # 登录
    path('logout', do_logout, name='logout'),
    path('forbidden', forbidden, name='forbidden'),
    path('', RedirectView.as_view(url='/app/get_group_list')),
]
