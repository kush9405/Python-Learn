#type:ignore
"""
URL configuration for Wakefit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from accounts.views import RegisterView
from django.contrib import admin
from django.urls import include, path
from orders import views
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)


urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. JWT AUTH (Move these to the top of the 'api' section)
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='auth_register'),

    # 2. APP APIS
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),

    # 3. BROWSABLE API LOGIN (Keep this at the bottom)
    path('api-auth/', include('rest_framework.urls')),
]
# urlpatterns = [
#     path('api/accounts/', include('accounts.urls')),
# ]
