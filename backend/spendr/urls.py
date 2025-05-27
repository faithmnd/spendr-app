from django.contrib import admin 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, CategoryViewSet, TransactionViewSet, BudgetViewSet

router = DefaultRouter()
router.register('accounts', AccountViewSet, basename='account')
router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('budgets', BudgetViewSet, basename='budget') 

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('api/', include(router.urls)), 
    path('api/auth/', include('dj_rest_auth.urls')), 
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]