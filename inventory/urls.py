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
from schedule import views as iviews



urlpatterns = [
    path('', home, name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login.html', redirect_field_name=''), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page='/accounts/login/'), name='logout'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), 
    #     name='password_change'),
    # path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), 
    #     name='password_change_done'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name = 'change_password.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name = 'change_password_done.html'), name='password_change_done'),
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
    
    path('stock-receipt', iviews.stock_receipts, name='stock-receipt'),
    path('merchant-supply', iviews.merchant_supply_view, name='merchant-supply'),
    path('<int:pk>/supply-confirm', iviews.merchant_confirm_supply, name='supply-confirm'),
    path('<int:pk>/update-stock', iviews.update_stock_receipt, name='update-stock'),
    
    path('stock-return', iviews.stock_return, name='stock-return'),
    path('merchant-return', iviews.merchant_return_view, name='merchant-return'),
    path('<int:pk>/return-confirm', iviews.merchant_confirm_return, name='return-confirm'),
    path('<int:pk>/update-stock-return', iviews.update_stock_return, name='update-stock-return'),
    
    path('items-issued', iviews.items_issued, name='items-issued'),
    path('dept-receipt', iviews.dept_receipt_view, name='dept-receipt'),
    path('<int:pk>/confirm-dept-receipt', iviews.confirm_dept_receipt, name='confirm-dept-receipt'),
    path('<int:pk>/update-items-issued', iviews.update_items_issued, name='update-items-issued'),
    
    path('items-received', iviews.items_received, name='items-received'),
    path('dept-issue', iviews.dept_return_view, name='dept-issue'),
    path('<int:pk>/confirm-dept-return', iviews.confirm_dept_return, name='confirm-dept-return'),
    path('<int:pk>/update-items-received', iviews.update_items_received, name='update-items-received'),

    # path('<int:pk>/item-view', iviews.view_supply, name='item-view'),
    path('view-stock-use', iviews.view_stock_use, name='view-stock-use'),
    path('view-supply', iviews.control_view_supply, name='view-supply'),
    path('view-return', iviews.control_view_return, name='view-return'),
    path('view-issue', iviews.control_view_issue, name='view-issue'),
    path('view-dept-return', iviews.control_view_dept_return, name='view-dept-return'),
    path('<int:pk>/delete-supply', iviews.control_delete_supply, name='delete-supply'),
    path('<int:pk>/delete-return', iviews.control_delete_return, name='delete-return'),
    path('<int:pk>/delete-issue', iviews.control_delete_issue, name='delete-issue'),
    path('<int:pk>/delete-dept-return', iviews.control_delete_dept_return, name='delete-dept-return'),
    path('create-merchant', iviews.ctrl_create_merchant, name='create-merchant'),
    path('create-staff', iviews.ctrl_create_staff, name='create-staff'),
    path('view-users', iviews.pending_users, name='view-users'),
    path('<int:pk>/activate-user', iviews.activate_user, name='activate-user'),
    path('<int:pk>/delete-user', iviews.delete_user, name='delete-user'),
    path('import-db', iviews.import_db, name='import-db'),
    path('import-format', iviews.import_format, name='import-format'),

    path('staff/signup', iviews.staff_signup, name='staff-signup'),
    path('signup', iviews.merchant_signup, name='signup'),
    
    
]
