from django.urls import path
from .views import (
    PortalView, QuoteCreateView, QuoteListView, QuoteApproveView, PortalLoginView,
    CardJobOrderCreateView, CardJobOrderDetailView, CardJobOrderListView
)

app_name = 'quotes'

urlpatterns = [
    # Portal views (External clients)
    path('login/', PortalLoginView.as_view(), name='portal_login'),
    path('', PortalView.as_view(), name='portal_home'),
    path('new/', QuoteCreateView.as_view(), name='quote_create'),
    path('card-job/new/', CardJobOrderCreateView.as_view(), name='card_job_create'),
    
    # Internal staff views
    path('list/', QuoteListView.as_view(), name='quote_list'),
    path('approve/<int:pk>/', QuoteApproveView.as_view(), name='quote_approve'),
    path('card-jobs/', CardJobOrderListView.as_view(), name='card_job_list'),
    path('card-job/<int:pk>/', CardJobOrderDetailView.as_view(), name='card_job_detail'),
]
