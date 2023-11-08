"""
Tests for the portfolio API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Cryptocurrency, Transaction, UserCoin

CRYPTOCURRENCY_URL = reverse("portfolio:cryptocurrency-list")
TRANSACTION_URL = reverse("portfolio:transaction-list")
HOLDINGS_URL = reverse("portfolio:holdings-list")


def transaction_detail_url(transaction_id):
    return reverse("portfolio:transaction-detail", args=[transaction_id])


class PublicUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user_can_list_cryptocurrencies(self):
        # Create Cryptocurrency entries
        Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")
        Cryptocurrency.objects.create(name="Ethereum", symbol="ETH")

        # Make a GET request to the cryptocurrency list endpoint
        response = self.client.get(CRYPTOCURRENCY_URL)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the expected cryptocurrencies are present in the deserialized data
        self.assertIn({"name": "Bitcoin", "symbol": "BTC"}, response.data)
        self.assertIn({"name": "Ethereum", "symbol": "ETH"}, response.data)

    def test_unauthenticated_user_cannot_add_cryptocurrency(self):
        # Define the data for creating a new cryptocurrency
        new_crypto_data = {"name": "Litecoin", "symbol": "LTC"}

        # Make a POST request to the cryptocurrency list endpoint with the new data
        response = self.client.post(CRYPTOCURRENCY_URL, new_crypto_data, format="json")

        # Check that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check that no new cryptocurrency was added to the database
        self.assertEqual(Cryptocurrency.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_transaction(self):
        # Add coin to database
        Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Define the data you want to send in the POST request
        data = {
            "crypto": "BTC",  # Replace with the ID of a valid crypto
            "date": "2023-09-01T00:00:00Z",
            "transaction_type": "buy",  # Or "sell" depending on your model's choices
            "amount": "1.0",
            "price": "100.0",
        }

        # Make a POST request to the transaction creation endpoint
        response = self.client.post(TRANSACTION_URL, data, format="json")

        # Check that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create an authenticated user
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="userpassword",
        )
        self.client.force_authenticate(user=self.user)  # Authenticate the user

    def test_authenticated_user_can_list_cryptocurrencies(self):
        # Create Cryptocurrency entries
        Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")
        Cryptocurrency.objects.create(name="Ethereum", symbol="ETH")

        # Make a GET request to the cryptocurrency list endpoint
        response = self.client.get(CRYPTOCURRENCY_URL)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the expected cryptocurrencies are present in the deserialized data
        self.assertIn({"name": "Bitcoin", "symbol": "BTC"}, response.data)
        self.assertIn({"name": "Ethereum", "symbol": "ETH"}, response.data)

    def test_authenticated_user_cannot_add_cryptocurrency(self):
        # Define the data for creating a new cryptocurrency
        new_crypto_data = {"name": "Litecoin", "symbol": "LTC"}

        # Make a POST request to the cryptocurrency list endpoint with the new data
        response = self.client.post(CRYPTOCURRENCY_URL, new_crypto_data, format="json")

        # Check that the response status code is 403 (Forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check that no new cryptocurrency was added to the database
        self.assertEqual(Cryptocurrency.objects.count(), 0)

    def test_authenticated_user_can_create_transaction(self):
        # Create cryptocurrency entry
        cryptocurency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Define the data for creating a new transaction
        payload = {
            "crypto": cryptocurency.symbol,  # Replace with the ID of the cryptocurrency you want to use
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",  # Or "sell" depending on your model's choices
            "amount": "1.0",
            "price": "100.0",
        }

        # Make a POST request to the transaction creation endpoint with the new data
        response = self.client.post(TRANSACTION_URL, payload, format="json")

        # Check that the response status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the new transaction was added to the database
        self.assertEqual(Transaction.objects.count(), 1)

    def test_authenticated_user_cannot_create_invalid_transaction(self):
        # Define invalid transaction data (missing required fields)
        payload = {
            "date": "2023-09-01T00:00:00Z",
        }

        # Make a POST request to the transaction creation endpoint with invalid data
        response = self.client.post(TRANSACTION_URL, payload, format="json")

        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that no new transaction was added to the database
        self.assertEqual(Transaction.objects.count(), 0)


class AuthenticatedSuperUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create an authenticated super user
        self.user = get_user_model().objects.create_superuser(
            email="user@example.com",
            password="userpassword",
        )
        self.client.force_authenticate(user=self.user)  # Authenticate the user

    def test_authenticated_superuser_can_add_cryptocurrency(self):
        # Define the data for creating a new cryptocurrency
        new_crypto_data = {"name": "Litecoin", "symbol": "LTC"}

        # Make a POST request to the cryptocurrency list endpoint with the new data
        response = self.client.post(CRYPTOCURRENCY_URL, new_crypto_data, format="json")

        # Check that the response status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the new cryptocurrency was added to the database
        self.assertEqual(Cryptocurrency.objects.count(), 1)

    def test_authenticated_superuser_cannot_create_invalid_transaction(self):
        # Define invalid transaction data (missing required fields)
        payload = {
            "date": "2023-09-01T00:00:00Z",
        }

        # Make a POST request to the transaction creation endpoint with invalid data
        response = self.client.post(TRANSACTION_URL, payload, format="json")

        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that no new transaction was added to the database
        self.assertEqual(Transaction.objects.count(), 0)


class ApiLogicTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create an authenticated user
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="userpassword",
        )
        self.client.force_authenticate(user=self.user)  # Authenticate the user

    def test_create_transaction_affects_usercoins(self):
        # Step 1: Create a Cryptocurrency
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Step 2: Define transaction data with the cryptocurrency you created
        transaction_data = {
            "crypto": cryptocurrency.symbol,
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",
            "amount": "1.0",
            "price": "100.0",
        }

        # Step 3: Make a POST request to create the transaction
        response = self.client.post(TRANSACTION_URL, transaction_data, format="json")

        # Step 4: Query UserCoin to get the updated amount
        user_coin = UserCoin.objects.get(user=self.user, crypto=cryptocurrency)

        # Step 5: Assert that the UserCoin's amount has been updated correctly
        self.assertEqual(
            user_coin.amount, Decimal("1.0")
        )  # Adjust the expected amount as needed

    def test_create_and_delete_transaction_updates_usercoin(self):
        # Step 1: Create a Cryptocurrency
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Step 2: Define transaction data with the cryptocurrency you created
        transaction_data = {
            "crypto": cryptocurrency.symbol,
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",
            "amount": "1.0",
            "price": "100.0",
        }

        # Step 3: Make a POST request to create the transaction
        response = self.client.post(TRANSACTION_URL, transaction_data, format="json")

        # Step 4: Query UserCoin to get the updated amount after creating the transaction
        user_coin_after_create = UserCoin.objects.get(
            user=self.user, crypto=cryptocurrency
        )

        # Step 5: Assert that the UserCoin's amount has been updated correctly after creation
        self.assertEqual(
            user_coin_after_create.amount, Decimal("1.0")
        )  # Adjust the expected amount as needed

        # Step 6: Delete the created transaction
        transaction_id = response.data["id"]
        delete_url = transaction_detail_url(transaction_id)
        self.client.delete(delete_url)

        # Step 7: Query UserCoin to check if it was deleted (if amount is zero)
        with self.assertRaises(UserCoin.DoesNotExist):
            UserCoin.objects.get(user=self.user, crypto=cryptocurrency)

    def test_buy_and_sell_transactions_insufficient_coins(self):
        # Step 1: Create a Cryptocurrency
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Step 2: Define transaction data with the cryptocurrency you created
        buy_transaction_data = {
            "crypto": cryptocurrency.symbol,  # Use symbol instead of id
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",
            "amount": "10.0",
            "price": "100.0",
        }

        # Step 3: Make a POST request to create the buy transaction
        response_buy = self.client.post(
            TRANSACTION_URL, buy_transaction_data, format="json"
        )

        # Step 4: Query UserCoin to get the updated amount after creating the buy transaction
        user_coin_after_buy = UserCoin.objects.get(
            user=self.user, crypto=cryptocurrency
        )

        # Step 5: Assert that the UserCoin's amount has been updated correctly after the buy transaction
        self.assertEqual(user_coin_after_buy.amount, Decimal("10.0"))

        # Step 6: Define sell transaction data with the cryptocurrency you created
        sell_transaction_data = {
            "crypto": cryptocurrency.symbol,  # Use symbol instead of id
            "date": "2023-09-02T00:00:00Z",
            "type": "sell",
            "amount": "15.0",
            "price": "150.0",
        }

        # Step 7: Make a POST request to create the sell transaction, which should fail
        response_sell = self.client.post(
            TRANSACTION_URL, sell_transaction_data, format="json"
        )

        # Step 8: Assert that the response status code is 400 (Bad Request) due to insufficient coins
        self.assertEqual(response_sell.status_code, status.HTTP_400_BAD_REQUEST)

        # Step 9: Query UserCoin to check that the amount remains unchanged after the failed sell transaction
        user_coin_after_sell_failed = UserCoin.objects.get(
            user=self.user, crypto=cryptocurrency
        )

        # Step 10: Assert that the UserCoin's amount remains unchanged
        self.assertEqual(user_coin_after_sell_failed.amount, Decimal("10.0"))

    def test_update_buy_transaction_to_sell_transaction(self):
        # Step 1: Create a Cryptocurrency
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Step 2: Define transaction data with the cryptocurrency you created
        buy_transaction_data = {
            "crypto": cryptocurrency.symbol,  # Use symbol instead of id
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",
            "amount": "10.0",
            "price": "100.0",
        }

        # Step 3: Make a POST request to create the buy transaction
        response_create = self.client.post(
            TRANSACTION_URL, buy_transaction_data, format="json"
        )

        # Step 4: Assert that the response status code is 201 (Created)
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)

        # Step 5: Get the ID of the created transaction
        transaction_id = response_create.data["id"]

        # Step 6: Define updated transaction data to change the type to "sell"
        updated_transaction_data = {
            "type": "sell",
        }

        # Step 7: Make a PATCH request to update the transaction type to "sell"
        response_update = self.client.patch(
            transaction_detail_url(transaction_id),
            updated_transaction_data,
            format="json",
        )

        # Step 8: Assert that the response status code is 400 (Bad Request) due to invalid update
        self.assertEqual(response_update.status_code, status.HTTP_400_BAD_REQUEST)

        # Step 9: Query the transaction to check that the type remains "buy"
        updated_transaction = Transaction.objects.get(pk=transaction_id)

        # Step 10: Assert that the transaction type remains "buy"
        self.assertEqual(updated_transaction.type, "buy")

    def test_delete_buy_transaction_with_negative_holdings(self):
        # Step 1: Create a Cryptocurrency
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Step 2: Define transaction data with the cryptocurrency you created
        buy_transaction_data = {
            "crypto": cryptocurrency.symbol,  # Use symbol instead of id
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",
            "amount": "10.0",
            "price": "100.0",
        }

        # Step 3: Make a POST request to create the buy transaction
        response_create_buy = self.client.post(
            TRANSACTION_URL, buy_transaction_data, format="json"
        )

        # Step 4: Assert that the response status code is 201 (Created)
        self.assertEqual(response_create_buy.status_code, status.HTTP_201_CREATED)

        # Step 5: Create a sell transaction to reduce the holdings
        sell_transaction_data = {
            "crypto": cryptocurrency.symbol,
            "date": "2023-09-02T00:00:00Z",
            "type": "sell",
            "amount": "5.0",
            "price": "110.0",
        }

        # Step 6: Make a POST request to create the sell transaction
        response_create_sell = self.client.post(
            TRANSACTION_URL, sell_transaction_data, format="json"
        )

        # Step 7: Assert that the response status code is 201 (Created)
        self.assertEqual(response_create_sell.status_code, status.HTTP_201_CREATED)

        # Step 8: Get the ID of the buy transaction
        buy_transaction_id = response_create_buy.data["id"]

        # Step 9: Attempt to delete the buy transaction
        response_delete_buy = self.client.delete(
            transaction_detail_url(buy_transaction_id)
        )

        # Step 10: Assert that the response status code is 400 (Bad Request) due to negative holdings
        self.assertEqual(response_delete_buy.status_code, status.HTTP_400_BAD_REQUEST)

        # Step 11: Query the buy transaction to check that it still exists
        buy_transaction_still_exists = Transaction.objects.filter(
            pk=buy_transaction_id
        ).exists()

        # Step 12: Assert that the buy transaction still exists
        self.assertTrue(buy_transaction_still_exists)

    def test_creating_transaction_with_negative_amount_fails(self):
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Define a payload with a negative amount
        payload = {
            "crypto": cryptocurrency.symbol,  # Replace with a valid cryptocurrency symbol
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",  # Or "sell" depending on your model's choices
            "amount": "-1.0",  # Negative amount
            "price": "100.0",
        }

        # Attempt to create a transaction with a negative amount
        response = self.client.post(TRANSACTION_URL, payload, format="json")

        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that no new transaction was added to the database
        self.assertEqual(Transaction.objects.count(), 0)

    def test_creating_transaction_with_negative_price_fails(self):
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Define a payload with a negative amount
        payload = {
            "crypto": cryptocurrency.symbol,  # Replace with a valid cryptocurrency symbol
            "date": "2023-09-01T00:00:00Z",
            "type": "buy",  # Or "sell" depending on your model's choices
            "amount": "1.0",
            "price": "-100.0",  # Negative price
        }

        # Attempt to create a transaction with a negative price
        response = self.client.post(TRANSACTION_URL, payload, format="json")

        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that no new transaction was added to the database
        self.assertEqual(Transaction.objects.count(), 0)

    def test_user_cannot_access_other_user_transactions(self):
        # Create a cryptocurrency entry
        cryptocurrency = Cryptocurrency.objects.create(name="Bitcoin", symbol="BTC")

        # Create another user with their own transactions
        other_user = get_user_model().objects.create_user(
            email="otheruser@example.com",
            password="otheruserpassword",
        )
        other_user_transactions = [
            {
                "crypto": cryptocurrency,  # Use the Cryptocurrency instance
                "date": "2023-09-01T00:00:00Z",
                "type": "buy",
                "amount": "1.0",
                "price": "100.0",
            },
        ]
        for transaction_data in other_user_transactions:
            Transaction.objects.create(user=other_user, **transaction_data)

        # Attempt to retrieve the other user's transactions
        response = self.client.get(TRANSACTION_URL)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        authenticated_user_transactions = Transaction.objects.filter(user=self.user)
        for transaction in authenticated_user_transactions:
            self.assertIn(
                {"crypto": transaction.crypto.symbol, "type": transaction.type},
                response.data,
            )

        # Check that the other user's transactions are not present in the response
        for transaction in other_user_transactions:
            self.assertNotIn(
                {"crypto": transaction["crypto"], "type": transaction["type"]},
                response.data,
            )
