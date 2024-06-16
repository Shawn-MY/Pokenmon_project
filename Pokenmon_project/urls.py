from django.contrib import admin
from django.urls import path
from pokenmon_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('get_result/', views.get_result, name='get_result'),
]
