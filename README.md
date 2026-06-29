# Commerce Agent Checkout Orchestrator Skill

This repository contains the **Commerce Agent Checkout Orchestrator Skill** — an agent configuration skill config (`skill.json`), a production-ready Python SDK client (`checkout_orchestrator.py`), and executable verification tests. It is designed to orchestrate checkout sessions across payment gateways (Stripe & PayPal), calculate dynamic discounts, resolve location-based shipping, and compute HMAC-SHA256 verification hashes to prevent checkout request tampering.

---

## 🚀 Capabilities

* **HMAC-SHA256 Cart Audits:** Prevents client-side parameter tampering by signing pricing totals and metadata via merchant signing keys.
* **Percentage & Shipping Discounts:** Supports multiple promo coupons like "SAVE20" (20% off subtotal) and "FREESHIP" (zero shipping cost).
* **Multi-Gateway Formatting:** Outputs complete API structure configurations ready to send to Stripe Checkout Sessions or PayPal Order Intent endpoints.

---

## 🛠️ Setup & Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configuration:
   Set your merchant signing secret environment variable (defaults to `default_secret_key` if absent):
   * **PowerShell**:
     ```powershell
     $env:CHECKOUT_SIGNING_SECRET="your_secret_key"
     ```
   * **bash**:
     ```bash
     export CHECKOUT_SIGNING_SECRET="your_secret_key"
     ```

---

## 💻 SDK Usage Reference

```python
from checkout_orchestrator import CommerceCheckoutOrchestrator

# Initialize client with secret key
orchestrator = CommerceCheckoutOrchestrator(signing_secret="merchant_secret")

# Run orchestration
session = orchestrator.orchestrate_checkout(
    cart_items=[{"sku": "SKU-01", "price": 45.00, "quantity": 2}],
    discount_code="SAVE20",
    shipping_address={"country": "US", "postal_code": "90210"},
    gateway="stripe"
)

print(f"Grand Total: ${session['pricing_summary']['grand_total']:.2f}")
print(f"HMAC Verification Hash: {session['signature_hash']}")
```

---

## 📜 License
This project is licensed under the MIT License.
