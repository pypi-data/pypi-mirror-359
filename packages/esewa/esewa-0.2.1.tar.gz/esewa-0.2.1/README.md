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
from esewa import esewa_payment_gateway, esewa_check_status, generate_unique_id, base64_decode


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
        base64_data = request.data.get("data")

        if not base64_data:
            return Response({"error": "data is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_data = base64_decode(base64_data)
            transaction_uuid = decoded_data.get("transaction_uuid")

            transaction = (
                Transaction.objects
                .filter(transaction_uuid=transaction_uuid)
                .first()
            )

            if not transaction:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

            status_response = esewa_check_status(
                total_amount=transaction.amount,
                transaction_uuid=transaction.transaction_uuid,
                product_code="EPAYTEST", 
                status_check_url="https://rc.esewa.com.np/api/epay/transaction/status/"  
            )
            
            if status_response.get("status") == "SUCCESS":
                transaction.status = "COMPLETED"
            else:
                transaction.status = status_response.get("status", "FAILED")

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
