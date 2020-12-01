"""migrate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from web.views import *
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', RedirectView.as_view(url='/signup')),
    re_path(r'^login/', web_login, name='web_login'),
    re_path(r'^logout/', logout_view, name='logout'),
    re_path(r'^accounts/profile/', account_profile, name='account_profile'),
    re_path(r'^auto_login/', auto_login, name='autologin'),
    re_path(r'^signup/$', signup_view, name='web3auth_signup'),
    re_path(r'^login_api/$', login_api, name='web3auth_login_api'),
    re_path(r'^signup_api/$', signup_api, name='web3auth_signup_api'),
    re_path(r'^page_data_api/$', pageDataApi, name='page_data_api'),
    re_path(r'^log/wallet_notify$', wallet_notify, name='wallet_notify'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
