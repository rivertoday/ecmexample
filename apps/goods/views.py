from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.cache import cache
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.views.generic import View
from django_redis import get_redis_connection
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU
from order.models import OrderGoods
from promotion.models import Promotion, Promotion4Goods, Promotion4Goods_GoodsType, Promotion4Goods_GoodsSKU, Promotion4Order
import pytz
import datetime

# Create your views here.
# http://127.0.0.1:8000
# /
class IndexView(View):
    """首页"""

    def get(self, request):
        """显示"""
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')  # None pickle

        if context is None:
            # 获取商品的分类信息
            print('设置首页缓存')
            types = GoodsType.objects.all()

            # 获取首页的轮播商品的信息
            index_banner = IndexGoodsBanner.objects.all().order_by('index')

            # 获取首页的促销活动的信息
            promotion_banner = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品的展示信息
            for category in types:
                # 获取type种类在首页展示的图片商品的信息和文字商品的信息
                # QuerySet
                image_banner = IndexTypeGoodsBanner.objects.filter(category=category, display_type=1).order_by('index')[:4]
                title_banner = IndexTypeGoodsBanner.objects.filter(category=category, display_type=0).order_by('index')[:6]

                # 给type对象增加属性title_banner,image_banner
                # 分别保存type种类在首页展示的文字商品和图片商品的信息
                category.title_banner = title_banner
                category.image_banner = image_banner

                # for itt in category.image_banner:
                #     print(itt.sku)

            # 缓存数据
            context = {
                'types': types,
                'index_banner': index_banner,
                'promotion_banner': promotion_banner,
                'cart_count': 0
            }

            # 设置首页缓存
            # from django.core.cache import cache
            # cache.set('缓存名称', '缓存数据', '缓存有效时间'} pickle
            cache.set('index_page_data', context, 3600)

        # 判断用户用户是否已登录
        cart_count = 0
        #if request.user.is_authenticated():
        if request.user.is_authenticated:
            # 获取redis链接
            conn = get_redis_connection('default')

            print(request.user.id)
            # 拼接key
            cart_key = 'cart_%s' % request.user.id

            # 获取用户购物车中商品的条目数
            # hlen(key)-> 返回属性的数目
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context.update(cart_count=cart_count)

        # 使用模板
        return render(request, 'index.html', context)  # HttpResponse


# 前端向后端传递数据的三种方式:
# 1) get传参。
# 2) post传参。
# 3）url捕获参数。
#
# 前端传递的参数：商品id(sku_id)
# 商品详情页url地址: '/goods/商品id'

