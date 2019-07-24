from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


# Register your models here.
class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    verbose_name = u'收货地址'

class MyUserAdmin(UserAdmin):
    """用户模型admin管理类"""
    fieldsets = [
        (None, {'fields': ['username', 'first_name', 'last_name', 'email','password',
                           'is_staff','is_active','is_superuser',
                           'date_joined','last_login']}),
    ]
    inlines = [AddressInline]
    list_display = ('username', 'first_name', 'last_name', 'email', 'last_login')
    list_filter = ['username']
    search_fields = ['username', 'first_name', 'last_name', 'email']

admin.site.register(User, MyUserAdmin)

admin.site.site_header = u'凤凰茶城管理后台'
admin.site.site_title = u'凤凰茶城管理后台'
