"""
Test custom Django management commands.
"""
import tempfile
import json
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase, TestCase

from core.models import Cryptocurrency


@patch("core.management.commands.wait_for_db.Command.check")
class WaitForDatabaseTestCase(SimpleTestCase):
    """Test wait_for_db commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = (
            [Psycopg2OpError] * 2 + [OperationalError] * 1 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 4)
        patched_check.assert_called_with(databases=["default"])


class ImportCryptoCurrencies(TestCase):
    """Test the import command"""

    def test_import_cryptocurrencies_command(self):
        # Create a sample JSON file with cryptocurrency data
        data = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            # Add more cryptocurrencies if needed
        }

        # Create a temporary JSON file and write the data
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_json_file:
            json.dump(data, temp_json_file)

        try:
            # Execute the management command to import the cryptocurrencies
            call_command("import_cryptocurrencies", temp_json_file.name)

            # Check if the cryptocurrencies were imported successfully
            btc_crypto = Cryptocurrency.objects.get(symbol="BTC")
            eth_crypto = Cryptocurrency.objects.get(symbol="ETH")

            self.assertEqual(btc_crypto.name, "Bitcoin")
            self.assertEqual(eth_crypto.name, "Ethereum")

            # Optionally, you can check for other cryptocurrencies if needed
        finally:
            # Clean up the temporary JSON file
            temp_json_file.close()
