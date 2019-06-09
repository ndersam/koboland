from django.contrib import admin

from .models import Topic, Post, Board, TopicVote, PostVote, User

admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Board)
admin.site.register(PostVote)
admin.site.register(TopicVote)
admin.site.register(User)
