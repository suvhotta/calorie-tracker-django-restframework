from django.core.management.base import BaseCommand, CommandError
from calorie_app.serializers import UserRegisterSerializer

class Command(BaseCommand):
    help = 'Creates an initial admin account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--password', type=str, default='admin')
        parser.add_argument('--max_calories', type=int, default=2000)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        max_calories = options['max_calories']

        data = {
            "username":username,
            "password":password,
            "profile":{
                "max_calories":max_calories
            },
            "groups":["Administrator"]
        }
        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully created admin account for user : {username}"))
        else:
            raise CommandError(serializer.errors)
            