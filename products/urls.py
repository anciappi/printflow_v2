from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('catalogo/', views.ProductCatalogView.as_view(), name='catalog'),
    path('nuevo/', views.ProductCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ProductUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ProductDeleteView.as_view(), name='delete'),
    path('document/<int:pk>/eliminar/', views.ProductDocumentDeleteView.as_view(), name='document-delete'),
]