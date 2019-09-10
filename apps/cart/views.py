from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from goods.models import GoodsSKU
from django.views.generic import detail

from promotion.models import Promotion4Order
import pytz
import datetime
import decimal

# Create your views here.
# 前端传递的参数: 商品id(sku_id) 商品数量(count)
# ajax post 请求
# /cart/add
class CartAddView(View):
    """购物车记录添加"""

    def post(self, request):
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 获取参数
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')  # 数字

        # 参数校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验商品id requests urllib
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品信息错误'})

        # 校验商品数量count
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 3, 'errmsg': '商品数量必须为有效数字'})

        # 业务处理: 购物车记录添加
        # 获取redis链接
        conn = get_redis_connection('default')
        # 拼接key
        cart_key = 'cart_%d' % user.id
        # cart_1 : {'1':'3', '2':'5'}
        # hget(key, field)
        cart_count = conn.hget(cart_key, sku_id)

        if cart_count:
            # 如果用户的购物车中已经添加过sku_id商品, 购物车中对应商品的数目需要进行累加
            count += int(cart_count)

        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        # 设置用户购物车中sku_id商品的数量
        # hset(key, field, value)   存在就是修改，不存在就是新增
        conn.hset(cart_key, sku_id, count)

        # 获取用户购物车中商品的条目数
        cart_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res': 5, 'cart_count': cart_count, 'errmsg': '添加购物车记录成功'})


# 购物车页面显示
# get /cart/
class CartInfoView(LoginRequiredMixin, View):
    """购物车页面显示"""

    # starttime: "b'2019-09-06 07:26:00+00:00"
    #将redis里面的日期时间字符串转换成带时区的日期时间
    def parse_mytime(self, s):
        year_s, mon_s, day_s = s[2:12].split('-')
        hour_s, min_s, sec_s = s[13:21].split(':')
        mytime = datetime.datetime(int(year_s), int(mon_s), int(day_s), int(hour_s), int(min_s), int(sec_s))
        mytime = mytime.replace(tzinfo=pytz.timezone('UTC'))
        return mytime

    #订单查优惠
    def checkPromotion4Order(self):
        print("查询订单优惠信息")
        #满折和满减冲突，只能二选一，包邮不冲突
        # 准备用于传递给模板的数据
        bPostFree = 0 #包邮
        fPostFee = 0 #包邮起点金额
        bDiscount = 0 #满折
        fDiscount = 1.0
        fDiscountFee = 0 #满折起点金额
        bReduct = 0 #满减
        fReduct = 0
        fReductFee = 0 #满减起点金额，每够这个金额就减去多少
        starttime = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        starttime = starttime.replace(tzinfo=pytz.timezone('UTC'))
        endtime = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        endtime = endtime.replace(tzinfo=pytz.timezone('UTC'))
        # 下面开始
        n_time = datetime.datetime.utcnow()
        n_time = n_time.replace(tzinfo=pytz.timezone('UTC'))
        # 1、先查包邮的
        search_dict = dict()
        search_dict['status'] = 0  # 状态为启用
        search_dict['type'] = 0  # 包邮
        # 即使后台设置了多个同期促销活动，也只会按顺序选取其中最晚创建的那个
        p4olist = Promotion4Order.objects.filter(**search_dict).order_by('-pk')
        for it in p4olist:
            starttime = it.start_time
            endtime = it.end_time
            if (n_time < starttime) or (n_time >= endtime):
                print("该促销活动尚未开始或者已经结束")
                continue

            #活动仍然当期且最新的那个
            bPostFree = 1
            fPostFee = it.amount
            break

        # 2、再查满折的
        search_dict['status'] = 0  # 状态为启用
        search_dict['type'] = 1  # 满折
        # 即使后台设置了多个同期促销活动，也只会按顺序选取其中最晚创建的那个
        p4olist = Promotion4Order.objects.filter(**search_dict).order_by('-pk')
        for it in p4olist:
            starttime = it.start_time
            endtime = it.end_time
            if (n_time < starttime) or (n_time >= endtime):
                print("该促销活动尚未开始或者已经结束")
                continue

            # 活动仍然当期且最新的那个
            bDiscount = 1
            fDiscount = it.discount
            fDiscountFee = it.amount
            break

        # 3、再查满减的
        search_dict['status'] = 0  # 状态为启用
        search_dict['type'] = 2  # 满减
        # 即使后台设置了多个同期促销活动，也只会按顺序选取其中最晚创建的那个
        p4olist = Promotion4Order.objects.filter(**search_dict).order_by('-pk')
        for it in p4olist:
            starttime = it.start_time
            endtime = it.end_time
            if (n_time < starttime) or (n_time >= endtime):
                print("该促销活动尚未开始或者已经结束")
                continue

            # 活动仍然当期且最新的那个
            bReduct = 1
            fReduct = it.reduct
            fReductFee = it.amount
            break
            
        return bPostFree, fPostFee, bDiscount, fDiscount, fDiscountFee, bReduct, fReduct, fReductFee

    def get(self, request):
        # 获取登录用户
        user = request.user

        # 从redis中获取用户的购物车记录信息
        conn = get_redis_connection('default')

        # 拼接key
        cart_key = 'cart_%d' % user.id

        # cart_1 : {'1':'2', '3':'1', '5':'2'}
        # hgetall(key) -> 返回是一个字典，字典键是商品id, 键对应值是添加的数目
        cart_dict = conn.hgetall(cart_key)

        total_count = 0
        total_amount = 0
        # 遍历获取购物车中商品的详细信息
        skus = []
        for sku_id, count in cart_dict.items():
            # 根据sku_id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)

            #############################################
            #促销拼接key
            prom_key = 'promotion_%d' % int(sku_id)

            n_time = datetime.datetime.utcnow()
            n_time = n_time.replace(tzinfo=pytz.timezone('UTC'))
            # starttime: "2019-09-06 07:26:00+00:00"
            sku.promotion = 0
            sku.hasdiscount = 0
            sku.hasreduct = 0
            if (n_time < self.parse_mytime(str(conn.hget(prom_key, 'starttime')))) or (n_time >= self.parse_mytime(str(conn.hget(prom_key, 'endtime')))):
                print("购物车计算，该促销活动尚未开始或者已经结束")
                # 给sku对象增加促销相关属性
                # 计算商品的小计
                amount = sku.price * int(count)
                print("购物车：amount: %.2f" % amount)
            else:
                # 计算商品的小计
                if int(conn.hget(prom_key, 'bPromotion')):
                    # 给sku对象增加促销相关属性
                    sku.promotion = 1
                    if int(conn.hget(prom_key, 'bDiscount')):
                        sku.hasdiscount = 1
                        print("购物车redis fDiscount：%s" % conn.hget(prom_key, 'fDiscount'))
                        fDiscount = decimal.Decimal(float(conn.hget(prom_key, 'fDiscount')))
                        sku.discount = fDiscount
                        print("购物车：fDiscount: %.2f"%fDiscount)
                        amount = sku.price * int(count) * fDiscount
                        print("购物车：amount: %.2f"%amount)
                    elif int(conn.hget(prom_key, 'bReduct')):
                        sku.hasreduct = 1
                        print("购物车redis fReduct：%s" % conn.hget(prom_key, 'fReduct'))
                        fReduct = decimal.Decimal(float(conn.hget(prom_key, 'fReduct')))
                        sku.reduct = fReduct
                        print("购物车：fReduct: %.2f"%fReduct)
                        amount = (sku.pricecou - fReduct) * int(count)
                        print("购物车：amount: %.2f" % amount)
                else:
                    amount = sku.price * int(count)

            #############################################
            # 给sku对象增加属性amout和count, 分别保存用户购物车中商品的小计和数量
            sku.count = int(count)
            sku.amount = float('%.2f'%amount)

            print("%s-%d" % (sku.name, sku.count))

            # 追加商品的信息
            skus.append(sku)

            # 累加计算用户购物车中商品的总数目和总价格
            total_count += int(count)
            total_amount += float('%.2f'%amount)
            total_amount = float('%.2f'%total_amount)

        #获取订单优惠信息
        orderprom = []
        #包邮，包邮起点金额，满折，满折折扣，满折起点金额，满减，满减金额，满减起点金额
        orderbpost, orderpostfee, orderbdiscount, orderdiscount, orderdiscountfee, orderbreduct, orderreduct, orderreductfee = self.checkPromotion4Order()


        # 组织模板上下文
        context = {
            'total_count': total_count,
            'total_amount': total_amount,
            'skus': skus,
            'orderbpost': orderbpost,
            'orderpostfee': orderpostfee,
            'orderbdiscount': orderbdiscount,
            'orderdiscount': orderdiscount,
            'orderdiscountfee': orderdiscountfee,
            'orderbreduct': orderbreduct,
            'orderreduct': orderreduct,
            'orderreductfee': orderreductfee
        }

        # 使用模板
        return render(request, 'cart.html', context)


