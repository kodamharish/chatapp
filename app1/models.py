from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=8)
    name = models.CharField(max_length=40)
    email = models.EmailField()
    def __str__(self):
        return self.username


class Admin(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=8)
    name = models.CharField(max_length=40)
    email = models.EmailField()
    def __str__(self):
        return self.username
    

class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queries')
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')

    def __str__(self):
        return f"Query by {self.user.username}"


class Response(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='responses')
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response by {self.admin.username} to {self.query.user.username}"

