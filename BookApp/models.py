from django.db import models
from django.contrib.auth.models import User



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    book_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255)
    book_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    fav_book_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,related_name="books")
    summary = models.TextField()
    cover = models.CharField(max_length=455,default='null')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    page_count = models.IntegerField()
    pdf_link = models.CharField(max_length=455)

    def __str__(self):
        return self.title


class FavBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'user')


class ReadList(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'user')


class UserComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.name} on {self.book.title}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = ('user', 'book')
