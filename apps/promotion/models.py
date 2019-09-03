from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField
from datetime import date
#from goods.models import GoodsType, GoodsSKU

# Create your models here.
# 促销基类
class Promotion(BaseModel):
    '''商品促销模型类'''
    promotion_status = (
        (0, '启用'),
        (1, '停用'),
    )
    # 活动编码
    serial = models.CharField(max_length=50, verbose_name=u'促销活动编码', help_text="促销活动编码")
    # 活动名称
    name = models.CharField(max_length=50, verbose_name=u'促销活动名称', help_text="促销活动名称")
    # 富文本类型:带有格式的文本
    detail = HTMLField(blank=True, verbose_name=u'促销活动详情')
    # 活动时间
    start_time = models.DateTimeField(verbose_name=u'开始时间', help_text="开始时间")
    end_time = models.DateTimeField(verbose_name=u'结束时间', help_text="结束时间")
    #活动状态
    status = models.SmallIntegerField(default=1, choices=promotion_status, verbose_name='活动状态')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'df_promotions'
        verbose_name = '促销活动'
        verbose_name_plural = verbose_name

#按单品促销
class Promotion4Goods(Promotion):
    prom_type_goods = (
        (0, '打折'),
        (1, '降价'),
    )
    prom_category = (
        (0, '全部商品'),
        (1, '商品分类'),
        (2, '指定商品'),
    )
    # 活动类型
    type = models.SmallIntegerField(default=0, choices=prom_type_goods, verbose_name=u'活动类型')
    # 覆盖范围
    category = models.SmallIntegerField(default=0, choices=prom_category, verbose_name=u'覆盖范围')
    # 根据覆盖范围不同，建立不同的关联关系
    # 程序去检索下面两个对应的模型
    #打折率,例如0.95折
    discount = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, null=True, verbose_name=u'打折率')
    #降价价格，最多降999
    reduct = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, verbose_name=u'降价')

    class Meta:
        db_table = 'df_promotions4goods'
        verbose_name = '单品促销'
        verbose_name_plural = verbose_name

#单品促销与商品分类的关联
class Promotion4Goods_GoodsType(BaseModel):
    p4gobj = models.ForeignKey('Promotion4Goods', verbose_name=u'促销按单品', on_delete=models.CASCADE)
    gtobj = models.ForeignKey('goods.GoodsType', verbose_name=u'商品种类', on_delete=models.CASCADE)
    class Meta:
        db_table = 'df_promotions4goods_goodstype'
        verbose_name = '单品促销与分类关联'
        verbose_name_plural = verbose_name

#单品促销与商品SKU的关联
class Promotion4Goods_GoodsSKU(BaseModel):
    p4gobj = models.ForeignKey('Promotion4Goods', verbose_name=u'促销按单品', on_delete=models.CASCADE)
    gskuobj = models.ForeignKey('goods.GoodsSKU', verbose_name=u'商品SKU', on_delete=models.CASCADE)
    class Meta:
        db_table = 'df_promotions4goods_goodssku'
        verbose_name = '单品促销与sku关联'
        verbose_name_plural = verbose_name

#按订单促销
class Promotion4Order(Promotion):
    prom_type_order = (
        (0, '包邮'),
        (1, '满折'),
        (2, '满减'),
        #(3, '满赠'),
    )
    # 活动类型
    type = models.SmallIntegerField(default=0, choices=prom_type_order, verbose_name=u'活动类型')
    # 订单金额起点，最多99999
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name=u'订单金额起点')
    # 打折率,例如0.95折
    discount = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, null=True, verbose_name=u'打折率')
    # 减免金额，最多减免9999
    reduct = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True, verbose_name=u'减免金额')

    class Meta:
        db_table = 'df_promotions4order'
        verbose_name = '订单促销'
        verbose_name_plural = verbose_name
