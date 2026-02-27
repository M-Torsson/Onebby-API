# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from decimal import Decimal
from datetime import datetime

from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.address import Address
from app.schemas.order import OrderCreate, OrderUpdate


class CRUDOrder:
    """CRUD operations for Order"""
    
    def get(self, db: Session, id: int) -> Optional[Order]:
        """Get order by ID"""
        return db.query(Order).filter(Order.id == id).first()
    
    def get_by_user(
        self, 
        db: Session, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get all orders for a specific user"""
        return db.query(Order)\
            .filter(Order.user_id == user_id)\
            .order_by(Order.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        shipping_status: Optional[str] = None,
        user_type: Optional[str] = None
    ) -> List[Order]:
        """
        Get multiple orders with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by order status
            payment_status: Filter by payment status
            shipping_status: Filter by shipping status
            user_type: Filter by user type (customer/company/guest)
        
        Returns:
            List of orders
        """
        query = db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        if shipping_status:
            query = query.filter(Order.shipping_status == shipping_status)
        if user_type:
            query = query.filter(Order.user_type == user_type)
        
        return query.order_by(Order.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def count(
        self,
        db: Session,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        shipping_status: Optional[str] = None
    ) -> int:
        """Count orders with optional filters"""
        query = db.query(func.count(Order.id))
        
        if status:
            query = query.filter(Order.status == status)
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        if shipping_status:
            query = query.filter(Order.shipping_status == shipping_status)
        
        return query.scalar()
    
    def create_from_cart(
        self,
        db: Session,
        cart: Cart,
        order_data: OrderCreate,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Order:
        """
        Create an order from a cart
        
        This is the main function for converting a cart to an order during checkout.
        
        Args:
            db: Database session
            cart: Cart object to convert
            order_data: Order creation data from checkout form
            user_id: User ID (if logged in)
            session_id: Session ID (if guest)
        
        Returns:
            Created Order object
        """
        if not cart or not cart.items:
            raise ValueError("Cannot create order from empty cart")
        
        # Determine user type
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_type = user.reg_type  # 'user' or 'company'
                if user_type == 'user':
                    user_type = 'customer'
            else:
                user_type = 'guest'
        else:
            user_type = 'guest'
        
        # Calculate order totals
        subtotal = Decimal('0.00')
        
        for cart_item in cart.items:
            # Base product price
            item_subtotal = Decimal(str(cart_item.price_at_add)) * cart_item.quantity
            
            # Add delivery option price
            if cart_item.delivery_option and cart_item.delivery_option.get('price'):
                item_subtotal += Decimal(str(cart_item.delivery_option['price']))
            
            # Add warranty option price
            if cart_item.warranty_option and cart_item.warranty_option.get('price'):
                item_subtotal += Decimal(str(cart_item.warranty_option['price']))
            
            subtotal += item_subtotal
        
        # Calculate shipping cost (can be dynamic based on shipping_method)
        # For now, using a simple fixed cost
        shipping_cost = Decimal('10.00') if order_data.shipping_method else Decimal('0.00')
        
        # Calculate tax (IVA - can be dynamic based on country)
        # For Italy, VAT is typically 22%
        # For now, set to 0 (can be calculated based on business logic)
        tax = Decimal('0.00')
        
        # Calculate discount (if any)
        discount = Decimal('0.00')
        
        # Calculate total
        total_amount = subtotal + shipping_cost + tax - discount
        
        # Create order
        order = Order(
            user_id=user_id,
            session_id=session_id,
            user_type=user_type,
            customer_info=order_data.customer_info,
            billing_address=order_data.billing_address,
            shipping_address=order_data.shipping_address,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            discount=discount,
            total_amount=total_amount,
            currency='EUR',
            payment_status='pending',
            payment_method=order_data.payment_method,
            shipping_method=order_data.shipping_method,
            shipping_status='pending',
            status='pending',
            customer_note=order_data.customer_note
        )
        
        db.add(order)
        db.flush()  # Get order.id before adding items
        
        # Create order items from cart items
        for cart_item in cart.items:
            # Get product details
            product = cart_item.product
            if not product:
                continue  # Skip if product was deleted
            
            # Get product title
            product_title = "Unknown Product"
            if product.translations and len(product.translations) > 0:
                product_title = product.translations[0].title
            
            # Get product image
            product_image = None
            if product.images and len(product.images) > 0:
                product_image = product.images[0].url
            
            # Get variant attributes if applicable
            variant_attributes = None
            if cart_item.product_variant_id:
                variant = cart_item.product_variant
                if variant:
                    # Build variant attributes dict
                    # This depends on your variant structure
                    variant_attributes = {}
                    # Add variant-specific attributes here
            
            # Calculate item prices
            unit_price = Decimal(str(cart_item.price_at_add))
            quantity = cart_item.quantity
            item_subtotal = unit_price * quantity
            item_discount = Decimal('0.00')
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_variant_id=cart_item.product_variant_id,
                product_title=product_title,
                product_sku=product.reference,
                product_type=product.product_type,
                product_image=product_image,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=item_subtotal,
                discount=item_discount,
                delivery_option=cart_item.delivery_option,
                warranty_option=cart_item.warranty_option,
                variant_attributes=variant_attributes
            )
            
            db.add(order_item)
        
        db.commit()
        db.refresh(order)
        
        return order
    
    def update(
        self,
        db: Session,
        order_id: int,
        order_update: OrderUpdate
    ) -> Optional[Order]:
        """
        Update an order
        
        Used by admin to update order status, tracking number, notes, etc.
        
        Args:
            db: Database session
            order_id: Order ID to update
            order_update: Update data
        
        Returns:
            Updated Order object or None if not found
        """
        order = self.get(db, id=order_id)
        if not order:
            return None
        
        update_data = order_update.model_dump(exclude_unset=True)
        
        # Update timestamps based on status changes
        current_time = datetime.now()
        
        if 'payment_status' in update_data:
            if update_data['payment_status'] == 'completed' and not order.paid_at:
                order.paid_at = current_time
        
        if 'status' in update_data:
            if update_data['status'] == 'confirmed' and not order.confirmed_at:
                order.confirmed_at = current_time
            elif update_data['status'] == 'cancelled' and not order.cancelled_at:
                order.cancelled_at = current_time
        
        if 'shipping_status' in update_data:
            if update_data['shipping_status'] == 'shipped' and not order.shipped_at:
                order.shipped_at = current_time
            elif update_data['shipping_status'] == 'delivered' and not order.delivered_at:
                order.delivered_at = current_time
        
        # Apply updates
        for field, value in update_data.items():
            setattr(order, field, value)
        
        db.commit()
        db.refresh(order)
        
        return order
    
    def update_payment_status(
        self,
        db: Session,
        order_id: int,
        status: str,
        transaction_id: Optional[str] = None
    ) -> Optional[Order]:
        """
        Update payment status
        
        Called by payment gateway webhooks/callbacks.
        
        Args:
            db: Database session
            order_id: Order ID
            status: New payment status (pending/processing/completed/failed/refunded)
            transaction_id: Transaction ID from payment gateway
        
        Returns:
            Updated Order object or None if not found
        """
        order = self.get(db, id=order_id)
        if not order:
            return None
        
        order.payment_status = status
        
        if transaction_id:
            order.payment_transaction_id = transaction_id
        
        if status == 'completed' and not order.paid_at:
            order.paid_at = datetime.now()
            # Also update order status to confirmed
            if order.status == 'pending':
                order.status = 'confirmed'
                order.confirmed_at = datetime.now()
        
        db.commit()
        db.refresh(order)
        
        return order
    
    def update_warranty_info(
        self,
        db: Session,
        order_item_id: int,
        contract_number: str,
        pin_code: str,
        registered_at: Optional[datetime] = None
    ) -> Optional[OrderItem]:
        """
        Update warranty information in order item
        
        Called after successful Garanzia3 registration.
        
        Args:
            db: Database session
            order_item_id: Order item ID
            contract_number: Garanzia3 contract number
            pin_code: Garanzia3 PIN code
            registered_at: Registration timestamp
        
        Returns:
            Updated OrderItem or None if not found
        """
        order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
        if not order_item or not order_item.warranty_option:
            return None
        
        # Update warranty_option JSON
        warranty_option = order_item.warranty_option.copy()
        warranty_option['contract_number'] = contract_number
        warranty_option['pin_code'] = pin_code
        warranty_option['registered_at'] = (registered_at or datetime.now()).isoformat()
        warranty_option['registration_error'] = None
        
        order_item.warranty_option = warranty_option
        
        db.commit()
        db.refresh(order_item)
        
        return order_item
    
    def update_warranty_error(
        self,
        db: Session,
        order_item_id: int,
        error_message: str
    ) -> Optional[OrderItem]:
        """
        Update warranty registration error
        
        Called when Garanzia3 registration fails.
        
        Args:
            db: Database session
            order_item_id: Order item ID
            error_message: Error message from Garanzia3
        
        Returns:
            Updated OrderItem or None if not found
        """
        order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
        if not order_item or not order_item.warranty_option:
            return None
        
        # Update warranty_option JSON
        warranty_option = order_item.warranty_option.copy()
        warranty_option['registration_error'] = error_message
        
        order_item.warranty_option = warranty_option
        
        db.commit()
        db.refresh(order_item)
        
        return order_item
    
    def get_orders_with_failed_warranty_registration(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Get orders that have items with failed warranty registration
        
        Used by admin to retry failed registrations.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of orders with failed warranty registrations
        """
        # This is a complex query - we need to find orders where any item
        # has warranty_option with registration_error not null
        orders = db.query(Order)\
            .join(OrderItem)\
            .filter(
                and_(
                    OrderItem.warranty_option.isnot(None),
                    OrderItem.warranty_option['registration_error'].astext.isnot(None)
                )
            )\
            .order_by(Order.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return orders
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get order statistics
        
        Used by admin dashboard.
        
        Returns:
            Dictionary with statistics
        """
        # Total orders
        total_orders = db.query(func.count(Order.id)).scalar()
        
        # Total revenue
        total_revenue = db.query(func.sum(Order.total_amount))\
            .filter(Order.payment_status == 'completed')\
            .scalar() or Decimal('0.00')
        
        # Orders by status
        pending_orders = self.count(db, status='pending')
        confirmed_orders = self.count(db, status='confirmed')
        completed_orders = self.count(db, status='completed')
        cancelled_orders = self.count(db, status='cancelled')
        
        # Orders by payment status
        unpaid_orders = self.count(db, payment_status='pending')
        paid_orders = self.count(db, payment_status='completed')
        
        # Orders by shipping status
        pending_shipment = self.count(db, shipping_status='pending')
        shipped_orders = self.count(db, shipping_status='shipped')
        delivered_orders = self.count(db, shipping_status='delivered')
        
        # Warranty statistics
        orders_with_warranty = db.query(func.count(func.distinct(Order.id)))\
            .join(OrderItem)\
            .filter(OrderItem.warranty_option.isnot(None))\
            .scalar()
        
        # Calculate warranty revenue
        # Sum all warranty prices from order items
        warranty_revenue = Decimal('0.00')
        orders_with_warranties = db.query(Order)\
            .join(OrderItem)\
            .filter(
                and_(
                    OrderItem.warranty_option.isnot(None),
                    Order.payment_status == 'completed'
                )
            )\
            .all()
        
        for order in orders_with_warranties:
            for item in order.items:
                if item.warranty_option and item.warranty_option.get('price'):
                    warranty_revenue += Decimal(str(item.warranty_option['price']))
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'unpaid_orders': unpaid_orders,
            'paid_orders': paid_orders,
            'pending_shipment': pending_shipment,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'orders_with_warranty': orders_with_warranty,
            'warranty_revenue': warranty_revenue
        }
    
    def create_direct(
        self,
        db: Session,
        order_data,  # OrderCreateDirect schema
        user_id: int
    ) -> Order:
        """
        Create an order directly from items (new API format)
        
        This bypasses the cart system and creates an order directly
        from the provided items in the request.
        
        Args:
            db: Database session
            order_data: OrderCreateDirect schema with items and payment info
            user_id: User ID (required - no guest users)
        
        Returns:
            Created Order object
        
        Raises:
            ValueError: If validation fails
        """
        # 1. Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # 2. Get address from database
        address = db.query(Address).filter(
            and_(
                Address.id == order_data.address_id,
                Address.user_id == user_id
            )
        ).first()
        
        if not address:
            raise ValueError(f"Address with ID {order_data.address_id} not found for this user")
        
        # 3. Convert address to JSON format for order
        billing_address = {
            "address_type": address.address_type,
            "name": address.name,
            "last_name": address.last_name,
            "company_name": address.company_name,
            "address_house_number": address.address_house_number,
            "house_number": address.house_number,
            "city": address.city,
            "postal_code": address.postal_code,
            "country": address.country,
            "phone": address.phone
        }
        shipping_address = billing_address.copy()  # Same as billing for now
        
        # 4. Build customer_info from user and order_data
        if order_data.reg_type == 'customer':
            customer_info = {
                "reg_type": "user",
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email,
                "title": getattr(user, 'title', 'Sig.')
            }
        else:  # company
            customer_info = {
                "reg_type": "company",
                "company_name": getattr(user, 'company_name', ''),
                "email": user.email,
                "vat_number": getattr(user, 'vat_number', ''),
                "tax_code": getattr(user, 'tax_code', ''),
                "sdi_code": getattr(user, 'sdi_code', ''),
                "pec": getattr(user, 'pec', '')
            }
        
        # 5. Validate and process items
        order_items_data = []
        total_calculated = Decimal('0.00')
        total_warranty = Decimal('0.00')
        total_shipping = Decimal('0.00')
        
        for item in order_data.items:
            # Check product exists
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise ValueError(f"Product with ID {item.product_id} not found")
            
            # Check stock availability
            if product.stock_quantity < item.qty:
                raise ValueError(
                    f"Insufficient stock for product {item.product_id}. "
                    f"Available: {product.stock_quantity}, Requested: {item.qty}"
                )
            
            # Get product details
            product_title = "Unknown Product"
            if product.translations and len(product.translations) > 0:
                product_title = product.translations[0].title
            
            product_image = None
            if product.images and len(product.images) > 0:
                product_image = product.images[0].url
            
            # Calculate prices
            unit_price = Decimal(str(product.price))
            quantity = item.qty
            item_subtotal = unit_price * quantity
            
            # Build warranty_option JSON
            warranty_option = None
            if item.warranty:
                warranty_option = {
                    "title": item.warranty.title,
                    "price": float(item.warranty.cost),
                    "contract_number": None,
                    "pin_code": None,
                    "registered_at": None,
                    "registration_error": None
                }
                total_warranty += item.warranty.cost
            
            # Build delivery_option JSON
            delivery_option = None
            if item.delivery_opt:
                delivery_option = {
                    "title": item.delivery_opt.title,
                    "price": float(item.delivery_opt.cost)
                }
                total_shipping += item.delivery_opt.cost
            
            # Add to total
            total_calculated += item_subtotal
            
            # Store item data for later
            order_items_data.append({
                "product": product,
                "product_title": product_title,
                "product_image": product_image,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": item_subtotal,
                "warranty_option": warranty_option,
                "delivery_option": delivery_option
            })
        
        # 6. Calculate totals automatically
        # Subtotal = all products prices
        subtotal = total_calculated
        
        # Shipping cost = sum of all delivery options
        shipping_cost = total_shipping
        
        # Tax (can be calculated based on country/business logic)
        tax = Decimal('0.00')
        
        # Discount (can be applied if needed)
        discount = Decimal('0.00')
        
        # Total amount = subtotal + shipping + tax - discount
        # Note: warranty costs are already included in item prices if added
        total_amount = subtotal + total_warranty + shipping_cost + tax - discount
        
        # 7. Build payment_info JSON
        payment_info = {
            "payment_type": order_data.payment_info.payment_type,
            "payment_status": order_data.payment_info.payment_status,
            "invoice_num": order_data.payment_info.invoice_num,
            "payment_id": order_data.payment_info.payment_id
        }
        
        # Determine payment_status based on payment_info
        payment_status = "completed" if order_data.payment_info.payment_status == "successful" else "pending"
        
        # 8. Create Order
        order = Order(
            user_id=user_id,
            session_id=None,
            user_type='customer' if order_data.reg_type == 'customer' else 'company',
            customer_info=customer_info,
            billing_address=billing_address,
            shipping_address=shipping_address,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            discount=discount,
            total_amount=total_amount,
            currency='EUR',
            payment_status=payment_status,
            payment_method=order_data.payment_info.payment_type,
            payment_info=payment_info,
            order_date=order_data.order_date,
            shipping_method='standard',
            shipping_status='pending',
            status='pending' if payment_status == 'pending' else 'confirmed',
            customer_note=order_data.customer_note
        )
        
        db.add(order)
        db.flush()  # Get order.id
        
        # 9. Create Order Items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                product_variant_id=None,
                product_title=item_data["product_title"],
                product_sku=item_data["product"].reference,
                product_type=item_data["product"].product_type,
                product_image=item_data["product_image"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"],
                discount=Decimal('0.00'),
                delivery_option=item_data["delivery_option"],
                warranty_option=item_data["warranty_option"],
                variant_attributes=None
            )
            db.add(order_item)
            
            # 10. Update product stock
            item_data["product"].stock_quantity -= item_data["quantity"]
        
        db.commit()
        db.refresh(order)
        
        return order


# Create a singleton instance
crud_order = CRUDOrder()
