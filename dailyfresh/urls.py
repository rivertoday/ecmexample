"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search', include('haystack.urls')), # 全文检索框架
    url(r'^tinymce/', include('tinymce.urls')),  # 富文本编辑器url
    url(r'^user/', include('apps.user.urls', namespace='user')), # 用户模块 user.urls
    url(r'^cart/', include('apps.cart.urls', namespace='cart')), # 购物车模块
    url(r'^order/', include('apps.order.urls', namespace='order')), # 订单模块
    url(r'^', include('apps.goods.urls', namespace='goods')), # 商品模块
]
