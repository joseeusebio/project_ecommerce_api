from django.urls import re_path
from .views import ProductCreateView, ProductListView, ProductDetailView, ProductDeleteView, ProductUpdateView
from .views import CategoryCreateView, CategoryListView, CategoryUpdateView, CategoryDetailView, CategoryDeleteView
from .views import SupplierCreateView, SupplierListView, SupplierDetailView, SupplierUpdateView, SupplierDeleteView
from .views import StockDetailView, StockUpdateView, StockListView
from .views import ReviewCreateView, ProductRatingDetailView

urlpatterns = [
    re_path(r'^product/create/$', ProductCreateView.as_view(), name='product-create'),
    re_path(r'^product/list/$', ProductListView.as_view(), name='product-list'),    
    re_path(r'^product/detail/(?P<sku>[\w-]+)/$', ProductDetailView.as_view(), name='product-detail'),
    re_path(r'^product/update/(?P<sku>[\w-]+)/$', ProductUpdateView.as_view(), name='product-update'),
    re_path(r'^product/delete/(?P<sku>[\w-]+)/$', ProductDeleteView.as_view(), name='product-delete'),

    re_path(r'^category/create/$', CategoryCreateView.as_view(), name='category-create'),
    re_path(r'^category/list/$', CategoryListView.as_view(), name='category-list'),
    re_path(r'^category/detail/(?P<name>[\w-]+)/$', CategoryDetailView.as_view(), name='category-detail'),
    re_path(r'^category/update/(?P<name>[\w-]+)/$', CategoryUpdateView.as_view(), name='category-update'),
    re_path(r'^category/delete/(?P<name>[\w-]+)/$', CategoryDeleteView.as_view(), name='category-delete'),

    re_path(r'^supplier/list/$', SupplierListView.as_view(), name='supplier-list'),
    re_path(r'^supplier/create/$', SupplierCreateView.as_view(), name='supplier-create'),
    re_path(r'^supplier/detail/(?P<pk>\d+)/$', SupplierDetailView.as_view(), name='supplier-detail'),
    re_path(r'^supplier/update/(?P<pk>\d+)/$', SupplierUpdateView.as_view(), name='supplier-update'),
    re_path(r'^supplier/delete/(?P<pk>\d+)/$', SupplierDeleteView.as_view(), name='supplier-delete'),

    re_path(r'^stock/list/$', StockListView.as_view(), name='stock-list'),
    re_path(r'^stock/detail/(?P<sku>[\w-]+)/$', StockDetailView.as_view(), name='stock-detail'),
    re_path(r'^stock/update/(?P<sku>[\w-]+)/$', StockUpdateView.as_view(), name='stock-update'),

    re_path(r'^review/create/$', ReviewCreateView.as_view(), name='review-create'),

    re_path(r'^product/rating/(?P<sku>[\w-]+)/$', ProductRatingDetailView.as_view(), name='product-rating-detail'),
]
