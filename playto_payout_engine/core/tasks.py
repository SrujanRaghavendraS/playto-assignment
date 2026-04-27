import random
import time

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from core.models import playto_payout, playto_ledger_entries


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):
    try:
        payout = playto_payout.objects.get(id=payout_id)

        if payout.status in ["COMPLETED", "FAILED"]:
            return

        payout.status = "PROCESSING"
        payout.save(update_fields=["status"])

        # Simulate delay
        time.sleep(2)

        outcome = random.random()

        if outcome < 0.7:
            payout.status = "COMPLETED"
            payout.save(update_fields=["status"])
            return

        elif outcome < 0.9:
            with transaction.atomic():
                payout.status = "FAILED"
                payout.failure_reason = "Simulated failure"
                payout.save(update_fields=["status", "failure_reason"])

                # RELEASE funds
                playto_ledger_entries.objects.create(
                    puid=payout.puid,
                    amount_paise=payout.amount_paise,
                    entry_type="RELEASE",
                    reference_id=payout.id
                )
            return
        else:
            raise Exception("Simulated timeout")

    except Exception as e:
        if self.request.retries >= 3:
            with transaction.atomic():
                payout = playto_payout.objects.get(id=payout_id)

                payout.status = "FAILED"
                payout.failure_reason = "Max retries exceeded"
                payout.save(update_fields=["status", "failure_reason"])

                # RELEASE funds
                playto_ledger_entries.objects.create(
                    puid=payout.puid,
                    amount_paise=payout.amount_paise,
                    entry_type="RELEASE",
                    reference_id=payout.id
                )
            return

        raise self.retry(
            exc=e,
            countdown=2 ** self.request.retries  # exponential backoff
        )