# 购物车记录更新
# 前端传递的参数: 商品id(sku_id) 更新数量(count)
# ajax post请求
# /cart/update
class CartUpdateView(View):
    """购物车记录更新"""

    def post(self, request):
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 参数校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验商品id requests urllib
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品信息错误'})

        # 校验商品数量count
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 3, 'errmsg': '商品数量必须为有效数字'})

        # 业务处理: 购物车记录更新
        # 获取链接
        conn = get_redis_connection('default')

        # 拼接key
        cart_key = 'cart_%d' % user.id

        # 校验商品的库存量
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        # 更新用户购物车中商品数量
        # hset(key, field, value)
        conn.hset(cart_key, sku_id, count)

        # 返回应答
        return JsonResponse({'res': 5, 'errmsg': '更新购物车记录成功'})


# 购物车记录删除
# 前端传递的参数: 商品id(sku_id)
# /cart/delete
# ajax post请求
class CartDeleteView(View):
    """购物车记录删除"""

    def post(self, request):
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')

        # 参数校验
        if not all([sku_id]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验商品id requests urllib
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品信息错误'})

        # 业务处理: 删除用户的购物车记录
        # 获取链接
        conn = get_redis_connection('default')

        # 拼接key
        cart_key = 'cart_%d' % user.id

        # 删除记录
        # hdel(key, *fields)
        conn.hdel(cart_key, sku_id)

        # 返回应答
        return JsonResponse({'res': 3, 'errmsg': '删除购物车记录成功'})
