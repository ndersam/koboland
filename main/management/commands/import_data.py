import csv
import json
from collections import Counter

from django.core.management.base import BaseCommand

from main import models


class Command(BaseCommand):
    help = 'Import sample data (users, boards, topics, posts) for development purposes only'

    def add_arguments(self, parser):
        parser.add_argument('user_file', nargs='?', type=str, default='main/sample_data/users.csv')
        parser.add_argument('board_file', nargs='?', type=str, default='main/sample_data/boards.csv')
        parser.add_argument('post_file', nargs='?', type=str, default='main/sample_data/post_data.json')

    def handle(self, *args, **options):
        self.stdout.write('Importing dev data')
        self.import_users(options['user_file'])
        self.import_boards(options.pop('board_file'))
        self.import_post_data(options.pop('post_file'))

    def import_users(self, user_file):
        c = Counter()
        with open(user_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user, created = models.User.objects.get_or_create(
                    username=row['username'], email=row['email'], password=row['password']
                )
                c['processed'] += 1
                if created:
                    c['created'] += 1
        self.stdout.write(f'Users processed={c["processed"]} (created={c["created"]})')

    def import_boards(self, board_file):
        c = Counter()
        with open(board_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.stdout.write(str(row))
                moderators = [mod.strip() for mod in row['moderators'].split(',')]
                board, created = models.Board.objects.get_or_create(
                    name=row['name'], description=row['description'],
                )
                if created:
                    for mod_name in moderators:
                        mod = models.User.objects.get(username=mod_name)
                        board.moderators.add(mod)
                    c['created'] += 1
                c['processed'] += 1
        self.stdout.write(f'Boards processed={c["processed"]} (created={c["created"]})')

    def import_post_data(self, data_file):
        c = Counter()
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                board = models.Board.objects.get(name=item['board'])
                author = models.User.objects.get(username=item['author'].strip())
                topic = author.topics.create(
                    title=item['title'], board=board, content=item['content']
                )
                for post_item in item['posts']:
                    author = models.User.objects.get(username=post_item['author'].strip())
                    author.posts.create(
                        content=post_item['content'],
                        topic_id=topic.id
                    )
                    c['posts_processed'] += 1
                c['topics_processed'] += 1
        self.stdout.write(f'Topics processed={c["topics_processed"]} (posts processed={c["posts_processed"]})')
