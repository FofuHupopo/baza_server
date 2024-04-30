from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_title = "Панель администратора"
admin.site.site_header = "Администрирование BAZA"
admin.site.index_title = ""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("api.urls"))
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
