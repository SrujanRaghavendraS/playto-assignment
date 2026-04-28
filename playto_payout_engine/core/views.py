from playto_payout_engine.core.management.commands.seed_data import run_seed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError, NotFound

from core.serializers import *
from core.utils import *
from core.base.BaseAPIview import BaseAPIView
import logging

logger = logging.getLogger(__name__)

class PayoutListView(BaseAPIView):
    request_serializer_class = PayoutListRequestSerializer
    response_serializer_class = PayoutListResponseSerializer

    def post(self, request):
        try:
            validated_data = self.get_validated_data(request)
            user = self.get_user_obj(validated_data)

            if not user:
                raise NotFound("User not found")

            logger.info(f"Fetching Payout List for the user : {user.pt_id}")

            payouts = playto_payout.objects.filter(
                puid=user.id
            ).order_by("-created_at")

            serializer = self.response_serializer_class(payouts, many=True)

            return Response(serializer.data)

        except Exception as e:
            logger.error("Failed to fetch the required data")
            raise APIException(str(e))


class CreatePayoutView(BaseAPIView):
    request_serializer_class = PayoutRequestSerializer
    response_serializer_class = PayoutResponseSerializer

    def post(self, request):
        try:
            validated_data = self.get_validated_data(request)

            response_data = self._handle_request(validated_data)

            serializer = self.response_serializer_class(response_data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            raise APIException(str(e))

    def _handle_request(self, validated_data):
        try:
            user = self.get_user_obj(validated_data)
            bank_account_id = validated_data.get("bank_account_id")
            logger.info(f"Creating PAyout fot the user : {user.pt_id}")

            is_valid_account = check_acc_belongs_to_user(user, bank_account_id)

            if not is_valid_account:
                raise ValidationError(
                    {"bank_account_id": "Account does not belong to user"}
                )


            idempotency_key = validated_data.get('idempotency_key')
            payout = create_payout(
                puid=user.id,
                amount_paise=validated_data.get("amount_paise"),
                bank_account_id=validated_data.get("bank_account_id"),
                idempotency_key=idempotency_key
            )

            return {
                "payout_id": payout.id,
                "status": payout.status,
                "amount_paise": payout.amount_paise
            }

        except Exception as e:
            logger.error("Failed to Create payout")
            raise APIException(str(e))

class GetBalanceView(BaseAPIView):
    request_serializer_class = BalanceRequestSerializer
    response_serializer_class = BalanceResponseSerializer

    def post(self, request):
        try:
            validated_data = self.get_validated_data(request)

            user = self.get_user_obj(validated_data)
            summary = get_balance_summary(user.id)
            logger.info(f"Fetching Summary for pt_id: {user.pt_id}")

            serializer = self.response_serializer_class(summary)

            return Response(serializer.data)

        except Exception as e:
            logger.error("FAiled to get Balance for the user")
            raise APIException(str(e))
        
class LedgerView(BaseAPIView):
    request_serializer_class = LedgerRequestSerializer
    response_serializer_class = LedgerResponseSerializer

    def post(self, request):
        try:
            validated_data = self.get_validated_data(request)

            user = self.get_user_obj(validated_data)
            page_no = validated_data.get("page_no", 1)
            page_size = 10
            logger.info(f"Fetching the data for pt_id : {user.pt_id} ,page_no: {page_no}, page_size: {page_size} ")

            queryset = get_ledger_queryset(user.id)
            total_count = queryset.count()
            start = (page_no - 1) * page_size
            end = start + page_size

            page_data = queryset[start:end]

            serializer = self.response_serializer_class(page_data, many=True)

            return Response({
                "total_count": total_count,
                "page_no": page_no,
                "results": serializer.data
            })

        except Exception as e:
            raise APIException(str(e))
        
class GetProfile(BaseAPIView):
    request_serializer_class = GetProfileRequestSerializer
    response_serializer_class = GetProfileResponseSerializer

    def post(self, request):
        try:
            validated_data = self.get_validated_data(request)

            pt_id = validated_data.get("pt_id")
            logger.info(f"Fetching data for pt_id: {pt_id}")

            user = playto_user.objects.prefetch_related(
                "bank_accounts"
            ).filter(pt_id=pt_id).first()

            if not user:
                raise APIException("User not found")

            serializer = self.response_serializer_class(user)

            return Response(serializer.data)

        except Exception as e:
            logger.exception("Failed to Fetch Requested Profile data")
            raise APIException(str(e))

class GetAllUsersView(BaseAPIView):
    response_serializer_class = UserListResponseSerializer

    def get(self, request):

        try:
            logger.info("Fetching all users Data")
            users = get_all_users()

            serializer = self.response_serializer_class(users, many=True)

            return Response(serializer.data)
        
        except Exception as e:
            logger.error("Something went Wrong !")
            raise APIException(str(e))


class SeedDataView(BaseAPIView):

    def post(self, request):

        result = run_seed()

        return Response({
            "message": result
        })