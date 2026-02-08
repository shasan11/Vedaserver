from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/assessments/', include('assessments.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/communication/', include('communication.urls')),
    path('api/content/', include('content.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/enrollments/', include('enrollments.urls')),
    path('api/organization/', include('organization.urls')),
    path('api/progress/', include('progress.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/support/', include('support.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
