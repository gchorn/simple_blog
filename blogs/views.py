from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from blogs.models import Post
from blogs.models import Category


def getPosts(request, qset=None):
    """
    Not a view but a helper function used by most views; getPosts is a method for retrieving many posts
    at once.  If a qset (queryset) is included in the parameters, getPosts will filter using that
    queryset.  If a user is authenticated when this function is called, both published posts and
    unpublished posts *by that author* will be returned.  If the user is not authenticated, only
    published posts will be returned.
    """
    if request.user.is_authenticated():
        if qset:
            results = Post.objects.filter(qset, published=True).distinct() | \
                      Post.objects.filter(qset, published=False, author=request.user).distinct()
            return results.order_by('-pub_date')
        else:
            results = Post.objects.filter(published=True).distinct() | \
                      Post.objects.filter(published=False, author=request.user).distinct()
            return results.order_by('-pub_date')
    else:
        if qset:
            return Post.objects.filter(qset, published=True).distinct().order_by('-pub_date')
        else:
            return Post.objects.filter(published=True).distinct().order_by('-pub_date')


def buildArchives(all_posts):
    """
    Another helper function that gathers up two things: all instances of the Category model 
    as a way of creating a list of all blog categories, as well as a dictionary where the 
    keys are years in which posts have been published and the values are months for that year when
    a post has been published.  With this list of categories and this dictionary of years + months,
    the base template can build the clickable list of categories and year/month archives found
    in the right-hand column of the blog.
    """
    categories = [category for category in Category.objects.all()]
    archdict = {}
    for item in all_posts:
        month = item.pub_date.month
        year = item.pub_date.year
        if year in archdict:
            if month in archdict[year]:
                continue
            else:
                archdict[year].append(month)
        else:
            archdict[year] = [month]
    for key in archdict.keys():
        archdict[key].sort()
    return categories, archdict


def homepage(request):
    """
    View for the homepage, which displays the 5 most recent published posts.  The "start" and "post_num"
    values can be altered to change the first post displayed, and how many posts are displayed (they
    in turn affect the "end" and "next_set" values).  Users can click the "Older Posts" link at the
    bottom of the page to view the next set of most recent posts.
    """
    start = 0 #Index of first (and most recent) post that will be displayed
    post_num = 5 #Number of posts that will be displayed on homepage, as well as subsequent preview pages
    end = start+post_num
    next_set = end+post_num
    all_posts = getPosts(request)
    recent_posts = all_posts[start:end]
    categories, archdict = buildArchives(all_posts)
    return render(request,'homepage.html',{
		'recent_posts':recent_posts,
		'end':end,
		'next_set':next_set,
		'categories':categories,
		'archdict':archdict
		})


def older(request, end, next_set):
    """
    View that is similar to homepage but shows subsequent sets of posts.  The number of posts shown
    per page by in this view is again based on the "start" and "post_num" values in the homepage view.
    Allows user to keep clicking "Older Posts" link at the bottom of the page to access subsequent sets of 
    older posts, until there are none left.  Alternatively, users can click on "Newer Posts" link to go back
    to the next set of more recent posts.
    """
    end, next_set = int(end),int(next_set)
    prev_start, prev_end = end-(next_set-end),end
    all_posts = getPosts(request)
    posts = all_posts[end:next_set]
    if len(all_posts[end:next_set+1])>5:
        end, next_set = end+(next_set-end), next_set+(next_set-end)
    else:
        next_set = None	
    categories, archdict = buildArchives(all_posts)
    return render(request,'older.html',{
		'posts':posts,
		'prev_start':prev_start,
		'prev_end':prev_end,
		'end':end,
		'next_set':next_set,
		'categories':categories,
		'archdict':archdict
		})


def about(request):
    """
    A simple view that returns the post titled "About Me".  This is intended to be an isolated
    view for the blog author(s) to use as an "About Me" or "About Us" style page.  Use this view
    to change the title that is filtered for.
    """
    try:
        #Alter string "About Me" to change the title that is filtered for
        about = Post.objects.get(title="About Me") 
    except:
        about = ''
        message = "You haven't created a post titled 'About Me' yet."
    all_posts = getPosts(request)
    categories, archdict = buildArchives(all_posts)
    return render(request,'about.html', {
										'about':about,
										'categories':categories,
										'archdict':archdict,
                                        'message':message
										})
    

