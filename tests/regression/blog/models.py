from django.db import models


class Blog(models.Model):
    class Meta:
        verbose_name_plural = "Blogs"

    title = models.CharField(max_length=255)


class Post(models.Model):
    class Meta:
        verbose_name_plural = "Posts"

    title = models.CharField(max_length=255)
    body = models.TextField()
    blog = models.ForeignKey("Blog", on_delete=models.CASCADE)


class Tag(models.Model):
    class Meta:
        verbose_name_plural = "Tags"

    name = models.CharField(primary_key=True, max_length=255)


class PostTag(models.Model):
    class Meta:
        verbose_name_plural = "PostTags"

    post = models.ForeignKey("Post", primary_key=True, on_delete=models.CASCADE)
    tag = models.ForeignKey("Tag", primary_key=True, on_delete=models.CASCADE)
