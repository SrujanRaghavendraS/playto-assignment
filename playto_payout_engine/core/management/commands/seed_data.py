def run_seed():
    from core.models import (
        playto_user,
        playto_account_directory,
        playto_payout,
    )

    # Avoid duplicates (important)
    if playto_user.objects.filter(pt_id="PT1001").exists():
        return "Already seeded"

    user1 = playto_user.objects.create(
        pt_id="PT1001",
        first_name="Aarav",
        last_name="Sharma"
    )

    user2 = playto_user.objects.create(
        pt_id="PT1002",
        first_name="Ishita",
        last_name="Verma"
    )

    acc1 = playto_account_directory.objects.create(
        user=user1,
        bank_name="HDFC Bank",
        bank_branch="Bangalore",
        account_number_hash="123456789012"
    )

    acc2 = playto_account_directory.objects.create(
        user=user1,
        bank_name="ICICI Bank",
        bank_branch="Mumbai",
        account_number_hash="987654321098"
    )

    acc3 = playto_account_directory.objects.create(
        user=user2,
        bank_name="SBI",
        bank_branch="Delhi",
        account_number_hash="555566667777"
    )

    playto_payout.objects.create(
        puid=user1,
        bank_account=acc1,
        amount_paise=100000,
        status="COMPLETED",
        idempotency_key="11111111-1111-1111-1111-111111111111"
    )

    return "Seed completed"