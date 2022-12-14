from django.contrib import admin
from django.urls import path, include
from api.routers import router
from main.views import Login, Logout
from rest_framework.documentation import include_docs_urls
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include('main.urls')),
    path('login/', Login, name='login'),
    path('logout/', Logout, name='logout'),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title='API | Santexnika')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)