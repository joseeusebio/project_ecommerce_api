from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Product, ProductStock, Review, Category, Supplier

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductStockSerializer(serializers.ModelSerializer):
    product_sku = serializers.SerializerMethodField()

    class Meta:
        model = ProductStock
        fields = ['product_sku', 'quantity']

    def get_product_sku(self, obj):
        return obj.product.sku

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("A quantidade não pode ser negativa.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    is_subcategory = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'is_subcategory', 'parent_category']
    
    def get_is_subcategory(self, obj):
        return obj.parent is not None

    def get_parent_category(self, obj):
        if obj.parent:
            return obj.parent.name
        return None

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
    

class ReviewSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(write_only=True)

    class Meta:
        model = Review
        fields = ['product_sku', 'user', 'rating', 'comment', 'review_date']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        product_sku = validated_data.pop('product_sku')
        product = get_object_or_404(Product, sku=product_sku)
        validated_data['product'] = product
        review = Review.objects.create(**validated_data)
        return review