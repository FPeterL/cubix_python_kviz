from django.contrib import admin
from django.urls import path
from quiz.views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
]
