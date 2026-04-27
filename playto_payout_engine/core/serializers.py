from rest_framework import serializers

from core.models import *


class PayoutRequestSerializer(serializers.Serializer):
    amount_paise = serializers.IntegerField(min_value=1)
    bank_account_id = serializers.IntegerField()
    idempotency_key = serializers.UUIDField()
    pt_id = serializers.UUIDField()


class PayoutListResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = playto_payout
        fields = [
            "id",
            "amount_paise",
            "status",
            "created_at",
            "failure_reason"
        ]
    
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