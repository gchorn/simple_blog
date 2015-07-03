from django.db import models
from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.auth.models import User


class Category(models.Model):
    """
    A model for categorizing blog posts.  Each blog post (meaning each instance of the model Post)
    has a category to which is related by ForeignKey.  Categories are very simple, they consist only
    of a name.
    """
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __unicode__(self):
        return self.name
    

class Post(models.Model):
    """
    The meat and bones of the blog app.  Instances of this model are individual blog posts with
    basic attributes such as a title, author (which is a ForeignKey to Django's own User model),
    and text.  They also have some useful additional attributes such as a category (ForeignKey 
    to Category model), a date/time published, and a custom URL field (if left blank, the URL for
    each post will default to a slugified version of the post's title).
    """
    title = models.CharField(max_length=1000)
    published = models.BooleanField(default=False)
    custom_url = models.CharField(max_length=1000,blank=True)
    author = models.ForeignKey(User)
    pub_date = models.DateTimeField('date published')
    text = models.TextField(max_length=10000)
    category = models.ForeignKey(Category)
    
    def __unicode__(self):
        return self.title
        
            
class Tag(models.Model):
    """
    A simple model which has a ForeignKey relationship to the Post model in order to provide the 
    blog author(s) with as many tags per post as they wish.  Tags simply consist of a name and a
    key to the post to which they belong.
    """
    post = models.ForeignKey(Post)
    name = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.name


class Image(models.Model):
    """
    A model that allows the blog author(s) to add images to each blog post.  As this model is
    related to a specific Post instance by ForeignKey, each post can have as many associated
    Image objects as the author wants.  There are optional name and caption fields.
    """
    post = models.ForeignKey(Post, related_name='images')
    name = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to='photos/%Y/%m/%d')
    caption = models.CharField(max_length=1000,blank=True)
    
    def __unicode__(self):
        return self.name
    

class PostModerator(CommentModerator):
    """
    An subclass of CommendModerator that makes all comments subject to moderation immediately
    after they are posted.
    """
    email_notification = False
    auto_moderate_field = 'pub_date'
    moderate_after = 0
    

moderator.register(Post,PostModerator)