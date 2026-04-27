from django.db import models
import uuid

class playto_user(models.Model):
    id = models.BigAutoField(primary_key=True)

    pt_id = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)

    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class playto_account_directory(models.Model):
    id = models.BigAutoField(primary_key=True)

    puid = models.ForeignKey(
        playto_user,
        on_delete=models.CASCADE,
        related_name="bank_accounts"
    )

    bank_name = models.CharField(max_length=100)
    bank_branch = models.CharField(max_length=100)

    account_number_encrypted = models.TextField()
    account_number_hash = models.CharField(max_length=255, db_index=True)

    bank_details = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank_name} - {self.puid_id}"


class playto_ledger_entries(models.Model):

    class EntryType(models.TextChoices):
        CREDIT = "CREDIT"      
        HOLD = "HOLD"          
        RELEASE = "RELEASE"    

    id = models.BigAutoField(primary_key=True)

    puid = models.ForeignKey(
        playto_user,
        on_delete=models.CASCADE,
        related_name="ledger_entries",
        db_index=True
    )

    amount_paise = models.BigIntegerField()

    entry_type = models.CharField(
        max_length=20,
        choices=EntryType.choices
    )

    reference_id = models.BigIntegerField(
        null=True,
        blank=True
    )  # payout_id

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["puid", "created_at"])
        ]

    def __str__(self):
        return f"{self.entry_type} | {self.amount_paise}"


class playto_payout(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    id = models.BigAutoField(primary_key=True)

    puid = models.ForeignKey(
        playto_user,
        on_delete=models.CASCADE,
        related_name="payouts",
        db_index=True
    )

    bank_account = models.ForeignKey(
        playto_account_directory,
        on_delete=models.CASCADE
    )

    amount_paise = models.BigIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    idempotency_key = models.UUIDField()

    retry_count = models.IntegerField(default=0)

    failure_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["puid", "idempotency_key"],
                name="unique_puid_idempotency"
            )
        ]

    def __str__(self):
        return f"{self.id} | {self.status} | {self.amount_paise}"