#  /goods/商品id
class DetailView(View):
    def checkPromotionByType(self, skutypeid, category):
        print("根据全部或部分商品分类检查")
        # 准备用于传递给模板的数据
        bPromotion = 0
        bDiscount = 0
        fDiscount = 1.0
        bReduct = 0
        fReduct = 0
        starttime = datetime.datetime.utcnow() + datetime.timedelta(days = -1)
        starttime = starttime.replace(tzinfo=pytz.timezone('UTC'))
        endtime = datetime.datetime.utcnow() + datetime.timedelta(days = -1)
        endtime = endtime.replace(tzinfo=pytz.timezone('UTC'))
        #下面开始
        n_time = datetime.datetime.utcnow()
        n_time = n_time.replace(tzinfo=pytz.timezone('UTC'))
        search_dict = dict()
        search_dict['status'] = 0  # 状态为启用
        search_dict['category'] = category  # 覆盖范围为全部商品、商品分类
        #即使后台设置了多个同期促销活动，也只会按顺序选取其中最晚创建的那个
        p4glist = Promotion4Goods.objects.filter(**search_dict).order_by('-pk')
        for it in p4glist:
            starttime = it.start_time
            endtime = it.end_time
            if (n_time < starttime) or (n_time >= endtime):
                print("该促销活动尚未开始或者已经结束")
                continue

            #活动仍然当期
            if (category==0) :#对于覆盖全商品分类来说，无需再检查关联分类
                if (it.type == 0):
                    print("针对全部商品的打折率: %.2f" % it.discount)
                    bDiscount = 1
                    fDiscount = it.discount
                if (it.type == 1):
                    print("针对全部商品的降价：%.2f" % it.reduct)
                    bReduct = 1
                    fReduct = it.reduct
                #设定具有促销后，直接退出
                bPromotion = 1
                break
            else:#对于覆盖部分商品分类来说，则需再检查该商品是否在关联分类里面
                sd = dict()
                sd['p4gobj_id'] = it.id
                pgtlist = Promotion4Goods_GoodsType.objects.filter(**sd)
                for gt in pgtlist:
                    #print("商品分类id：%d" % (gt.gtobj_id))
                    #要找到匹配的分类才行
                    if (skutypeid == gt.gtobj_id):
                        bPromotion = 1
                        break
                if bPromotion:
                    if (it.type == 0):
                        print("针对部分分类商品的打折率: %.2f" % it.discount)
                        bDiscount = 1
                        fDiscount = it.discount
                    if (it.type == 1):
                        print("针对部分分类商品的降价：%.2f" % it.reduct)
                        bReduct = 1
                        fReduct = it.reduct
                    break
        print("Now we confirm: bPromotion:%d, fDiscount:%.2f, fReduct:%.2f"%(bPromotion,fDiscount,fReduct))
        return bPromotion, bDiscount, fDiscount, bReduct, fReduct, starttime, endtime

    def checkPromotionBySKU(self, skuid, category):
        print("根据SKU检查")
        sku_id = int(skuid)
        # 准备用于传递给模板的数据
        bPromotion = 0
        bDiscount = 0
        fDiscount = 1.0
        bReduct = 0
        fReduct = 0
        starttime = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        starttime = starttime.replace(tzinfo=pytz.timezone('UTC'))
        endtime = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        endtime = endtime.replace(tzinfo=pytz.timezone('UTC'))
        #下面开始
        n_time = datetime.datetime.utcnow()
        n_time = n_time.replace(tzinfo=pytz.timezone('UTC'))
        search_dict = dict()
        search_dict['status'] = 0  # 状态为启用
        search_dict['category'] = category  # 覆盖范围为商品SKU
        # 即使后台设置了多个同期促销活动，也只会按顺序选取其中最晚创建的那个
        p4glist = Promotion4Goods.objects.filter(**search_dict).order_by('-pk')
        for it in p4glist:
            starttime = it.start_time
            endtime = it.end_time
            if (n_time < starttime) or (n_time >= endtime):
                print("该促销活动尚未开始或者已经结束")
                continue

            sd = dict()
            sd['p4gobj_id'] = it.id
            pgskulist = Promotion4Goods_GoodsSKU.objects.filter(**sd)
            for gsku in pgskulist:
                print("促销活动里面的商品SKUid：%d" % gsku.gskuobj_id)
                print("参数传递进来的商品SKUid：%d" % sku_id)
                # 要找到匹配的id才行
                if (sku_id == gsku.gskuobj_id):
                    bPromotion = 1
                    break
            if bPromotion:
                if (it.type == 0):
                    print("针对该商品SKU的打折率: %.2f" % it.discount)
                    bDiscount = 1
                    fDiscount = it.discount
                if (it.type == 1):
                    print("针对该商品SKU的降价：%.2f" % it.reduct)
                    bReduct = 1
                    fReduct = it.reduct
                break
        print("Now we confirm: bPromotion:%d, fDiscount:%.2f, fReduct:%.2f"%(bPromotion,fDiscount,fReduct))
        return bPromotion, bDiscount, fDiscount, bReduct, fReduct, starttime, endtime

    def get(self, request, sku_id):
        """显示"""
        # 获取商品的详情信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在，则直接跳回首页
            return redirect(reverse('goods:index'))
        # 获取商品分类信息
        types = GoodsType.objects.all()
        # 获取本商品所在分类id
        myskutypeid = sku.category.id
        print("商品sku所在分类id：%d"%sku.category.id)
        # 获取商品的评论信息
        order_skus = OrderGoods.objects.filter(sku=sku).exclude(comment='').order_by('-update_time')
        # 获取同一SPU的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)
        # 获取同种类的新品信息
        new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[:2]

        ##########################################################################
        # 获取促销信息，有三种情况
        # 1）检查是否有覆盖全部商品的促销活动
        btmpProm1 = 0
        btmpDiscount1 = 0
        ftmpDiscount1 = 1.0
        btmpReduct1 = 0
        ftmpReduct1 = 0
        btmpProm1, btmpDiscount1, ftmpDiscount1, btmpReduct1, ftmpReduct1, starttime1, endtime1 = self.checkPromotionByType(myskutypeid, 0)
        # 2) 检查是否有覆盖部分商品分类的促销活动，此时需要检查本商品是否在该分类中
        btmpProm2 = 0
        btmpDiscount2 = 0
        ftmpDiscount2 = 1.0
        btmpReduct2 = 0
        ftmpReduct2 = 0
        btmpProm2, btmpDiscount2, ftmpDiscount2, btmpReduct2, ftmpReduct2, starttime2, endtime2 = self.checkPromotionByType(myskutypeid, 1)
        # 3) 同时检查是否有覆盖商品sku促销活动，此时需要检查本商品sku是否在清单中
        btmpProm3 = 0
        btmpDiscount3 = 0
        ftmpDiscount3 = 1.0
        btmpReduct3 = 0
        ftmpReduct3 = 0
        btmpProm3, btmpDiscount3, ftmpDiscount3, btmpReduct3, ftmpReduct3, starttime3, endtime3 = self.checkPromotionBySKU(sku_id, 2)

        # 准备用于传递给模板的数据
        bPromotion = 0
        bDiscount = 0
        fDiscount = 1.0
        bReduct = 0
        fReduct = 0
        starttime = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        starttime = starttime.replace(tzinfo=pytz.timezone('UTC'))
        endtime = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        endtime = endtime.replace(tzinfo=pytz.timezone('UTC'))
        #基本逻辑是促销活动不叠加
        #如果本商品属于某个针对该商品SKU的促销活动，以针对该商品SKU的活动优先
        if btmpProm3:
            bPromotion = 1
            bDiscount = btmpDiscount3
            fDiscount = ftmpDiscount3
            bReduct = btmpReduct3
            fReduct = ftmpReduct3
            starttime = starttime3
            endtime = endtime3
        #如果本商品属于某个覆盖部分分类的促销活动，以部分分类次优先
        elif btmpProm2:
            bPromotion = 1
            bDiscount = btmpDiscount2
            fDiscount = ftmpDiscount2
            bReduct = btmpReduct2
            fReduct = ftmpReduct2
            starttime = starttime2
            endtime = endtime2
        # 如果没有，则考虑是否有覆盖全部商品的促销活动
        elif btmpProm1:
            bPromotion = 1
            bDiscount = btmpDiscount1
            fDiscount = ftmpDiscount1
            bReduct = btmpReduct1
            fReduct = ftmpReduct1
            starttime = starttime1
            endtime = endtime1

        ##########################################################################

        # 若用户登录，获取购物车中商品的条目数
        cart_count = 0
        if request.user.is_authenticated:
            # 获取redis链接
            conn = get_redis_connection('default')

            # 拼接key
            cart_key = 'cart_%s' % request.user.id

            # 获取用户购物车中商品的条目数
            # hlen(key)-> 返回属性的数目
            cart_count = conn.hlen(cart_key)

            ###################################
            # 设置促销信息
            prom_key = 'promotion_%s' % sku_id
            # promotion_1:
            # {'bPromotion':'1',
            # 'bDiscount':'1','fDiscount':'0.90',
            # 'bReduct':'0', 'fReduct':'0',
            # 'starttime':'2019-09-06 07:26:00+00:00', 'endtime':'2019-09-09 07:26:00+00:00'}
            conn.hset(prom_key, 'bPromotion', bPromotion)
            conn.hset(prom_key, 'bDiscount', bDiscount)
            conn.hset(prom_key, 'fDiscount', fDiscount)
            conn.hset(prom_key, 'bReduct', bReduct)
            conn.hset(prom_key, 'fReduct', fReduct)
            conn.hset(prom_key, 'starttime', starttime)
            conn.hset(prom_key, 'endtime', endtime)
            ###################################

            # 添加用户的历史浏览记录
            # 拼接key
            history_key = 'history_%d' % request.user.id

            # 先尝试从redis对应列表中移除sku_id
            # lrem(key, count, value) 如果存在就移除，如果不存在什么都不做
            # count = 0 移除所有值为 value 的元素。
            conn.lrem(history_key, 0, sku_id)

            # 把sku_id添加到redis对应列表左侧
            # lpush(key, *args)
            conn.lpush(history_key, sku_id)

            # 只保存用户最新浏览的5个商品的id
            # ltrim(key, start, stop)
            conn.ltrim(history_key, 0, 4)

        # 组织模板上下文
        context = {
            'sku': sku,
            'types': types,
            'order_skus': order_skus,
            'same_spu_skus': same_spu_skus,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'promotion': bPromotion,
            'hasdiscount': bDiscount,
            'discount': fDiscount,
            'hasreduct': bReduct,
            'reduct': fReduct
        }
        # 使用模板
        return render(request, 'detail.html', context)



