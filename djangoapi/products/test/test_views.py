from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from products.models import *
from rest_framework import status
from products.serializers import *

def mocked_data_product(category_name, supplier):
    return {
        'name': 'Produto Teste',
        'description': 'Descrição do produto de teste',
        'price': '37.99',
        'sku': 'TESTE01',
        'category_name': category_name,
        'supplier': supplier
    }

def mocked_product_create():
    supplier = Supplier.objects.create(name="Fornecedor Teste")
    category = Category.objects.create(name="Categoria Teste")
    product1 = Product.objects.create(
        name="Produto Teste 1", 
        description="Produto Teste 1", 
        price="10.99", 
        sku="PROD1", 
        supplier=supplier,
        category=category)
    product2 = Product.objects.create(
        name="Produto Teste 2", 
        description="Descrição do Produto Teste 2", 
        price="20.99", 
        sku="PROD2", 
        supplier=supplier,
        category=category)
    return [product1, product2]

def mocked_user():
    user = User.objects.create_user(username='testuser', password='testpassword')
    return user

#Teste Product Views
class ProductCreateViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('product-create')
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='categoria-teste')
        self.supplier = Supplier.objects.create(name='fornecedor-teste')

    def test_create_product_success(self):
        data = mocked_data_product(self.category.name, self.supplier.id)
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(sku=data['sku']).exists())
        product = Product.objects.get(sku=data['sku'])
        self.assertTrue(PriceHistory.objects.filter(product=product).exists())

class ProductListViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('product-list')
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='categoria-teste')
        self.supplier = Supplier.objects.create(name='fornecedor-teste')
        Product.objects.create(name='Produto Teste 2', description='produto teste 2', price='29.99', sku='TESTE02', category=self.category, supplier=self.supplier)
        Product.objects.create(name='Produto Teste 3', description='produto teste 3', price='45.99', sku='TESTE03', category=self.category, supplier=self.supplier)

    def test_list_products_success(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products_count = Product.objects.count()
        self.assertEqual(len(response.data), products_count)
        skus = {product['sku'] for product in response.data}
        self.assertIn('TESTE02', skus)
        self.assertIn('TESTE03', skus)

class ProductDetailViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='eletronicos')
        self.supplier = Supplier.objects.create(name='fornecedor-teste')
        self.product = Product.objects.create(
            name='Produto Teste',
            description='Produto teste',
            price='10.5',
            sku='TESTE01',
            category=self.category,
            supplier=self.supplier
        )
        self.url = reverse('product-detail', kwargs={'sku': self.product.sku})

    def test_product_detail_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = ProductSerializer(self.product).data
        self.assertEqual(response.data, expected_data)

    def test_product_detail_sku_not_found(self):
        url = reverse('product-detail', kwargs={'sku': 'SKU_INEXISTENTE'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Produto não encontrado."})

class ProductUpdateViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='eletronicos')
        self.supplier = Supplier.objects.create(name='fornecedor-teste')
        self.product = Product.objects.create(
            name='Produto Teste',
            description='Descrição do produto de teste',
            price='37.99',
            sku='TESTE01',
            category=self.category,
            supplier=self.supplier
        )
        self.url = reverse('product-update', kwargs={'sku': self.product.sku})

    def test_product_update_success(self):
        update_data = {
            'name': 'Produto Teste Update',
            'description': 'Produto de teste',
            'price': '47.99',
            'category_name': 'eletronicos'
        }
        response = self.client.patch(self.url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, update_data['name'])
        self.assertEqual(self.product.description, update_data['description'])
        self.assertEqual(float(self.product.price), float(update_data['price']))
        self.assertEqual(self.product.category.name, update_data['category_name'].lower())

    def test_product_update_sku_not_found(self):
        url = reverse('product-update', kwargs={'sku': 'sku-teste'})
        update_data = {'name': 'Nome Atualizado'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_update_category_not_found(self):
        update_data = {
            'category_name': 'categoria inexistente'
        }
        response = self.client.patch(self.url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": f"Categoria '{update_data['category_name']}' não encontrada."})

class ProductDeleteViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='eletronicos')
        self.supplier = Supplier.objects.create(name='fornecedor-teste')
        self.product = Product.objects.create(
            name='Produto Teste',
            description='Descrição do produto de teste',
            price='37.99',
            sku='TESTE01',
            category=self.category,
            supplier=self.supplier
        )
        self.url = reverse('product-delete', kwargs={'sku': self.product.sku})

    def test_product_delete_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(sku='TESTE01').exists())

    def test_product_delete_not_found(self):
        url = reverse('product-delete', kwargs={'sku': 'SKU_INEXISTENTE'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_delete_with_stock(self):
        ProductStock.objects.update_or_create(product=self.product, defaults={'quantity': 10})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Não é possível deletar produtos com saldo."})
        self.assertTrue(Product.objects.filter(sku='TESTE01').exists())

#Testes Category Views
class CategoryListViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.category1 = Category.objects.create(name='Eletrodomésticos')
        self.category2 = Category.objects.create(name='Livros')
        self.category3 = Category.objects.create(name='Roupas')
        self.url = reverse('category-list')

    def test_list_categories_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        expected_data = CategorySerializer([self.category1, self.category2, self.category3], many=True).data
        self.assertEqual(response.data, expected_data)

class CategoryCreateViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.parent_category = Category.objects.create(name='Tecnologia')
        self.url = reverse('category-create')

    def test_create_category_success(self):
        data = {
            'name': 'Eletrônicos',
            'parent_name': 'Tecnologia'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name=data['name'].lower()).exists())
        self.assertEqual(Category.objects.get(name=data['name'].lower()).parent, self.parent_category)

    def test_create_category_duplicate_name(self):
        data = {'name': 'Jogos'}
        self.client.post(self.url, data, format='json')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_category_parent_not_found(self):
        data = {
            'name': 'Consoles',
            'parent_name': 'Teste'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

class CategoryDeleteViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Eletrônicos')
        self.category_with_product = Category.objects.create(name='Livros')
        Product.objects.create(
            name='Produto Teste', 
            description='Produto teste', 
            price='25.99', 
            sku='LIVRO123', 
            category=self.category_with_product)
        self.url = lambda category_name: reverse('category-delete', kwargs={'name': category_name})

    def test_delete_category_success(self):
        response = self.client.delete(self.url(self.category.name))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(name=self.category.name).exists())

    def test_delete_category_not_found(self):
        response = self.client.delete(self.url('categoria-teste'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_category_with_product(self):
        response = self.client.delete(self.url(self.category_with_product.name))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertTrue(Category.objects.filter(name=self.category_with_product.name).exists())

#Testes Supplier Views
def mocked_data_supplier():
    return Supplier.objects.create(
        name='Fornecedor teste', 
        description='fornecedor teste', 
        contact_info='92999999999'
    )
class SupplierListViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        Supplier.objects.create(name='Fornecedor 1')
        Supplier.objects.create(name='Fornecedor 2')
        self.url = reverse('supplier-list')

    def test_list_suppliers(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suppliers_count = Supplier.objects.count()
        self.assertEqual(len(response.data), suppliers_count)
        expected_data = SupplierSerializer(Supplier.objects.all(), many=True).data
        self.assertEqual(response.data, expected_data)

class SupplierCreateViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('supplier-create')

    def test_create_supplier_success(self):
        data = {
            'name': 'Fornecedor Teste',
            'description': 'fornecedor teste',
            'contact_info': '92999999999'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supplier_id = response.data['id']
        self.assertTrue(Supplier.objects.filter(id=supplier_id).exists())

    def test_create_supplier_invalid_data(self):
        data = {
            'name': ''
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SupplierDetailViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.supplier = mocked_data_supplier()
        self.url = reverse('supplier-detail', kwargs={'pk': self.supplier.pk})

    def test_supplier_detail_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = SupplierSerializer(self.supplier).data
        self.assertEqual(response.data, expected_data)

    def test_supplier_detail_not_found(self):
        url = reverse('supplier-detail', kwargs={'pk': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Fornecedor não encontrado."})

class SupplierUpdateViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.supplier = mocked_data_supplier()
        self.url = reverse('supplier-update', kwargs={'pk': self.supplier.pk})

    def test_supplier_update_success(self):
        update_data = {
            'name': 'Fornecedor Teste Update',
        }
        response = self.client.patch(self.url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, update_data['name'])

    def test_supplier_update_not_found(self):
        url = reverse('supplier-update', kwargs={'pk': 999999})
        response = self.client.patch(url, {'name': 'Fornecedor Inexistente'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_supplier_update_invalid_data(self):
        invalid_data = {'name': ''}
        response = self.client.patch(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SupplierDeleteViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.supplier = mocked_data_supplier()
        
    def test_delete_supplier_success(self):
        url = reverse('supplier-delete', kwargs={'pk': self.supplier.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Supplier.objects.filter(pk=self.supplier.pk).exists())

    def test_delete_supplier_not_found(self):
        url = reverse('supplier-delete', kwargs={'pk': 999999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_supplier_with_products(self):
        Product.objects.create(
            name="Produto Teste", 
            description="Descrição do Produto", 
            price="10.99", 
            sku="PROD001", 
            supplier=self.supplier)
        url = reverse('supplier-delete', kwargs={'pk': self.supplier.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertTrue(Supplier.objects.filter(pk=self.supplier.pk).exists())

#Testes Stock Views
class StockListViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.product1,self.product2 = mocked_product_create()
        ProductStock.objects.update_or_create(product=self.product1,defaults={'quantity': 100})
        ProductStock.objects.update_or_create(product=self.product2,defaults={'quantity': 200})
        self.url = reverse('stock-list')

    def test_list_product_stocks_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        expected_data = ProductStockSerializer(ProductStock.objects.all(), many=True).data
        self.assertEqual(response.data, expected_data)

class StockDetailViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.product = mocked_product_create()[0]
        self.product_stock, _ = ProductStock.objects.update_or_create(product=self.product, defaults={'quantity': 100})
        self.url = lambda sku: reverse('stock-detail', kwargs={'sku': sku})

    def test_stock_detail_success(self):
        response = self.client.get(self.url(self.product.sku))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"sku": self.product.sku, "stock": self.product_stock.quantity}
        self.assertEqual(response.data, expected_data)

    def test_stock_detail_product_not_found(self):
        response = self.client.get(self.url("sku-teste"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class StockUpdateViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.product = mocked_product_create()[0]
        self.product_stock, _ = ProductStock.objects.update_or_create(product=self.product, defaults={'quantity': 100})
        self.url = lambda sku: reverse('stock-update', kwargs={'sku': sku})

    def test_stock_update_success(self):
        update_data = {'quantity': 150}
        response = self.client.patch(self.url(self.product.sku), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_stock.refresh_from_db()
        self.assertEqual(self.product_stock.quantity, 150)

    def test_stock_update_product_not_found(self):
        update_data = {'quantity': 150}
        response = self.client.patch(self.url("sku-teste"), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_stock_update_invalid_quantity(self):
        update_data = {'quantity': -10}
        response = self.client.patch(self.url(self.product.sku), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#Teste Rating Views
class ReviewCreateViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.product = mocked_product_create()[0]
        self.url = reverse('review-create')

    def test_create_review_success(self):
        data = {
            'product_sku': self.product.sku,
            'rating': 5,
            'comment': 'Otimo produto'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(product=self.product, user=self.user).exists())
        review = Review.objects.get(product=self.product, user=self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Otimo produto')

    def test_create_review_invalid_data(self):
        data = {
            'product': self.product.id,
            'rating': 11,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Review.objects.filter(product=self.product, user=self.user).exists())

#Testes Rating Views
class ProductRatingDetailViewTest(APITestCase):
    def setUp(self):
        self.user = mocked_user()
        self.client.force_authenticate(user=self.user)
        self.product, self.product_no_rating = mocked_product_create()
        Review.objects.create(product=self.product, rating=5, comment='comentario teste 1', user=self.user)
        Review.objects.create(product=self.product, rating=6, comment='comentario teste 2', user=self.user)
        Review.objects.create(product=self.product, rating=7, comment='comentario teste 3', user=self.user)
        self.product_rating = ProductRating.objects.get(product=self.product)
        self.url = lambda sku: reverse('product-rating-detail', kwargs={'sku': sku})

    def test_product_rating_detail_success(self):
        response = self.client.get(self.url(self.product.sku))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "sku": self.product.sku,
            "average_rating": self.product_rating.average_rating,
            "ratings_count": self.product_rating.ratings_count
        }
        self.assertEqual(response.data, expected_data)

    def test_product_rating_detail_product_not_found(self):
        response = self.client.get(self.url("sku-teste"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_rating_detail_rating_not_found(self):
        response = self.client.get(self.url(self.product_no_rating.sku))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)