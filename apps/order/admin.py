from django.contrib import admin
from .models import OrderInfo, OrderGoods

# Register your models here.
class OrderGoodsInline(admin.TabularInline):
    model = OrderGoods
    extra = 0
    verbose_name = u'订单商品'

class OrderInfoAdmin(admin.ModelAdmin):
    """订单模型admin管理类"""
    fieldsets = [
        (None, {'fields': ['order_id', 'user', 'addr', 'pay_method', 'total_count','total_price',
                           'transit_price', 'order_status','trade_no']}),
    ]
    inlines = [OrderGoodsInline]
    list_display = ('order_id', 'user', 'pay_method', 'total_price', 'transit_price', 'order_status','trade_no')
    list_filter = ['order_id']
    search_fields = ['order_id', 'user']

admin.site.register(OrderInfo, OrderInfoAdmin)