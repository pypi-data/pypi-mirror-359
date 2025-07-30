# eSewa Python SDK

A Python package to integrate with **eSewa** payment gateway, enabling you to initiate payments and check transaction status easily.

---

## Features

- Initiate payment requests to eSewa
- Verify payment transaction status
- Generate unique transaction IDs
- Simple and easy-to-use API
- Designed to work well with Django/DRF and any Python web framework

---

## Installation

```bash
pip install esewa

```


## Configuration
Make sure to set your eSewa credentials and URLs correctly when calling the functions.

- secret — Your eSewa secret key

- success_url — URL eSewa redirects after successful payment

- failure_url — URL eSewa redirects after failed payment

- esewa_payment_url — eSewa payment endpoint (testing or production)

- status_check_url — eSewa transaction status check endpoint




## Usage

```python 

from esewa import (
    esewa_payment_gateway, 
    esewa_check_status, 
    generate_unique_id, 
    PaymentRequestError, 
    ValidationError
)

amount = 1000
product_delivery_charge = 50
product_service_charge = 20
tax_amount = 30
transaction_id = generate_unique_id()

def test_payment():
    try:
        response = esewa_payment_gateway(
            amount=amount,
            product_delivery_charge=product_delivery_charge,
            product_service_charge=product_service_charge,
            tax_amount=tax_amount,
            transaction_uuid=transaction_id,
            product_code="EPAYTEST",
            secret="YOUR_ESEWA_SECRET",
            success_url="https://yourdomain.com/payment-success",
            failure_url="https://yourdomain.com/payment-failure",
            esewa_payment_url="https://rc-epay.esewa.com.np/api/epay/main/v2/form"
        )
        print("Payment Response:", response)
    except PaymentRequestError as e:
        print("Payment failed:", e)
    except ValidationError as e:
        print("Invalid input:", e)

def test_status_check():
    try:
        response = esewa_check_status(
            total_amount=amount + product_delivery_charge + product_service_charge + tax_amount,
            transaction_uuid=transaction_id,
            product_code="EPAYTEST",
            status_check_url="https://rc.esewa.com.np/api/epay/transaction/status/"
        )
        print("Status Response:", response)
    except ValidationError as e:
        print("Invalid input:", e)
    except Exception as e:
        print("Status check failed:", e)

if __name__ == "__main__":
    initiate_payment()
    status_check()


 ```


## Integration with Django REST Framework

You can easily integrate this package within Django views or DRF viewsets to handle payment requests and status checks.

1.  Create a model to store transaction info

```python

from django.db import models
from products.models import Product 

class Transaction(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETE", "Complete"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="transactions")
    transaction_uuid = models.CharField(max_length=255, unique=True)
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_uuid} - {self.status}"

```

2. Create Serializers

```python

from rest_framework import serializers
from .models import Transaction
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']

class TransactionSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_uuid', 'amount', 'status', 'created_at', 'updated_at', 'product', 'product_id']

```

2. Create Views to handle Esewa transactions

```python

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from .serializers import TransactionSerializer
from products.models import Product
from esewa import esewa_payment_gateway, esewa_check_status, generate_unique_id


class EsewaInitiatePaymentView(APIView):
    def post(self, request):
        try:
            product = Product.objects.get(id=request.data["product_id"])
            transaction_uuid = generate_unique_id()

            esewa_response = esewa_payment_gateway(
                amount=product.price,
                product_delivery_charge=0,
                product_service_charge=0,
                tax_amount=0,
                transaction_uuid=transaction_uuid,
                product_code="your_product_code",  # Replace with your actual product code
                secret="your_secret",              # Replace with your actual secret
                success_url="your_success_url",    # Replace with your actual success URL
                failure_url="your_failure_url",    # Replace with your actual failure URL
                esewa_payment_url="your_payment_url"  # Replace with your actual payment URL
            )

            transaction = Transaction.objects.create(
                product=product,
                transaction_uuid=transaction_uuid,
                amount=product.price,
                status="PENDING"
            )

            return Response({
                "transaction": TransactionSerializer(transaction).data,
                "payment_url": esewa_response.get("payment_url"),
                "status": esewa_response.get("status"),
                "message": esewa_response.get("message"),
            })

        except Product.DoesNotExist:
            return Response({"error": "Invalid product ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EsewaStatusCheckView(APIView):
    def post(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = (
                Transaction.objects
                .filter(product_id=product_id)
                .latest("created_at")
            )

            status_response = esewa_check_status(
                total_amount=transaction.amount,
                transaction_uuid=transaction.transaction_uuid,
                product_code="your_product_code",  # Replace with your actual product code
                status_check_url="your_status_check_url"  # Replace with your actual status check URL
            )

            # Example: status_response might look like {'status': 200, 'data': {'status': 'COMPLETE', ...}}
            transaction.status = status_response.get("data", {}).get("status", transaction.status)
            transaction.save()

            return Response(TransactionSerializer(transaction).data)

        except Transaction.DoesNotExist:
            return Response({"error": "No transaction found for this product"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

If you want to contribute to this project, feel free to submit a pull request or open an issue for discussion.

## Contact
For any questions or issues, please open an issue on the [GitHub repository](https://github.com/sahilverse/esewa-python/issues).
