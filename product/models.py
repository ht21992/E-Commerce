from django.contrib.auth.models import User
from django.db import models
from django.core.files import File
from django.template.defaultfilters import slugify
from .utils import get_random_code, get_random_string
from io import BytesIO
from PIL import Image


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=250,
        null=False,
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="It will be populated automatically",
    )
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="uploads/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="uploads/", blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    def get_display_price(self):
        return self.price / 100

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                if self.thumbnail:
                    self.save()
                    return self.thumbnail.url
            else:
                return "https://placehold.co/400x300/png"

    def make_thumbnail(self, image, size=(400, 300)):
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        try:
            img.save(thumb_io, "JPEG", quality=85)
            thumbnail = File(thumb_io, name=image.name)
            return thumbnail
        except OSError:
            return ""

    def get_rating(self):
        reviews_total = 0

        for review in self.reviews.all():
            reviews_total += review.rating

        if reviews_total > 0:
            return reviews_total / self.reviews.count()

        return 0

    def delete(self, using=None, keep_parents=False):
        try:
            storage = self.image.storage
            if storage.exists(self.image.name):
                storage.delete(self.image.name)

            if storage.exists(self.thumbnail.name):
                storage.delete(self.thumbnail.name)
        except AssertionError:
            pass
        except ValueError:
            pass
        super().delete()

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            # Slug field must be unique, so give it a temporary throw-away value
            temp_slug = slugify(f"{get_random_string()}-{self.id},-{get_random_code()}")
            self.slug = temp_slug
            super().save(*args, **kwargs)
            self.slug = slugify(f"{get_random_string()}-{self.id},-{get_random_code()}")
        self.get_thumbnail()
        super().save(*args, **kwargs)


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    rating = models.IntegerField(default=3)
    content = models.TextField()
    created_by = models.ForeignKey(
        User, related_name="reviews", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
