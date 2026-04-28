from django.urls import path
from core.views import GetBalanceView, CreatePayoutView, PayoutListView ,\
LedgerView, GetAllUsersView, GetProfile, SeedDataView

urlpatterns = [
    path("payouts/", CreatePayoutView.as_view()),
    path("balance/", GetBalanceView.as_view()),
    path("payouts/list/", PayoutListView.as_view()),
    path("ledger/", LedgerView.as_view()),
    path("profile/", GetProfile.as_view()),
    path("users/", GetAllUsersView.as_view()),
    path("seed_data/", SeedDataView.as_view()),
]