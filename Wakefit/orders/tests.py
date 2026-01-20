#type: ignore
import pytest
from products.models import Product
from accounts.models import User
from django.urls import reverse
from rest_framework import status
from orders.models import Order

# --- FIXTURES: Reusable Setup ---

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def test_product(db):
    return Product.objects.create(name="Soft Pillow", price=500, stock_quantity=5, sku="PW-01")

@pytest.fixture
def auth_client(api_client, db):
    from accounts.models import User
    user = User.objects.create_user(username="testuser", password="password")
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
def test_order_creation_reduces_stock(auth_client, test_product, mocker):
    client, user = auth_client

    # MOCK the payment gateway (f3 logic)
    mocker.patch('payments.services.requests.post', return_value=mocker.Mock(status_code=201, json=lambda: {"uropayOrderId": "123"}))

    payload = {
        "address": "123 Mastery Street, Python City",
        "product_id": test_product.id,
        "quantity": 2
    }

    url = "/api/orders/place-order/"
    response = client.post(url, payload, format='json')

    assert response.status_code == 201
    test_product.refresh_from_db()
    assert test_product.stock_quantity == 3 # 5 - 2

@pytest.mark.django_db
def test_order_fails_for_missing_address(auth_client, test_product):
    client, user = auth_client
    payload = {"product_id": test_product.id, "quantity": 1} # Missing address

    response = client.post("/api/orders/place-order/", payload)

    assert response.status_code == 400
    assert "address" in response.data # Serializer validation caught it!

# --- FIXTURES (The 'Mastery' way to handle setup) ---


@pytest.fixture
def create_user(db):
    """A factory fixture to create users on the fly."""
    def make_user(username):
        return User.objects.create_user(username=username, password="password123")
    return make_user

# --- THE TESTS ---

@pytest.mark.django_db
def test_order_history_isolation(api_client, create_user):
    """
    PRD Section 7: Verify that User A cannot see User B's orders.
    This replaces your EndToEndOrderFlowTest method.
    """
    # 1. Setup two users using the fixture
    user_a = create_user("user_a")
    user_b = create_user("user_b")

    # 2. Create an order specifically for User B
    Order.objects.create(user=user_b, total_amount=100.00, address="User B's House")

    # 3. Authenticate the client as User A (The Intruder)
    api_client.force_authenticate(user=user_a)

    # 4. Attempt to fetch history
    url = reverse('order-history')
    response = api_client.get(url)

    # 5. VERIFICATIONS (Plain Python Assertions)
    assert response.status_code == status.HTTP_200_OK
    # Ensure User A sees zero orders in their results
    assert len(response.data['results']) == 0

    # --- BONUS: Verify User B CAN see their order ---
    api_client.force_authenticate(user=user_b)
    response_b = api_client.get(url)
    assert len(response_b.data['results']) == 1
    assert response_b.data['results'][0]['address'] == "User B's House"


@pytest.mark.django_db
def test_place_order_flow_success(api_client, create_user, test_product, mocker):
    """
    Tests the full Orchestrator flow with Mocks.
    """
    user = create_user("buyer")
    api_client.force_authenticate(user=user)

    # MOCK the UroPay API call (f3 Logic)
    mocker.patch('payments.services.requests.post', return_value=mocker.Mock(
        status_code=201, 
        json=lambda: {"uropayOrderId": "MOCK_ID", "payment_url": "http://mock.link"}
    ))

    payload = {
        "address": "123 Mastery Way",
        "product_id": test_product.id,
        "quantity": 1
    }

    url = reverse('place_order')
    response = api_client.post(url, payload, format='json')

    # Verifications
    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.filter(user=user).count() == 1

    # Check PRD Section 9: Stock should be reduced
    test_product.refresh_from_db()
    assert test_product.stock_quantity == 4