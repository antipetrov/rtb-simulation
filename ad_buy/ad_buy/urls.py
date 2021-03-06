"""ad_buy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings

from ad_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ad/<int:id>/', views.ad_view, name='ad_view'),
    path('ad/<int:id>/preview_json', views.ad_timetable_preview_json, name='ad_timetable_preview'),
    path('ad/<int:id>/report', views.ad_report, name='ad_report'),
    path('ad/<int:id>/timetable/<int:timetable_id>/delete', views.ad_timetable_delete, name='ad_timetable_delete'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns