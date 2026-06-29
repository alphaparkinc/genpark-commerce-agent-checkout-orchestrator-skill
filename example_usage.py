import sys
import json
from checkout_orchestrator import CommerceCheckoutOrchestrator

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("=== Commerce Agent Checkout Orchestrator Verification ===")
    orchestrator = CommerceCheckoutOrchestrator(signing_secret="live_merchant_signing_key_abc123")

    # Mock Cart
    cart = [
        {"sku": "SKU-ZENITH-SP1", "price": 120.00, "quantity": 1},
        {"sku": "SKU-ZENITH-ACC", "price": 15.50, "quantity": 2}
    ]
    
    address = {"country": "US", "postal_code": "90210"}

    # Test Scenario A: Checkout with Stripe & Discount Code
    print("\n--- Scenario A: Stripe Checkout with SAVE20 coupon ---")
    result_a = orchestrator.orchestrate_checkout(
        cart_items=cart,
        discount_code="SAVE20",
        shipping_address=address,
        gateway="stripe"
    )
    
    print("\nPricing Summary Output:")
    print(json.dumps(result_a["pricing_summary"], indent=2))
    
    print("\nCryptographic Verification Hash:")
    print(result_a["signature_hash"])
    
    print("\nStripe API Payload Draft:")
    print(json.dumps(result_a["gateway_payload"], indent=2))

    # Test Scenario B: Checkout with PayPal & Out-of-Country shipping
    print("\n--- Scenario B: PayPal Checkout (International Address) ---")
    intl_address = {"country": "DE", "postal_code": "10115"}
    result_b = orchestrator.orchestrate_checkout(
        cart_items=cart,
        discount_code=None,
        shipping_address=intl_address,
        gateway="paypal"
    )
    
    print("\nPricing Summary Output (DE Delivery):")
    print(json.dumps(result_b["pricing_summary"], indent=2))
    
    print("\nPayPal Order Payload Draft:")
    print(json.dumps(result_b["gateway_payload"], indent=2))

if __name__ == "__main__":
    main()
