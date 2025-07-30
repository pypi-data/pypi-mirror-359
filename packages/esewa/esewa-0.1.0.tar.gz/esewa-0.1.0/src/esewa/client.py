import requests
from typing import Dict
from .utils import generate_hmac_sha256_hash


def esewa_payment_gateway(
    amount: float,
    product_delivery_charge: float,
    product_service_charge: float,
    tax_amount: float,
    transaction_uuid: str,
    product_code: str,
    secret: str,
    success_url: str,
    failure_url: str,
    esewa_payment_url: str,
    algorithm: str = "sha256",
    encoding: str = "base64"
) -> Dict:
    """
    Initiate a payment request to the eSewa gateway.

    This function prepares the payment parameters, generates a secure signature,
    and sends a POST request with query parameters to the eSewa payment form URL.

    Args:
        amount (float): Base product amount.
        product_delivery_charge (float): Delivery charge applied.
        product_service_charge (float): Service charge applied.
        tax_amount (float): Tax amount applied.
        transaction_uuid (str): Unique transaction identifier.
        product_code (str): Registered product code with eSewa.
        secret (str): Merchant secret key used for HMAC generation.
        success_url (str): URL to redirect after successful payment.
        failure_url (str): URL to redirect after failed payment.
        esewa_payment_url (str): Full eSewa form URL (e.g., sandbox or live).
        algorithm (str): Hash algorithm for signature. Default is "sha256".
        encoding (str): Encoding type for the signature. Default is "base64".

    Returns:
        Dict: Contains status code, message, and the raw HTML form
              returned by eSewa (which should be rendered on the frontend).
    """
    total_amount = amount + product_delivery_charge + product_service_charge + tax_amount

    data = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = generate_hmac_sha256_hash(data, secret, algorithm, encoding)

    payment_data = {
        "amount": amount,
        "product_delivery_charge": product_delivery_charge,
        "product_service_charge": product_service_charge,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "success_url": success_url,
        "failure_url": failure_url,
        "signature": signature,
    }

    try:
        response = requests.post(esewa_payment_url, params=payment_data, timeout=10)

        return {
            "status": response.status_code,
            "message": "Payment form received",
            "form_html": response.text  
        }

    except Exception as e:
        return {
            "status": 500,
            "message": f"Error during payment request: {str(e)}"
        }


def esewa_check_status(
    total_amount: float,
    transaction_uuid: str,
    product_code: str,
    status_check_url: str
) -> Dict:
    """
    Check the payment status of a transaction from eSewa.

    Args:
        total_amount (float): Total amount of the transaction.
        transaction_uuid (str): Unique transaction identifier.
        product_code (str): Registered product code with eSewa.
        status_check_url (str): eSewa API URL to check transaction status.

    Returns:
        Dict: Response from eSewa as a dictionary. Includes status, ref_id, etc.
    """
    params = {
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code
    }

    try:
        response = requests.get(status_check_url, params=params, timeout=10)
        return response.json()

    except Exception as e:
        return {
            "status": 500,
            "message": f"Status check failed: {str(e)}"
        }


