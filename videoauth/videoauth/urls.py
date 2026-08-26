import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from django.contrib.auth import views as auth_views
from video import views as video_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('video/', include('video.urls')),
    path('', RedirectView.as_view(url='/video/')),
    path('account/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('account/register/', video_views.register, name='register'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

