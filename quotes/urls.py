from django.urls import path
from .views import PortalView, QuoteCreateView, QuoteListView, QuoteApproveView

app_name = 'quotes'

urlpatterns = [
    # Portal views (External clients)
    path('', PortalView.as_view(), name='portal_home'),
    path('new/', QuoteCreateView.as_view(), name='quote_create'),
    
    # Internal staff views
    path('list/', QuoteListView.as_view(), name='quote_list'),
    path('approve/<int:pk>/', QuoteApproveView.as_view(), name='quote_approve'),
]