def archive(request,arcyear,arcmonth):
    """
    A view that will show all posts published in a given year and month combination.  Accessed by clicking
    first on a year, then a month in the right-hand column.
    """
    posts = Post.objects.filter(pub_date__year=arcyear,pub_date__month=arcmonth, published=True).order_by('-pub_date')
    all_posts = getPosts(request)
    categories, archdict = buildArchives(all_posts)
    return render(request,'archive.html',{
										'posts':posts,
										'year':arcyear,
										'month':int(arcmonth),
										'categories':categories,
										'archdict':archdict
										})


def category(request,category):
    """
    A view that will show all posts assigned to a certain category.  Accessed by clicking
    on that category name in the right-hand column.
    """
    all_posts = getPosts(request)
    qset = (
        Q(category__name__iexact=category)
    )
    posts = getPosts(request, qset=qset)
    categories, archdict = buildArchives(all_posts)
    return render(request,'category.html', {
										'posts':posts,
										'category':category,
										'categories':categories,
										'archdict':archdict
										})
    

def search(request):
    """
    A view that displays search results obtained by using the search box on the upper-right side of
    the blog.  Common words such as 'the', 'a', and 'of' are removed from querysets, and then
    post titles, texts, tags, and categories are searched for each word in the queryset.
    """
    all_posts = getPosts(request)
    query = request.GET.get('q','')
    querywords = query.split(' ')
    for word in querywords:
        querywords.append(word.lower())
        querywords.remove(word)
    while 'the' in querywords:
        querywords.remove('the')
    while 'a' in querywords:
        querywords.remove('a')
    while 'of' in querywords:
        querywords.remove('of')
    results=[]
    if query:
        for word in querywords:
            word = r'\y%s\y' % word
            qset = (
                Q(title__iregex=word)|
                Q(text__iregex=word)|
                Q(tag__name__iregex=word)|
                Q(category__name__iregex=word)
            )
            result = getPosts(request, qset=qset)
            for item in result:
                results.append(item)
    categories, archdict = buildArchives(all_posts)
    return render(request,'search.html', {
											'results': results,
											'query': query,
											'querywords':querywords,
											'categories':categories,
											'archdict':archdict
										})


def postdetail(request,post_id):
    """
    The full, detailed view of each post.  This view includes a larger version of a post's first image,
    as well as the full text for the post and a list of tags for the post at the end.  It also includes
    a comments form and below it, a section listing previously approved comments for that post.
    """
    all_posts = getPosts(request)
    if request.user.is_authenticated():
        post = get_object_or_404(Post, pk = post_id)
        if post.published == 'False':
            if request.user != post.author:
                raise Http404
    else:
        post = get_object_or_404(Post, pk=post_id, published=True)
    tags = post.tag_set.all()
    categories, archdict = buildArchives(all_posts)
    return render(request,'postdetail.html', {
											'post':post,
											'categories':categories,
											'tags':tags,
											'archdict':archdict
											})
    

def posted(request,post_id):
    """
    The view a user sees after submitting a comment on a post.  It simply confirms the comment was
    submitted and that it will be up shortly.
    """
    all_posts = getPosts(request)
    post = Post.objects.get(pk = post_id)
    categories, archdict = buildArchives(all_posts)
    return render(request,'posted.html', {
										'categories':categories,
										'post':post,
										'archdict':archdict
										})
    

def tags(request,tag):
    """
    By clicking on a tag in a post's detailed view, the user will see all posts that have been tagged
    with the same tag.
    """
    all_posts = getPosts(request)
    qset = (
        Q(tag__name__iexact=tag)
    )
    posts = getPosts(request, qset=qset)
    categories, archdict = buildArchives(all_posts)
    return render(request,'tags.html',{
									'posts':posts,
									'category':category,
									'categories':categories,
									'tag':tag,
									'archdict':archdict
									})
