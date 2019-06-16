from django.contrib import admin

from .models import Topic, Post, Board, User, Vote

admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Board)
admin.site.register(Vote)
# admin.site.register(TopicVote)
admin.site.register(User)
