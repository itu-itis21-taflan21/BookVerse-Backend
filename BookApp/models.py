from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    book_count = models.IntegerField()

    def __str__(self) :
        return self.name
    
class Author(models.Model):
    name = models.CharField(max_length=50)
    book_count = models.IntegerField()
    average_rating = models.FloatField()
    favorite_book_count = models.IntegerField()

    def __str__(self) :
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=50)
    summary = models.TextField()
    page_count = models.IntegerField()
    author = models.ForeignKey(Author, related_name='books',on_delete=models.CASCADE) 
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    pdf_link = models.CharField(max_length=255, blank=True)
    cover = models.CharField(max_length=255, blank=True)

    def __str__(self) :
        return self.title
