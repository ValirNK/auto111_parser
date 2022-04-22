from django.contrib import admin
from .models import Result_8, Needs_8, User

# Register your models here.
class Needs_8Admin(admin.ModelAdmin):
    model = 'Needs_8'
    list_display = ('id_1c_part', 'id_1c_doc', 'part_sought', 'brand_sought', 'status')
    search_fields = ['status']

class Result_8Admin(admin.ModelAdmin):
    model = 'Result_8'
    list_display = ('part_sought', 'title', 'brand_result', 'supplier', 'price', 'qty', 'day', 'location', 'source')

class UserAdmin(admin.ModelAdmin):
    model = 'User'
    list_display = ('username', 'password', 'proxy')

admin.site.register(Needs_8, Needs_8Admin)
admin.site.register(Result_8, Result_8Admin)
admin.site.register(User, UserAdmin)