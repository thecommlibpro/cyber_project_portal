"""
URL configuration for portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
import re

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from entrylog.views import daily_log, mark_sticker


#print(settings.MEDIA_URL, settings.MEDIA_ROOT)

urlpatterns = [
    re_path('$', lambda request: redirect('admin/', permanent=False), name='index'),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path("slots/", include("slots.urls")),
    path("members/", include("members.urls")),
    re_path("library/log", daily_log, name="daily_log"),
    path("library/mark_sticker", mark_sticker, name="mark_sticker"),
    re_path(
        r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), serve, kwargs={'document_root':settings.MEDIA_ROOT},
    ),
]
