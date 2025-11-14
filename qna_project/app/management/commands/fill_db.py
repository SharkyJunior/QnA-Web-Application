from django.core.management.base import BaseCommand, CommandError

from app.models import Question, Answer, Tag, Profile, QuestionVote, AnswerVote
from django.contrib.auth import get_user_model
from faker import Faker
from rich.progress import Progress

import random

DEFAULT_NUM = 100
QUESTION_RATIO = 10
ANSWER_RATIO = 100
VOTE_RATIO = 200

class Command(BaseCommand):
    help = 'Fill database with fake data'
    
    fake = Faker()

    
    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, default=100)


    def handle(self, *args, **kwargs):
        ratio = int(kwargs["ratio"])
        self.stdout.write(f'Filling the database (ratio = {ratio})')

        self.generate_fake_profiles(ratio)
        self.generate_fake_tags(ratio)
        self.generate_fake_questions(ratio * QUESTION_RATIO)
        self.generate_fake_answers(ratio * ANSWER_RATIO)
        self.generate_fake_votes(ratio * VOTE_RATIO)
                
                
    def generate_fake_profiles(self, num_profiles=100):
        self.stdout.write(f'Generating {num_profiles} profiles...')
        
        User = get_user_model()
        with Progress() as p:
            t = p.add_task("", total=num_profiles)
            while not p.finished:
                p.update(t, advance=1)
                user = User.objects.create_user(
                    username=self.fake.user_name(),
                    email=self.fake.email(),
                    password=self.fake.password(),
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                )
                Profile.objects.create(user=user)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_profiles} users'))
        
        
    def generate_fake_questions(self, num_questions=100):
        self.stdout.write(f'Generating {num_questions} questions...')
        
        with Progress() as p:
            t = p.add_task("", total=num_questions)
            while not p.finished:
                p.update(t, advance=1)
                profile = Profile.objects.order_by('?').first()
                question = Question.objects.create(
                    title=self.fake.sentence()[:-1] + '?',
                    text=self.fake.paragraph(),
                    profile=profile,
                ) 
                
                for _ in range(self.fake.random_int(min=1, max=5)):
                    tag = Tag.objects.order_by('?').first()
                    question.tag.add(tag)
                
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_questions} questions'))
        
        
    def generate_fake_tags(self, num_tags=100):
        self.stdout.write(f'Generating {num_tags} tags...')
        
        with Progress() as p:
            t = p.add_task("", total=num_tags)
            while not p.finished:
                p.update(t, advance=1)
                Tag.objects.create(name=self.fake.word())
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_tags} tags'))
        
        
    def generate_fake_answers(self, num_answers=100):
        self.stdout.write(f'Generating {num_answers} answers...')
        
        with Progress() as p:
            t = p.add_task("", total=num_answers)
            while not p.finished:
                p.update(t, advance=1)
                profile = Profile.objects.order_by('?').first()
                question = Question.objects.order_by('?').first()
                answer = Answer.objects.create(
                    text=self.fake.paragraph(),
                    profile=profile,
                    question=question,
                )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_answers} answers'))
        
        
    def generate_fake_votes(self, num_votes=100):
        self.stdout.write(f'Generating {num_votes} votes...')
        
        with Progress() as p:
            t = p.add_task("", total=num_votes)
            while not p.finished:
                p.update(t, advance=2)
                profile = Profile.objects.order_by('?').first()
                question = Question.objects.order_by('?').first()
                answer = Answer.objects.order_by('?').first()
                vote = QuestionVote.objects.create(
                    question=question,
                    profile=profile,
                    value=random.choice([-1, 1]),
                )
                vote = AnswerVote.objects.create(
                    answer=answer,
                    profile=profile,
                    value=random.choice([-1, 1]),
                )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_votes} votes'))
            