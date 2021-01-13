"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path

from .views import home#, login, logout
from schedule.views import (
    merchant_supply_view, merchant_return_view, stock_receipts, 
    merchant_confirm_supply, stock_return, items_issued, items_received, 
    dept_receipt_view, dept_return_view, merchant_confirm_return, view_supply, 
    update_stock_receipt, update_stock_return, confirm_dept_receipt)

urlpatterns = [
    path('', home, name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login.html', redirect_field_name=''), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page='/accounts/login/'), name='logout'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), 
        name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), 
        name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), 
        name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), 
        name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), 
        name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), 
        name='password_reset_done'),
    # re_path(r'^admin/reset-password/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/
    # (?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(), 
    #   name='password_reset_confirm'),
    path('admin/reset-password/confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin/reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),
    path('admin/', admin.site.urls),
    path('merchant-supply', merchant_supply_view, name='merchant-supply'),
    path('merchant-return', merchant_return_view, name='merchant-return'),
    path('stock-receipt', stock_receipts, name='stock-receipt'),
    path('<int:pk>/supply-confirm', merchant_confirm_supply, name='supply-confirm'),
    path('<int:pk>/return-confirm', merchant_confirm_return, name='return-confirm'),
    path('<int:pk>/update-stock', update_stock_receipt, name='update-stock'),
    path('<int:pk>/update-stock-return', update_stock_return, name='update-stock-return'),
    path('<int:pk>/item-view', view_supply, update_stock_receipt, name='item-view'),
    path('stock-return', stock_return, name='stock-return'),
    path('items-issued', items_issued, name='items-issued'),
    path('items-received', items_received, name='items-received'),
    path('dept-issue', dept_return_view, name='dept-issue'),
    path('dept-receipt', dept_receipt_view, name='dept-receipt'),
    path('<int:pk>/confirm-dept-receipt', confirm_dept_receipt, name='confirm-dept-receipt'),
    # path('inventory/', include('inventory.urls')) call urls from here
]
