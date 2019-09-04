from django import template
from django.utils.safestring import mark_safe

register = template.Library()  # register的名字是固定的,不可改变
# 以上内容是固定格式。

@register.filter  # 定义一个过滤器
def filter_multi(x, y):  # 实现一个简单的乘法函数
    return x * y

@register.filter  # 定义一个过滤器
def filter_plus(x, y):  # 实现一个简单的加法函数
    return x + y

@register.filter  # 定义一个过滤器
def filter_minus(x, y):  # 实现一个简单的减法函数
    return x - y

@register.simple_tag  # 定义一个标签
def multi(x, y):
    return x * y