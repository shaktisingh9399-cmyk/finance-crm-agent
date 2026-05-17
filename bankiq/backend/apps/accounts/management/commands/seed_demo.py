"""Seed demo RM and sample customers for local development."""

from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

from apps.accounts.models import RelationshipManager
from apps.customers.models import Customer, KYCStatus


class Command(BaseCommand):
    """Create demo RM user and sample customers."""

    help = "Seed demo relationship manager and customers"

    def handle(self, *args, **options) -> None:
        fake = Faker("en_IN")
        rm, created = RelationshipManager.objects.get_or_create(
            username="rm_demo",
            defaults={
                "employee_id": "RM001",
                "branch_code": "MUM01",
                "email": "rm.demo@bankiq.local",
                "is_staff": True,
            },
        )
        if created:
            rm.set_password("demo1234")
            rm.save()
            self.stdout.write(self.style.SUCCESS("Created demo RM: rm_demo / demo1234"))
        else:
            self.stdout.write("Demo RM already exists")

        if Customer.objects.filter(rm=rm).exists():
            self.stdout.write("Customers already seeded — skipping")
            return

        batch = []
        for i in range(100):
            batch.append(
                Customer(
                    rm=rm,
                    name=fake.name(),
                    phone=fake.phone_number()[:15],
                    email=fake.email(),
                    pan=fake.bothify(text="?????####?").upper(),
                    aadhaar=fake.numerify(text="############"),
                    account_number=fake.bothify(text="##########"),
                    annual_income=Decimal(str(fake.random_int(300000, 2500000))),
                    credit_score=fake.random_int(550, 850),
                    emi_ratio=Decimal(str(round(fake.random.uniform(0.05, 0.45), 3))),
                    age=fake.random_int(25, 60),
                    tenure_years=fake.random_int(1, 15),
                    savings_balance=Decimal(str(fake.random_int(50000, 5000000))),
                    kyc_status=KYCStatus.COMPLETE,
                    marketing_consent=True,
                    do_not_contact=False,
                )
            )
        Customer.objects.bulk_create(batch, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(batch)} customers"))
