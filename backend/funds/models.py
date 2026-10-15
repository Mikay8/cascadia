"""Core tables for fund administration.

Every model here lives in the tenant's schema (the ``funds`` app is in
TENANT_APPS), so each CDFI sees only its own funds, investors, and loans.
Money is ``Decimal``/``NUMERIC`` everywhere; the API will send it as strings.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

#: NUMERIC(19, 2): exact to the cent, up to ~9 quadrillion. Standard for ledgers.
MONEY_KWARGS = {
    "max_digits": 19,
    "decimal_places": 2,
    "validators": [MinValueValidator(Decimal("0"))],
}


class Fund(models.Model):
    """One investment fund run by the tenant (e.g. a revolving loan fund)."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=200)
    vintage_year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class ShareClass(models.Model):
    """One ranked investor class within a fund (A, B, C).

    ``rank`` is the payout priority: rank 1 is paid first. Ranks are unique
    per fund so the waterfall order is never ambiguous.
    """

    fund = models.ForeignKey(Fund, related_name="share_classes", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rank = models.PositiveIntegerField()

    class Meta:
        ordering = ["rank"]
        constraints = [
            models.UniqueConstraint(fields=["fund", "rank"], name="unique_rank_per_fund"),
            models.UniqueConstraint(fields=["fund", "name"], name="unique_class_name_per_fund"),
        ]

    def __str__(self) -> str:
        return f"{self.fund.name} {self.name}"


class Investor(models.Model):
    """An investor. Tenant-level: one investor may hold commitments in several
    funds through different share classes."""

    class InvestorType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        INSTITUTION = "institution", "Institution"
        GOVERNMENT = "government", "Government"

    name = models.CharField(max_length=200)
    investor_type = models.CharField(
        max_length=20, choices=InvestorType.choices, default=InvestorType.INSTITUTION
    )

    def __str__(self) -> str:
        return self.name


class Commitment(models.Model):
    """Capital an investor committed to one share class of a fund."""

    investor = models.ForeignKey(Investor, related_name="commitments", on_delete=models.CASCADE)
    share_class = models.ForeignKey(
        ShareClass, related_name="commitments", on_delete=models.CASCADE
    )
    amount = models.DecimalField(**MONEY_KWARGS)
    committed_on = models.DateField()

    def __str__(self) -> str:
        return f"{self.investor.name} -> {self.share_class} ({self.amount})"


class Loan(models.Model):
    """One loan in a fund's portfolio. Repayments on these feed the waterfall."""

    class LoanStatus(models.TextChoices):
        CURRENT = "current", "Current"
        DELINQUENT = "delinquent", "Delinquent"
        DEFAULTED = "defaulted", "Defaulted"
        PAID_OFF = "paid_off", "Paid off"

    fund = models.ForeignKey(Fund, related_name="loans", on_delete=models.CASCADE)
    borrower_name = models.CharField(max_length=200)
    principal_amount = models.DecimalField(**MONEY_KWARGS)
    outstanding_balance = models.DecimalField(**MONEY_KWARGS)
    status = models.CharField(max_length=10, choices=LoanStatus.choices, default=LoanStatus.CURRENT)
    originated_on = models.DateField()
    maturity_on = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.borrower_name} ({self.fund.name})"
