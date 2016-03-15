from django.db import models


class Tag(models.Model):
    name = models.CharField(primary_key=True, max_length=255)


class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)


class Blog(models.Model):
    title = models.CharField(max_length=255)


class PostTag(models.Model):
    post = models.ForeignKey('Post', primary_key=True, on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', primary_key=True, on_delete=models.CASCADE)
