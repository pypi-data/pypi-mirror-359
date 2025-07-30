from esewa import (
    esewa_payment_gateway,
    esewa_check_status,
    PaymentRequestError,
    ValidationError,
    generate_unique_id,
)


amount = 1000
product_delivery_charge = 50
product_service_charge = 20
tax_amount = 30

def test_esewa_payment():
    """
    Initiates a payment request to eSewa and then checks the status
    using the same transaction UUID.
    """
    transaction_id = generate_unique_id()
    total_amount = amount + product_delivery_charge + product_service_charge + tax_amount

    try:
        payment_response = esewa_payment_gateway(
            amount=amount,
            product_delivery_charge=product_delivery_charge,
            product_service_charge=product_service_charge,
            tax_amount=tax_amount,
            transaction_uuid=transaction_id,
            product_code="EPAYTEST",
            secret="8gBm/:&EnhH.1/q",  
            success_url="https://example.com/success",
            failure_url="https://example.com/failure",
            esewa_payment_url="https://rc-epay.esewa.com.np/api/epay/main/v2/form"
        )
        print("✅ Payment Response:", payment_response['status'])

        status_response = esewa_check_status(
            total_amount=total_amount,
            transaction_uuid=transaction_id,
            product_code="EPAYTEST",
            status_check_url="https://rc.esewa.com.np/api/epay/transaction/status/"
        )
        print("📦 Status Check Response:", status_response)

    except PaymentRequestError as e:
        print("Payment failed:", e)
    except ValidationError as e:
        print("Invalid input:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__":
    test_esewa_payment()
