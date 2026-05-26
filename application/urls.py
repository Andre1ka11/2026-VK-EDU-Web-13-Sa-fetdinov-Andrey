from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found, server_error

handler404 = 'application.urls.handler404_view'
handler500 = 'application.urls.handler500_view'


def handler404_view(request, exception=None):
    return page_not_found(request, exception, template_name='404.html')


def handler500_view(request):
    return server_error(request, template_name='500.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('questions.urls')),
    path('', include('core.urls')),
]

# Подключаем debug-toolbar только в режиме отладки
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Подключаем медиафайлы (для загрузки аватаров и т.д.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)