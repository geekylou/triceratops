from django.test import TestCase
from feed.models import *
from django.contrib.auth.models import AnonymousUser, User

# Create your tests here.

class FeedTestCase(TestCase):
        def setUp(self):
            self.feed = Feed.objects.create(url="local://feed1")
            self.post1 = Post.objects.create(feed=self.feed,link="local://feed1/1",title="wibble")
            self.post2 = Post.objects.create(feed=self.feed,link="local://feed1/2",title="wobble")
            self.tag_name = PostGroupName.objects.create(name="#liked")
            self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
            
        def test_feed(self):
            postgroup = PostGroup.objects.create(post=self.post2,name=self.tag_name,owner=self.user)
            
            for item in PostGroupQuery(PostGroup.objects.all()).filter(title="wobble"):
                self.assertEqual(item.title,"wobble")
            
            # There are no tagged posts with title 'wibble' so assert if one is found.
            for item in PostGroupQuery(PostGroup.objects.all()).filter(title="wibble"):
                self.assertTrue(False)
                
            liked_posts = PostGroup.objects.all().values("post").values()
            print(liked_posts[0]['post_id'])
            print(self.post2.pk == liked_posts[0]['post_id'])
            
            liked_set = frozenset(o['post_id'] for o in liked_posts)
            print(self.post2.pk in liked_set)
            #print(liked_posts[0]['id' == self.post2.id)

            posts = Post.objects.all()
            for post in posts:
                post.liked = post.pk in liked_set
                print(post.liked)
                
            for post in posts:
                print(post.title,post.liked)