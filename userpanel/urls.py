from django.urls import path
from django.conf.urls.static import static
from . import views
from django.conf import settings

app_name = 'userpanel'

urlpatterns = [
    path('',views.indexpage, name = 'index'),
    path('dashboard',views.dashboard, name = 'dashboard'),
    path('request_code',views.request_code, name = 'request_code'),
    path('unused_codes',views.unused_codes, name = 'unused_codes'),
    path('used_codes',views.used_codes, name = 'used_codes'),
    path('obtain_earnings',views.obtain_earnings, name = 'obtain_earnings'),
    path('evacuate',views.evacuate, name = 'evacuate'),
    path('new_referral',views.new_referral, name = 'new_referral'),
    path('my_referrals',views.my_referrals, name = 'my_referrals'),
    path('new_ticket',views.new_ticket, name = 'new_ticket'),
    path('all_tickets',views.all_tickets, name = 'all_tickets'),
    path('kyc',views.kyc, name = 'kyc'),
    path('profile',views.Profile, name = 'profile'),
    path('closing',views.closing, name = 'closing'),

    path('topup_account',views.topup_account, name = 'topup_account'),

    path('loginUser',views.loginUser, name = 'loginUser'),
    path('logoutuser',views.logoutUser, name = 'logouruser'),
    path('validate_username', views.validate_username, name='validate_username'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)