from django.contrib import admin
from .models import Promotion4Goods, Promotion4Goods_GoodsType, Promotion4Goods_GoodsSKU, Promotion4Order
# Register your models here.

class Promotion4Goods_GoodsTypeInline(admin.TabularInline):
    model = Promotion4Goods_GoodsType
    extra = 0
    verbose_name = u'促销与商品分类关联'

class Promotion4Goods_GoodsSKUInline(admin.TabularInline):
    model = Promotion4Goods_GoodsSKU
    extra = 0
    verbose_name = u'促销与商品SKU关联'

class Promotion4GoodsAdmin(admin.ModelAdmin):
    """促销按单品模型admin管理类"""
    fieldsets = [
        (u'活动编码', {'fields': [ 'serial']}),
        (u'活动名称与描述', {'fields': ['name','detail']}),
        (u'活动时间', {'fields': ['start_time','end_time']}),
        (u'活动状态', {'fields': ['status']}),
        (u'活动类型', {'fields': ['type']}),
        (u'活动覆盖范围', {'fields': ['category']}),
        (u'活动折扣或降价', {'fields': ['discount','reduct']}),
    ]
    inlines = [Promotion4Goods_GoodsTypeInline, Promotion4Goods_GoodsSKUInline]
    list_display = ['serial', 'name', 'type', 'status', 'start_time', 'end_time']
    ordering = ['serial', 'name']
    list_filter = ['name']
    search_fields = ['name', 'type', 'status']
    verbose_name = u'按单品促销信息'

admin.site.register(Promotion4Goods, Promotion4GoodsAdmin)