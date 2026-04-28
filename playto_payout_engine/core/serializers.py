from rest_framework import serializers

from core.models import *


class PayoutRequestSerializer(serializers.Serializer):
    amount_paise = serializers.IntegerField(min_value=1)
    bank_account_id = serializers.IntegerField()
    idempotency_key = serializers.UUIDField()
    pt_id = serializers.UUIDField()


class PayoutListResponseSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source="bank_account.bank_name", read_only=True)
    bank_branch = serializers.CharField(source="bank_account.bank_branch", read_only=True)
    masked_account = serializers.SerializerMethodField()

    class Meta:
        model = playto_payout
        fields = [
            "id",
            "amount_paise",
            "status",
            "created_at",
            "failure_reason",
            "bank_name",
            "bank_branch",
            "masked_account",
        ]

    def get_masked_account(self, obj):
        acc = obj.bank_account.account_number_hash  # assuming this is stored
        if not acc:
            return None
        return "****" + acc[-4:]
    
class PayoutListRequestSerializer(serializers.Serializer):
    pt_id = serializers.UUIDField()

class LedgerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = playto_ledger_entries
        fields = [
            "id",
            "entry_type",
            "amount_paise",
            "created_at",
            "reference_id"
        ]

class LedgerRequestSerializer(serializers.Serializer):
    pt_id = serializers.UUIDField()
    page_no = serializers.IntegerField(default=1, min_value=1)

class PayoutResponseSerializer(serializers.Serializer):
    payout_id = serializers.IntegerField()
    status = serializers.CharField()
    amount_paise = serializers.IntegerField()

class BalanceResponseSerializer(serializers.Serializer):
    available_balance = serializers.IntegerField()
    held_balance = serializers.IntegerField()

class BalanceRequestSerializer(serializers.Serializer):
    pt_id = serializers.UUIDField()

class UserListResponseSerializer(serializers.Serializer):
    pt_id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class GetProfileRequestSerializer(serializers.Serializer):
    pt_id = serializers.UUIDField()

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = playto_account_directory
        fields = [
            "id",
            "bank_name",
            "bank_branch",
            "account_number_hash",
            "bank_details",
        ]


class GetProfileResponseSerializer(serializers.ModelSerializer):
    bank_accounts = BankAccountSerializer(many=True, read_only=True)

    class Meta:
        model = playto_user
        fields = [
            "pt_id",
            "first_name",
            "last_name",
            "bank_accounts"
        ]