from django.core.management.base import BaseCommand
from core.models import (
    playto_user,
    playto_account_directory,
    playto_ledger_entries
)
import uuid


class Command(BaseCommand):
    help = "Seed initial data"

    def handle(self, *args, **kwargs):

        playto_ledger_entries.objects.all().delete()
        playto_account_directory.objects.all().delete()
        playto_user.objects.all().delete()

        user1 = playto_user.objects.create(
            first_name="Srujan",
            last_name="R",
        )

        user2 = playto_user.objects.create(
            first_name="John",
            last_name="Doe",
        )

        acc1 = playto_account_directory.objects.create(
            puid=user1,
            bank_name="HDFC",
            bank_branch="Bangalore",
            account_number_encrypted="enc_123",
            account_number_hash="hash_123",
            bank_details={"ifsc": "HDFC0001"}
        )

        acc2 = playto_account_directory.objects.create(
            puid=user2,
            bank_name="ICICI",
            bank_branch="Mumbai",
            account_number_encrypted="enc_456",
            account_number_hash="hash_456",
            bank_details={"ifsc": "ICICI0002"}
        )

        playto_ledger_entries.objects.create(
            puid=user1,
            amount_paise=10000,
            entry_type="CREDIT"
        )

        playto_ledger_entries.objects.create(
            puid=user1,
            amount_paise=5000,
            entry_type="CREDIT"
        )

        playto_ledger_entries.objects.create(
            puid=user2,
            amount_paise=20000,
            entry_type="CREDIT"
        )

        self.stdout.write(self.style.SUCCESS("Seed data inserted successfully"))