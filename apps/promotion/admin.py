from django.contrib import admin
from django.contrib import messages
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
        (u'商品折扣或降价', {'fields': ['discount', 'reduct']}),
        (u'商品覆盖范围', {'fields': ['category']}),
    ]
    inlines = [Promotion4Goods_GoodsTypeInline, Promotion4Goods_GoodsSKUInline]
    list_display = ['serial', 'name', 'type', 'status', 'start_time', 'end_time']
    ordering = ['serial', 'name']
    list_filter = ['name']
    search_fields = ['name', 'type', 'status']
    verbose_name = u'按单品促销信息'

    def save_model(self, request, obj, form, change):
        """新增或更新时调用"""
        # 附加操作：检查数据一致性
        if (obj.type == 0 and obj.discount <= 0):
            messages.set_level(request, messages.ERROR)
            messages.error(request, '打折活动，打折率不能小于等于零！')
        elif (obj.type == 0 and obj.discount > 1):
            messages.set_level(request, messages.ERROR)
            messages.error(request, '打折活动，打折率不能大于1！')
        elif (obj.type == 1 and obj.reduct < 0):
            messages.set_level(request, messages.ERROR)
            messages.error(request, '降价活动，降价金额不能小于零！')
        else:
            # 调用ModelAdmin中save_model来实现更新或新增
            super().save_model(request, obj, form, change)
            messages.info(request, '商品促销活动创建成功！')

class Promotion4OrderAdmin(admin.ModelAdmin):
    """促销按单品模型admin管理类"""
    fieldsets = [
        (u'活动编码', {'fields': [ 'serial']}),
        (u'活动名称与描述', {'fields': ['name','detail']}),
        (u'活动时间', {'fields': ['start_time','end_time']}),
        (u'活动状态', {'fields': ['status']}),
        (u'活动类型', {'fields': ['type']}),
        (u'订单起点金额', {'fields': ['amount']}),
        (u'订单折扣或降价', {'fields': ['discount', 'reduct']}),
    ]
    list_display = ['serial', 'name', 'type', 'status', 'start_time', 'end_time']
    ordering = ['serial', 'name']
    list_filter = ['name']
    search_fields = ['name', 'type', 'status']
    verbose_name = u'按订单促销信息'

    def save_model(self, request, obj, form, change):
        """新增或更新时调用"""
        # 附加操作：检查数据一致性
        if (obj.type == 0 and obj.amount <= 0):
            messages.set_level(request, messages.ERROR)
            messages.error(request, '订单金额起点不能为零或负数！')
        elif (obj.type == 1 and obj.discount <= 0):
            messages.set_level(request, messages.ERROR)
            messages.error(request, '订单满折，打折率不能小于等于零！')
        elif (obj.type == 1 and obj.discount > 1):
            messages.set_level(request, messages.ERROR)
            messages.error(request, '订单满折，打折率不能大于1！')
        elif (obj.type == 2 and obj.reduct < 0):
            messages.set_level(request, messages.ERROR)
            messages.error(request, '订单满减，减免金额不能小于零！')
        else:
            # 调用ModelAdmin中save_model来实现更新或新增
            super().save_model(request, obj, form, change)
            messages.info(request, '订单促销活动创建成功！')

admin.site.register(Promotion4Goods, Promotion4GoodsAdmin)
admin.site.register(Promotion4Order, Promotion4OrderAdmin)