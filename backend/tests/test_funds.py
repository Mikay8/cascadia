"""Tests for increment 1.3: core tables and seed data.

Done when: a seed script loads three fake tenants with funds, classes,
investors, and loans.
"""

import itertools
import re
from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
from django_tenants.utils import get_public_schema_name, schema_context

from funds.models import Commitment, Fund, Investor, Loan, ShareClass
from tenants.models import Tenant

_schema_counter = itertools.count()


@pytest.fixture
def tenant_schema(transactional_db) -> Generator[str, None, None]:
    """Create a tenant and run the test inside its schema.

    Core tables live in tenant schemas, so ORM tests need a schema context.
    Each test gets a fresh schema name: flushed databases keep old schemas
    around, and re-creating a schema that exists would fail.
    """
    schema_name = f"fundtest{next(_schema_counter)}"
    assert re.fullmatch(r"[a-z0-9_]+", schema_name) and len(schema_name) <= 63
    Tenant(schema_name=schema_name, name="Fund Test Tenant").save()
    with schema_context(schema_name):
        yield schema_name


def _make_fund(name: str = "Test Fund") -> Fund:
    return Fund.objects.create(name=name, vintage_year=2024)


def _make_class(fund: Fund, name: str = "Class A", rank: int = 1) -> ShareClass:
    return ShareClass.objects.create(fund=fund, name=name, rank=rank)


@pytest.mark.django_db(transaction=True)
def test_money_is_stored_exactly_as_decimal(tenant_schema: str) -> None:
    fund = _make_fund()
    cls = _make_class(fund)
    investor = Investor.objects.create(name="Test Investor")
    commitment = Commitment.objects.create(
        investor=investor,
        share_class=cls,
        amount=Decimal("1000000.01"),
        committed_on=date(2024, 1, 15),
    )
    commitment.refresh_from_db()
    assert commitment.amount == Decimal("1000000.01")
    assert isinstance(commitment.amount, Decimal)


@pytest.mark.django_db(transaction=True)
def test_share_classes_come_back_in_rank_order(tenant_schema: str) -> None:
    fund = _make_fund()
    _make_class(fund, "Class C", rank=3)
    _make_class(fund, "Class A", rank=1)
    _make_class(fund, "Class B", rank=2)
    assert [c.name for c in fund.share_classes.all()] == ["Class A", "Class B", "Class C"]


@pytest.mark.django_db(transaction=True)
def test_rank_is_unique_per_fund(tenant_schema: str) -> None:
    fund = _make_fund()
    _make_class(fund, "Class A", rank=1)
    with pytest.raises(IntegrityError):
        _make_class(fund, "Class A Junior", rank=1)


@pytest.mark.django_db(transaction=True)
def test_negative_money_is_rejected(tenant_schema: str) -> None:
    fund = _make_fund()
    loan = Loan(
        fund=fund,
        borrower_name="Bad Borrower",
        principal_amount=Decimal("-100"),
        outstanding_balance=Decimal("0"),
        originated_on=date(2024, 1, 1),
    )
    with pytest.raises(ValidationError):
        loan.full_clean()


@pytest.mark.django_db(transaction=True)
def test_seed_demo_creates_three_tenants_with_data() -> None:
    call_command("seed_demo")

    with schema_context(get_public_schema_name()):
        schemas = set(Tenant.objects.values_list("schema_name", flat=True))
    assert {"acme", "harbor", "mesa"} <= schemas

    for schema in ("acme", "harbor", "mesa"):
        with schema_context(schema):
            assert Fund.objects.count() == 1
            assert ShareClass.objects.count() == 3
            assert list(ShareClass.objects.values_list("rank", flat=True)) == [1, 2, 3]
            assert Investor.objects.count() >= 3
            assert Commitment.objects.count() >= 3
            assert Loan.objects.count() >= 3
            # Every commitment amount is an exact Decimal.
            for amount in Commitment.objects.values_list("amount", flat=True):
                assert isinstance(amount, Decimal)


@pytest.mark.django_db(transaction=True)
def test_seed_demo_is_idempotent() -> None:
    call_command("seed_demo")
    call_command("seed_demo")

    with schema_context("acme"):
        assert Fund.objects.count() == 1
        assert ShareClass.objects.count() == 3


@pytest.mark.django_db(transaction=True)
def test_seeded_data_is_isolated_between_tenants() -> None:
    call_command("seed_demo")

    with schema_context("acme"):
        acme_borrowers = set(Loan.objects.values_list("borrower_name", flat=True))
        acme_investors = set(Investor.objects.values_list("name", flat=True))
    with schema_context("harbor"):
        harbor_borrowers = set(Loan.objects.values_list("borrower_name", flat=True))
        harbor_investors = set(Investor.objects.values_list("name", flat=True))

    assert len(acme_borrowers) > 0
    assert len(harbor_borrowers) > 0
    assert acme_borrowers.isdisjoint(harbor_borrowers)
    assert acme_investors.isdisjoint(harbor_investors)
