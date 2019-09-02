from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType, Goods, GoodsSKU, GoodsImage, IndexPromotionBanner, IndexGoodsBanner,  IndexTypeGoodsBanner
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增或更新时调用"""
        # 调用ModelAdmin中save_model来实现更新或新增
        super().save_model(request, obj, form, change)

        # 附加操作：发出生成静态首页的任务
        from celery_tasks.tasks import generate_static_index_html
        print('发出重新生成静态首页的任务')
        generate_static_index_html.delay()

        # 附加操作: 清除首页缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除数据时调用"""
        # 调用ModelAdmin中delete_model来实现删除操作
        super().delete_model(request, obj)

        # 附加操作：发出生成静态首页的任务
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 附加操作: 清除首页缓存
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseModelAdmin):
    """商品种类模型admin管理类"""
    fieldsets = [
        (u'商品分类名称', {'fields': ['name']}),
        (u'商品描述',
         {'fields': ['logo','image']}),
    ]
    list_display = ['name', 'logo', 'image']
    ordering = ['name']
    list_filter = ['name']
    search_fields = ['name', 'logo']
    verbose_name = u'商品分类信息'

class GoodsImageInline(admin.TabularInline):
    model = GoodsImage
    extra = 0
    verbose_name = u'商品图片'

class GoodsAdmin(BaseModelAdmin):
    """商品模型admin管理类"""
    fieldsets = [
        (u'商品SPU名称', {'fields': ['name']}),
        (u'商品描述',
         {'fields': ['detail']}),
    ]
    inlines = [GoodsImageInline]
    list_display = ['name', 'detail']
    ordering = ['name']
    list_filter = ['name']
    search_fields = ['name', 'detail']
    verbose_name = u'商品SPU信息'

class GoodsSKUAdmin(BaseModelAdmin):
    """商品SKU模型admin管理类"""
    fieldsets = [
        (u'商品SKU名称和简介', {'fields': ['name', 'desc']}),
        (u'所属商品种类和名称', {'fields': ['category','goods']}),
        (u'上下架状态', {'fields': ['status']}),
        (u'规格信息', {'fields': ['price', 'unit', 'stock', 'sales']}),
        (u'SKU图片', {'fields': ['image']}),
    ]
    list_display = ['name', 'category', 'goods', 'status', 'price', 'unit', 'stock', 'sales']
    ordering = ['name', 'category', 'goods', 'price']
    list_filter = ['name', 'category', 'goods']
    search_fields = ['category', 'goods', 'name']
    verbose_name = u'商品SKU信息'


class IndexGoodsBannerAdmin(BaseModelAdmin):
    """首页轮播商品模型admin管理类"""
    fieldsets = [
        (u'首页轮播大图商品SKU名称', {'fields': ['sku']}),
        (u'其它信息',
         {'fields': ['image','index']}),
    ]
    list_display = ['sku', 'index', 'image']
    ordering = ['index']
    list_filter = ['sku']
    verbose_name = u'首页轮播大图信息'


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    """首页分类商品展示模型admi管理类"""
    fieldsets = [
        (u'首页商品分类名称', {'fields': ['category']}),
        (u'其它信息',
         {'fields': ['sku', 'display_type', 'index']}),
    ]
    list_display = ['category', 'display_type', 'sku', 'index']
    ordering = ['index']
    list_filter = ['category']
    verbose_name = u'首页分类中展示商品信息'


class IndexPromotionBannerAdmin(BaseModelAdmin):
    """首页促销活动admin管理类"""
    pass

admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)


