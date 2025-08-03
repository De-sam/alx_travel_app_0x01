#!/usr/bin/env python3
"""Custom command to seed the database with listings"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing
from faker import Faker

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def handle(self, *args, **kwargs):
        # Ensure at least one host exists
        host, _ = User.objects.get_or_create(
            email='host@example.com',
            defaults={
                'username': 'hostuser',
                'first_name': 'Host',
                'last_name': 'User',
                'password': 'admin1234',
            }
        )
        if not host.check_password('admin1234'):
            host.set_password('admin1234')
            host.save()

        self.stdout.write(self.style.SUCCESS(f'Using host: {host.email}'))

        # Create sample listings
        for _ in range(10):
            Listing.objects.create(
                host=host,
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                price_per_night=round(random.uniform(50.00, 500.00), 2)
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 10 listings!'))
