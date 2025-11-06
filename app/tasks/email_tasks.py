from app.celery_app import celery_app


@celery_app.task(name='send_order_confirmation')
def send_order_confirmation(order_id: int):
    """Send order confirmation email"""
    from app.database import SessionLocal
    from app.models import Order
    
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            customer_email = order.customer.email
            
            # TODO: Implement actual email sending
            print(f"Sending order confirmation to {customer_email}")
            print(f"   Order: #{order.order_number}")
            print(f"   Total: ${order.total}")
            
            # Example with SMTP:
            # from app.services.email_service import send_email
            # send_email(
            #     to=customer_email,
            #     subject=f"Order Confirmation #{order.order_number}",
            #     template="order_confirmation.html",
            #     context={"order": order}
            # )
            
        return {"order_id": order_id, "status": "sent"}
    finally:
        db.close()


@celery_app.task(name='send_order_cancelled')
def send_order_cancelled(order_id: int):
    """Send order cancellation email"""
    print(f"Sending cancellation email for order {order_id}")
    return {"order_id": order_id, "status": "sent"}


@celery_app.task(name='send_welcome_email')
def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email to new users"""
    print(f"Welcome email to {user_email} ({user_name})")
    return {"email": user_email, "status": "sent"}