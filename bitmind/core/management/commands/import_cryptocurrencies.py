"""
Command to import default cryptos into the database
"""

import json

from django.core.management.base import BaseCommand

from core.models import Cryptocurrency


class Command(BaseCommand):
    help = "Import data from a JSON file into the Cryptocurrency model"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Path to the JSON file to import"
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]

        try:
            with open(json_file, "r") as file:
                data = json.load(file)
                number_imported = 0
                for symbol, name in data.items():
                    # Check if a Cryptocurrency object with the same symbol already exists
                    existing_crypto = Cryptocurrency.objects.filter(
                        symbol=symbol
                    ).first()

                    if existing_crypto is None:
                        Cryptocurrency.objects.create(symbol=symbol, name=name)
                        number_imported += 1
                    else:
                        continue

                self.stdout.write(
                    self.style.SUCCESS(f"\nImported {number_imported} Coins")
                )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"\nAn error occurred: {str(e)}"))
