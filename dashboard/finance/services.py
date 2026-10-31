from decimal import Decimal

from django.db import transaction
from django.db.models import F

from .models import Transaction, Wallet


def wallet_for(*, user=None, organization=None) -> Wallet:
    """get_or_create the wallet of a User OR an Organization (exactly one kwarg)."""
    if (user is None) == (organization is None):
        raise ValueError("wallet_for requires exactly one of user= or organization=")
    if user is not None:
        wallet, _ = Wallet.objects.get_or_create(user=user)
    else:
        wallet, _ = Wallet.objects.get_or_create(organization=organization)
    return wallet


@transaction.atomic
def record_transaction(wallet, amount, kind, order_code="") -> Transaction:
    """Create a Transaction and update wallet.balance (credit adds, debit subtracts)."""
    amount = Decimal(amount)
    if kind not in Transaction.Kind.values:
        raise ValueError(f"invalid kind: {kind!r}")
    if amount <= 0:
        raise ValueError("amount must be positive")
    tx = Transaction.objects.create(wallet=wallet, amount=amount, kind=kind, order_code=order_code)
    delta = amount if kind == Transaction.Kind.CREDIT else -amount
    Wallet.objects.filter(pk=wallet.pk).update(balance=F("balance") + delta)
    wallet.refresh_from_db(fields=["balance"])
    return tx