# 前端传递的参数：种类id(type_id) 页码(page) 排序方式(sort)
# 商品列表页的url地址: '/list/种类id/页码?sort=排序方式'

class ListView(View):
    def get(self, request, type_id, page):
        """type_id 为种类id， page为页码"""
        # 获取种类id对应的商品种类信息,判断是否合法存在
        try:
            category = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在时，直接跳转首页
            return redirect(reverse('goods:index'))
        # 获取所有种类
        types = GoodsType.objects.all()

        # 获取排序顺序
        # sort=price: 按照商品的价格(price)从低到高排序
        # sort=hot: 按照商品的人气(sales)从高到低排序
        # sort=default: 按照默认排序方式(id)从高到低排序
        sort = request.GET.get('sort')

        # 获取type种类的商品信息并排序
        if sort == 'price':
            skus = GoodsSKU.objects.filter(category=category).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(category=category).order_by('-sales')
        else:
            # 按照默认顺序来排序
            sort = 'default'
            skus = GoodsSKU.objects.filter(category=category).order_by('-id')

        # 分页操作
        from django.core.paginator import Paginator
        paginator = Paginator(skus, 5)

        # 处理页码
        page = int(page)

        if page > paginator.num_pages:
            # 默认获取第1页的内容
            page = 1

        # 获取第page页内容, 返回Page类的实例对象
        skus_page = paginator.page(page)

        # 页码处理
        # 如果分页之后页码超过5页，最多在页面上只显示5个页码：当前页前2页，当前页，当前页后2页
        # 1) 分页页码小于5页，显示全部页码
        # 2）当前页属于1-3页，显示1-5页
        # 3) 当前页属于后3页，显示后5页
        # 4) 其他请求，显示当前页前2页，当前页，当前页后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            # 1-num_pages
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            # num_pages-4, num_pages
            pages = range(num_pages - 4, num_pages + 1)
        else:
            # page-2, page+2
            pages = range(page - 2, page + 3)

        # 获取type种类的2个新品信息
        new_skus = GoodsSKU.objects.filter(category=category).order_by('-create_time')[:2]

        # 如果用户登录，获取用户购物车中商品的条目数
        cart_count = 0
        if request.user.is_authenticated:
            # 获取redis链接
            conn = get_redis_connection('default')

            # 拼接key
            cart_key = 'cart_%s' % request.user.id

            # 获取用户购物车中商品的条目数
            # hlen(key)-> 返回属性的数目
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文数据
        context = {
            'type': category,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages
        }

        # 使用模板
        return render(request, 'list.html', context)



