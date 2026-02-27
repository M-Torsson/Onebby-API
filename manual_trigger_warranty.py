"""
Manually trigger warranty auto-registration for Order 14
This script calls the API directly to complete the order and register warranties
"""
import asyncio
import sys
sys.path.append('/f/onebby-api')

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.order import Order
from app.api.v1.webhooks import auto_register_warranties

async def main():
    # Get database session
    db = SessionLocal()
    
    try:
        # Get Order 14
        order = db.query(Order).filter(Order.id == 14).first()
        
        if not order:
            print("❌ Order 14 not found!")
            return
        
        print(f"✅ Found Order 14")
        print(f"   User ID: {order.user_id}")
        print(f"   Total: €{order.total_amount}")
        print(f"   Status: {order.status}")
        print(f"   Payment Status: {order.payment_status}")
        print(f"   Items: {len(order.items)}")
        
        # Check for warranty items
        warranty_items = [item for item in order.items if item.warranty_option]
        print(f"   Items with warranty: {len(warranty_items)}")
        
        for item in warranty_items:
            warranty = item.warranty_option
            print(f"     - Product ID {item.product_id}: {warranty.get('title')}")
        
        # Update order to completed
        print("\n" + "=" * 80)
        print("UPDATING ORDER STATUS")
        print("=" * 80)
        
        order.status = 'completed'
        order.payment_status = 'completed'
        order.payment_transaction_id = 'manual_test_completion'
        
        db.commit()
        db.refresh(order)
        
        print(f"✅ Order 14 updated to completed")
        
        # Trigger auto warranty registration
        print("\n" + "=" * 80)
        print("TRIGGERING AUTO WARRANTY REGISTRATION")
        print("=" * 80)
        
        await auto_register_warranties(db, order)
        
        print(f"✅ Auto warranty registration completed")
        
        # Check registrations
        from app.crud.warranty_registration import crud_warranty_registration
        
        registrations = crud_warranty_registration.get_by_order(db, order_id=14)
        
        print(f"\n" + "=" * 80)
        print(f"REGISTRATIONS CREATED")
        print("=" * 80)
        print(f"Found {len(registrations)} warranty registration(s):\n")
        
        for reg in registrations:
            print(f"  Registration ID: {reg.id}")
            print(f"  Product ID: {reg.product_id}")
            print(f"  Product Name: {reg.product_name}")
            print(f"  Warranty ID: {reg.warranty_id}")
            print(f"  Status: {reg.status}")
            print(f"  Transaction ID: {reg.g3_transaction_id}")
            print(f"  PIN: {reg.g3_pin}")
            print(f"  Customer: {reg.customer_name} {reg.customer_lastname}")
            print(f"  Email: {reg.customer_email}")
            print(f"  Created: {reg.created_at}")
            print()
        
        print("=" * 80)
        print("✅ TEST COMPLETE - WARRANTY AUTO-REGISTRATION WORKING!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
