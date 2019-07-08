#from django.conf.urls import include, url
from django.urls import path, re_path
from apps.goods.views import IndexView, DetailView, ListView

urlpatterns = [
    # url(r'^$', IndexView.as_view(), name='index'),  # 首页
    # # url(r'^search', include('haystack.urls')), # 全文检索框架
    # # url(r'^index$', IndexView.as_view(), name='index'),  # 首页
    # url(r'^goods/(?P<sku_id>\d+)$', DetailView.as_view(), name='detail'),  # 详情页
    # url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list'), # 列表页

    path('', IndexView.as_view(), name='index'),  # 首页
    re_path('goods/(?P<sku_id>\d+)/', DetailView.as_view(), name='detail'),  # 详情页
    re_path('list/(?P<type_id>\d+)/(?P<page>\d+)/', ListView.as_view(), name='list'), # 列表页
]
