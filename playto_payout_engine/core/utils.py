from django.db import transaction
from django.db.models import Sum
from core.models import *
from rest_framework.pagination import PageNumberPagination

class LedgerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

def create_payout(puid, amount_paise, bank_account_id, idempotency_key):
    existing = playto_payout.objects.filter(
        puid=puid,
        idempotency_key=idempotency_key
    ).first()

    if existing:
        return existing  

    with transaction.atomic():

        user = playto_user.objects.select_for_update().get(id=puid)

        bank_account = playto_account_directory.objects.get(
            id=bank_account_id,
            puid=user
        )

        balance = playto_ledger_entries.objects.filter(
            puid=user
        ).aggregate(total=Sum("amount_paise"))["total"] or 0

        if balance < amount_paise:
            raise Exception("Insufficient balance")

        payout = playto_payout.objects.create(
            puid=user,
            bank_account=bank_account,
            amount_paise=amount_paise,
            status="PENDING",
            idempotency_key=idempotency_key
        )

        playto_ledger_entries.objects.create(
            puid=user,
            amount_paise=-amount_paise,
            entry_type="HOLD",
            reference_id=payout.id
        )

    from core.tasks import process_payout
    process_payout.delay(payout.id)

    return payout

def get_balance_summary(puid):
    entries = playto_ledger_entries.objects.filter(puid=puid)

    total = entries.aggregate(total=Sum("amount_paise"))["total"] or 0

    held = entries.filter(entry_type="HOLD").aggregate(
        total=Sum("amount_paise")
    )["total"] or 0

    held_balance = abs(held)

    available_balance = total

    return {
        "available_balance": available_balance,
        "held_balance": held_balance
    }

def get_balance(puid):
    result = playto_ledger_entries.objects.filter(
        puid=puid
    ).aggregate(total=Sum("amount_paise"))

    return result["total"] or 0

def get_ledger_queryset(puid):
    return playto_ledger_entries.objects.filter(
        puid=puid
    ).order_by("-created_at")

def check_acc_belongs_to_user(user_obj,bank_account_id):

    return playto_account_directory.objects.filter(
        id=bank_account_id,
        puid=user_obj.id
    ).exists()

def get_all_users():
    
    return playto_user.objects.values(
        "pt_id",
        "first_name",
        "last_name"
    )