from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, ProductStock, PriceHistory, Review, ProductRating

@receiver(post_save, sender=Product)
def create_product_stock(sender, instance, created, **kwargs):
    if created:
        ProductStock.objects.create(product=instance, quantity=0)


@receiver(post_save, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    reviews = Review.objects.filter(product=product)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    ratings_count = reviews.count()

    ProductRating.objects.update_or_create(
        product=product,
        defaults={'average_rating': average_rating or 0.00, 'ratings_count': ratings_count}
    )

@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    product = instance.product
    reviews = Review.objects.filter(product=product)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    ratings_count = reviews.count()

    ProductRating.objects.update_or_create(
        product=product,
        defaults={'average_rating': average_rating or 0.00, 'ratings_count': ratings_count}
    )