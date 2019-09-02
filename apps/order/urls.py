#from django.conf.urls import url
from django.urls import path, re_path
from order.views import OrderPlaceView, OrderCommitView, OrderCheckView, OrderPayView, CommentView

urlpatterns = [
    # url(r'^place$', OrderPlaceView.as_view(), name='place'), # 提交订单页面
    # url(r'^commit$', OrderCommitView.as_view(), name='commit'), # 创建订单
    # url(r'^pay$', OrderPayView.as_view(), name='pay'), # 订单支付
    # url(r'^check$', OrderCheckView.as_view(), name='check'), # 订单交易结果
    # url(r'^comment/(?P<order_id>.*)$', CommentView.as_view(), name='comment'), # 订单评论

    path('place/', OrderPlaceView.as_view(), name='place'), # 提交订单页面
    path('commit/', OrderCommitView.as_view(), name='commit'), # 创建订单
    path('pay/', OrderPayView.as_view(), name='pay'), # 订单支付
    path('check/', OrderCheckView.as_view(), name='check'), # 订单交易结果
    re_path('comment/(?P<order_id>.*)/', CommentView.as_view(), name='comment'), # 订单评论
]
