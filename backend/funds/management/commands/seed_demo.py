"""Seed three fake tenants with funds, classes, investors, and loans.

All data is fictitious and deterministic. Safe to re-run: tenants and rows
that already exist are left alone.

Demo-environment scaffolding (env-gated, off by default):
- ``PRIMARY_DOMAIN``: when set, the value is registered as an additional
  Domain row on the first seed tenant (acme), so the backend's own hostname
  (e.g. backend-uat.up.railway.app) routes to a tenant instead of 404ing.
  The acme.localhost-style domains are kept as well.
- A ``demo`` / ``demo-pass`` staff superuser is created in every tenant.
  These are clearly demo-only seed credentials, not a real secret.

Usage: python manage.py seed_demo
"""

import os
from datetime import date
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from funds.models import Commitment, Fund, Investor, Loan, ShareClass
from tenants.models import Domain, Tenant


def _d(value: str) -> Decimal:
    return Decimal(value)


TENANTS: list[dict[str, Any]] = [
    {
        "schema_name": "acme",
        "name": "Acme Community Loan Fund",
        "domain": "acme.localhost",
        "fund": {"name": "Acme Revolving Loan Fund", "vintage_year": 2023},
        "investors": [
            {
                "name": "Blue Ridge Foundation",
                "type": "institution",
                "commitments": [("Class A", "5000000")],
            },
            {
                "name": "Harbor Trust Bank",
                "type": "institution",
                "commitments": [("Class A", "3000000"), ("Class B", "2000000")],
            },
            {
                "name": "Maria Santos",
                "type": "individual",
                "commitments": [("Class B", "250000")],
            },
            {
                "name": "City of Springfield",
                "type": "government",
                "commitments": [("Class C", "1000000")],
            },
        ],
        "loans": [
            {
                "borrower": "Sunrise Bakery LLC",
                "principal": "150000",
                "balance": "120000",
                "status": "current",
                "originated": date(2024, 2, 15),
                "maturity": date(2029, 2, 15),
            },
            {
                "borrower": "Greenline Manufacturing",
                "principal": "500000",
                "balance": "480000",
                "status": "current",
                "originated": date(2024, 6, 1),
                "maturity": date(2031, 6, 1),
            },
            {
                "borrower": "Casa Verde Apartments",
                "principal": "1200000",
                "balance": "900000",
                "status": "delinquent",
                "originated": date(2023, 9, 10),
                "maturity": date(2033, 9, 10),
            },
            {
                "borrower": "Riverside Childcare Center",
                "principal": "85000",
                "balance": "0",
                "status": "paid_off",
                "originated": date(2022, 4, 20),
                "maturity": date(2027, 4, 20),
            },
            {
                "borrower": "North Fork Solar Co-op",
                "principal": "300000",
                "balance": "275000",
                "status": "current",
                "originated": date(2025, 1, 12),
                "maturity": date(2032, 1, 12),
            },
        ],
    },
    {
        "schema_name": "harbor",
        "name": "Harbor Community Capital",
        "domain": "harbor.localhost",
        "fund": {"name": "Harbor Small Business Fund", "vintage_year": 2024},
        "investors": [
            {
                "name": "Seaside Community Foundation",
                "type": "institution",
                "commitments": [("Class A", "4000000")],
            },
            {
                "name": "Beacon Credit Union",
                "type": "institution",
                "commitments": [("Class B", "1500000")],
            },
            {
                "name": "James Okafor",
                "type": "individual",
                "commitments": [("Class B", "100000"), ("Class C", "50000")],
            },
        ],
        "loans": [
            {
                "borrower": "Tidewater Print Shop",
                "principal": "95000",
                "balance": "70000",
                "status": "current",
                "originated": date(2024, 8, 5),
                "maturity": date(2029, 8, 5),
            },
            {
                "borrower": "Blue Crab Cannery",
                "principal": "650000",
                "balance": "610000",
                "status": "current",
                "originated": date(2025, 2, 18),
                "maturity": date(2032, 2, 18),
            },
            {
                "borrower": "Harborview Market Hall",
                "principal": "420000",
                "balance": "380000",
                "status": "delinquent",
                "originated": date(2024, 3, 30),
                "maturity": date(2030, 3, 30),
            },
            {
                "borrower": "Dune Grass Landscaping",
                "principal": "60000",
                "balance": "0",
                "status": "paid_off",
                "originated": date(2023, 5, 14),
                "maturity": date(2028, 5, 14),
            },
        ],
    },
    {
        "schema_name": "mesa",
        "name": "Mesa Verde Loan Fund",
        "domain": "mesa.localhost",
        "fund": {"name": "Mesa Verde Microenterprise Fund", "vintage_year": 2025},
        "investors": [
            {
                "name": "Desert Sun Foundation",
                "type": "institution",
                "commitments": [("Class A", "2500000")],
            },
            {
                "name": "Copper State Bank",
                "type": "institution",
                "commitments": [("Class A", "1000000"), ("Class C", "500000")],
            },
            {
                "name": "Lucia Fernandez",
                "type": "individual",
                "commitments": [("Class B", "75000")],
            },
        ],
        "loans": [
            {
                "borrower": "Saguaro Food Truck",
                "principal": "45000",
                "balance": "38000",
                "status": "current",
                "originated": date(2025, 4, 2),
                "maturity": date(2030, 4, 2),
            },
            {
                "borrower": "Red Rock Outfitters",
                "principal": "180000",
                "balance": "165000",
                "status": "current",
                "originated": date(2025, 6, 21),
                "maturity": date(2031, 6, 21),
            },
            {
                "borrower": "Adobe House Builders",
                "principal": "750000",
                "balance": "720000",
                "status": "defaulted",
                "originated": date(2024, 11, 8),
                "maturity": date(2034, 11, 8),
            },
        ],
    },
]

