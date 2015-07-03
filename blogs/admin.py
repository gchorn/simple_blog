from django.contrib import admin
from django.contrib.admin import site, ModelAdmin
from django.contrib.comments.models import Comment
from django.contrib.comments.admin import CommentsAdmin

from django.db import models

from tinymce.widgets import TinyMCE

from blogs.models import Post,Image,Tag,Category


class PostImageInline(admin.TabularInline):
    model = Image
    extra = 5
    

class TagInline(admin.TabularInline):
    model = Tag
    extra = 5


class PostAdmin(admin.ModelAdmin):
    """
    This is the admin form blog authors will use to write and edit blog posts.  It includes two TabularInline
    sections, one for images to add to the post and one for tags to add to the post.
    """
    formfield_overrides = {
        models.TextField: {'widget':TinyMCE(attrs={'cols':100,'rows':30})}
    }
    inlines = [PostImageInline, TagInline]

admin.site.register(Category)
admin.site.register(Post, PostAdmin)


class CustomCommentsAdmin(CommentsAdmin):
    """
    This is the admin form that blog authors or admins will use to moderate comments posted to the blog.
    They simply check the box that says "Is public" in order to approve a comment; otherwise the comment
    will not appear on the blog.
    """
    list_display = ('name', 'content_type', 'object_title', 'ip_address', 'submit_date', 'is_public', 'is_removed')

    def object_title(self, obj):
        return unicode(obj.content_object)
    object_title.short_description = 'Title'
    object_title.admin_order_field = 'content_pk'

admin.site.unregister(Comment)
admin.site.register(Comment, CustomCommentsAdmin)
