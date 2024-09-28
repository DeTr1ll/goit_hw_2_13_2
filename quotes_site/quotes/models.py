from django.db import models
from django.contrib.auth.models import AbstractUser

class Author(models.Model):
    _id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    born_date = models.TextField(null=True, blank=True)
    born_location = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    @property
    def id(self):
        return self._id
    
    def __str__(self):
        return self.fullname

class Quote(models.Model):
    _id = models.AutoField(primary_key=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE) 
    quote = models.TextField()
    tags = models.JSONField(default=list)

    class Meta:
        db_table = 'quotes_quote'

    def __str__(self):
        return f'"{self.quote}" — {self.author.name}'
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
