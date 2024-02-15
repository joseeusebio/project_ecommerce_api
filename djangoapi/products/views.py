from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, ProductStock, Review, Supplier, Category, PriceHistory, ProductRating
from .serializers import ProductSerializer, ProductStockSerializer, ReviewSerializer, CategorySerializer, SupplierSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated

#Views Product
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        category_name = data.get('category_name', "sem categoria").lower()

        try:
            if category_name:
                category = Category.objects.get(name=category_name)
            else:
                category, _ = Category.objects.get_or_create(name="sem categoria")
            data['category'] = category.pk
        except ObjectDoesNotExist:
            return Response({"error": f"Categoria '{category_name}' não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save() 
            
            old_price = 0
            new_price = serializer.validated_data.get('price', 0)
            
            PriceHistory.objects.create(
                product=product, 
                old_price=old_price, 
                new_price=new_price, 
                user=request.user
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, sku, format=None):
        try:
            product = Product.objects.get(sku=sku)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, sku, format=None):
        try:
            product = Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            return Response({"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        category_name = request.data.get('category_name')
        if category_name is not None:
            try:
                category = Category.objects.get(name=category_name.lower())
                product.category = category
            except Category.DoesNotExist:
                return Response({"error": f"Categoria '{category_name}' não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data.pop('category_name', None)
        old_price = product.price
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            new_price = serializer.instance.price
            if old_price != new_price:
                PriceHistory.objects.create(product=product,old_price=old_price,new_price=new_price,user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, sku, format=None):
        try:
            product = Product.objects.get(sku=sku)
            if ProductStock.objects.filter(product=product, quantity__gt=0).exists():
                return Response({"error": "Não é possível deletar produtos com saldo."}, status=status.HTTP_400_BAD_REQUEST)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

#Views Category
class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        name = data.get('name', '').lower()
        
        if Category.objects.filter(name=name).exists():
            return Response({"error": f"A categoria '{name}' já existe."}, status=status.HTTP_400_BAD_REQUEST)
        
        parent_name = data.get('parent_name', '').lower()
        if parent_name:
            try:
                parent = Category.objects.get(name=parent_name)
                data['parent'] = parent.id
            except Category.DoesNotExist:
                return Response({"error": f"Categoria pai '{parent_name}' não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        else:
            data.pop('parent_name', None)

        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, name, format=None):
        try:
            category = Category.objects.get(name=name)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"error": "Categoria não encontrada."}, status=status.HTTP_404_NOT_FOUND)

class CategoryUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, name, format=None):
        try:
            category = Category.objects.get(name=name.lower())
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({"error": "Categoria não encontrada."}, status=status.HTTP_404_NOT_FOUND)

class CategoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, name, format=None):
        try:
            category = Category.objects.get(name=name)
            if Product.objects.filter(category=category).exists():
                return Response({"error": "Não é possível deletar categorias associadas a produtos."}, status=status.HTTP_400_BAD_REQUEST)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"error": "Categoria não encontrada."}, status=status.HTTP_404_NOT_FOUND)

#Views Supplier
class SupplierListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

class SupplierCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupplierDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, *args, **kwargs):
        try:
            supplier = Supplier.objects.get(pk=pk)
            serializer = SupplierSerializer(supplier)
            return Response(serializer.data)
        except Supplier.DoesNotExist:
            return Response({"error": "Fornecedor não encontrado."}, status=status.HTTP_404_NOT_FOUND)

class SupplierUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk, *args, **kwargs):
        try:
            supplier = Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return Response({"error": "Fornecedor não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SupplierDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk, *args, **kwargs):
        try:
            supplier = Supplier.objects.get(pk=pk)
            if supplier.product_set.exists():
                return Response({"error": "Não é possível deletar fornecedores vinculados a produtos."}, status=status.HTTP_400_BAD_REQUEST)
            
            supplier.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Supplier.DoesNotExist:
            return Response({"error": "Fornecedor não encontrado."}, status=status.HTTP_404_NOT_FOUND)

#Views Stock
class StockListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        product_stocks = ProductStock.objects.all()
        serializer = ProductStockSerializer(product_stocks, many=True)
        return Response(serializer.data)

class StockDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, sku, format=None):
        try:
            product = Product.objects.get(sku=sku)
            product_stock = ProductStock.objects.get(product=product)
            return Response({"sku": sku, "stock": product_stock.quantity})
        except Product.DoesNotExist:
            return Response({"error": f"Produto com SKU {sku} não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except ProductStock.DoesNotExist:
            return Response({"error": f"Estoque não encontrado para o produto com SKU {sku}."}, status=status.HTTP_404_NOT_FOUND)
    
class StockUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, sku, format=None):
        product = Product.objects.filter(sku=sku).first()
        if not product:
            return Response({"error": f"Produto com SKU {sku} não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        product_stock, created = ProductStock.objects.get_or_create(product=product)
        data = {'quantity': request.data.get('quantity')}
        serializer = ProductStockSerializer(product_stock, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#Views Review
class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#Views Product Rating
class ProductRatingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, sku, format=None):
        try:
            product = Product.objects.get(sku=sku)
            product_rating = ProductRating.objects.get(product=product)
            return Response({
                "sku": sku,
                "average_rating": product_rating.average_rating,
                "ratings_count": product_rating.ratings_count
            })
        except Product.DoesNotExist:
            return Response({"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except ProductRating.DoesNotExist:
            return Response({"error": "Avaliação do produto não encontrada."}, status=status.HTTP_404_NOT_FOUND)