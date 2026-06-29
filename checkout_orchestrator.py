import os
import hmac
import hashlib
import json
from typing import List, Dict, Any, Optional

class CheckoutOrchestrationError(Exception):
    """Raised when calculation parameters or signatures are invalid."""
    pass

class CommerceCheckoutOrchestrator:
    """
    Production-ready orchestrator for auditing e-commerce carts, applying discount logic,
    calculating shipping, and outputting payment gateway configurations.
    Includes built-in SHA256 integrity signature calculations.
    """
    def __init__(self, signing_secret: Optional[str] = None):
        self.signing_secret = signing_secret or os.environ.get("CHECKOUT_SIGNING_SECRET", "default_secret_key")

    def orchestrate_checkout(
        self,
        cart_items: List[Dict[str, Any]],
        discount_code: Optional[str],
        shipping_address: Dict[str, Any],
        gateway: str
    ) -> Dict[str, Any]:
        """
        Processes cart items, applies pricing reductions, evaluates delivery costs,
        and constructs signed checkout API request schemas.
        """
        if not cart_items:
            raise CheckoutOrchestrationError("Cart must contain at least one item.")

        # 1. Compute subtotal
        subtotal = 0.0
        for item in cart_items:
            sku = item.get("sku")
            price = float(item.get("price", 0.0))
            qty = int(item.get("quantity", 0))
            if price < 0 or qty <= 0:
                raise CheckoutOrchestrationError(f"Invalid price or quantity for SKU {sku}.")
            subtotal += price * qty

        # 2. Compute discount code
        discount_amount = 0.0
        if discount_code:
            code_upper = discount_code.upper().strip()
            if code_upper == "SAVE20":
                discount_amount = round(subtotal * 0.20, 2)
            elif code_upper == "FREESHIP":
                # Marked for shipping cost cancellation
                pass

        # 3. Calculate shipping
        country = shipping_address.get("country", "US").upper()
        if country == "US":
            shipping_cost = 5.99
        else:
            shipping_cost = 19.99

        if discount_code and discount_code.upper().strip() == "FREESHIP":
            shipping_cost = 0.0

        # 4. Grand total
        grand_total = round((subtotal - discount_amount) + shipping_cost, 2)
        if grand_total < 0:
            grand_total = 0.0

        pricing_summary = {
            "subtotal": round(subtotal, 2),
            "discount_amount": discount_amount,
            "shipping_cost": shipping_cost,
            "grand_total": grand_total
        }

        # 5. Build payment gateway payload configurations
        gateway_payload = {}
        if gateway.lower() == "stripe":
            gateway_payload = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {"name": f"SKU: {item['sku']}"},
                            "unit_amount": int(float(item["price"]) * 100)
                        },
                        "quantity": int(item["quantity"])
                    } for item in cart_items
                ],
                "mode": "payment",
                "shipping_options": [
                    {
                        "shipping_rate_data": {
                            "type": "fixed_amount",
                            "fixed_amount": {"amount": int(shipping_cost * 100), "currency": "usd"},
                            "display_name": "Standard Delivery"
                        }
                    }
                ]
            }
            if discount_amount > 0:
                # Mock voucher application for Stripe Session creation API
                gateway_payload["discounts"] = [{"coupon": "SAVE20_COUPON"}]
        else:
            # PayPal payload
            gateway_payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{grand_total:.2f}",
                            "breakdown": {
                                "item_total": {"currency_code": "USD", "value": f"{subtotal - discount_amount:.2f}"},
                                "shipping": {"currency_code": "USD", "value": f"{shipping_cost:.2f}"}
                            }
                        }
                    }
                ]
            }

        # 6. Generate cryptographic signature of checkout state to prevent client-side tampering
        serialized_state = json.dumps({
            "summary": pricing_summary,
            "gateway": gateway
        }, sort_keys=True)
        
        signature = hmac.new(
            self.signing_secret.encode("utf-8"),
            serialized_state.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return {
            "pricing_summary": pricing_summary,
            "gateway_payload": gateway_payload,
            "signature_hash": signature
        }
