from django.urls import path
from . import views
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
    path('users/new/', views.PortalCreateUserView.as_view(), name='portal_create_user'),
    path('card-job/new/', CardJobOrderCreateView.as_view(), name='card_job_create'),
    
    # Internal staff views
    path('list/', QuoteListView.as_view(), name='quote_list'),
    path('approve/<int:pk>/', QuoteApproveView.as_view(), name='quote_approve'),
    path('card-jobs/', CardJobOrderListView.as_view(), name='card_job_list'),
    path('card-job/<int:pk>/', CardJobOrderDetailView.as_view(), name='card_job_detail'),
    
    # Workflow transitions
    path('card-job/<int:pk>/submit/', views.CardJobSubmitView.as_view(), name='card_job_submit'),
    path('card-job/<int:pk>/staff-review/', views.CardJobStaffReviewView.as_view(), name='card_job_staff_review'),
    path('card-job/<int:pk>/send-to-client/', views.CardJobSendToClientView.as_view(), name='card_job_send_to_client'),
    path('card-job/<int:pk>/to-production/', views.CardJobToProductionView.as_view(), name='card_job_to_production'),

    # Public approval URL — no login required
    path('aprobar/<uuid:token>/', views.CardJobClientApprovalView.as_view(), name='card_job_approval'),
]