CLASS_NAMES = ["Class A", "Class B", "Class C"]

#: Demo-only seed credentials. Clearly not a real secret: the same values are
#: documented in the PR and the demo UI. Never use for anything but seed data.
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo-pass"  # noqa: S105 - demo-only seed credential, documented above


class Command(BaseCommand):
    help = "Seed three fake tenants with funds, classes, investors, and loans."

    def handle(self, *args: str, **options: str) -> None:
        for spec in TENANTS:
            self._seed_tenant(spec)

    @staticmethod
    def _seed_demo_user(schema_name: str) -> None:
        """Create (or refresh) the demo login for a tenant. Idempotent."""
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={"is_staff": True, "is_superuser": True},
        )
        user.set_password(DEMO_PASSWORD)
        user.is_staff = True
        user.is_superuser = True
        user.save()

    def _seed_tenant(self, spec: dict[str, Any]) -> None:
        tenant, created = Tenant.objects.get_or_create(
            schema_name=spec["schema_name"], defaults={"name": spec["name"]}
        )
        if created:
            self.stdout.write(f"Created tenant {tenant.schema_name} (schema provisioned).")
        Domain.objects.get_or_create(
            domain=spec["domain"], defaults={"tenant": tenant, "is_primary": True}
        )
        # Demo-env scaffolding: map the platform hostname to the first seed
        # tenant so /admin/ and /accounts/* resolve instead of 404ing.
        # get_or_create keeps re-runs from duplicating the domain.
        primary_domain = os.environ.get("PRIMARY_DOMAIN", "").strip()
        if primary_domain and spec["schema_name"] == TENANTS[0]["schema_name"]:
            Domain.objects.get_or_create(
                domain=primary_domain,
                defaults={"tenant": tenant, "is_primary": False},
            )

        with schema_context(spec["schema_name"]):
            self._seed_demo_user(spec["schema_name"])
            fund, fund_created = Fund.objects.get_or_create(
                name=spec["fund"]["name"],
                defaults={"vintage_year": spec["fund"]["vintage_year"]},
            )
            if not fund_created:
                self.stdout.write(f"Tenant {tenant.schema_name} already seeded; skipping.")
                return

            classes = {
                name: ShareClass.objects.create(fund=fund, name=name, rank=rank)
                for rank, name in enumerate(CLASS_NAMES, start=1)
            }
            for inv in spec["investors"]:
                investor = Investor.objects.create(name=inv["name"], investor_type=inv["type"])
                for class_name, amount in inv["commitments"]:
                    Commitment.objects.create(
                        investor=investor,
                        share_class=classes[class_name],
                        amount=_d(amount),
                        committed_on=date(2024, 1, 15),
                    )
            for loan in spec["loans"]:
                Loan.objects.create(
                    fund=fund,
                    borrower_name=loan["borrower"],
                    principal_amount=_d(loan["principal"]),
                    outstanding_balance=_d(loan["balance"]),
                    status=loan["status"],
                    originated_on=loan["originated"],
                    maturity_on=loan["maturity"],
                )
            self.stdout.write(
                f"Seeded {tenant.schema_name}: 1 fund, {len(classes)} classes, "
                f"{len(spec['investors'])} investors, {len(spec['loans'])} loans."
            )
