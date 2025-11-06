from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Order, OrderStatus
from datetime import datetime, timedelta


@celery_app.task(name='process_new_order')
def process_new_order(order_id: int):
    """Process newly created order"""
    print(f"Processing order {order_id}")
    
    # Send confirmation email
    from app.tasks.email_tasks import send_order_confirmation
    from app.tasks.notification_tasks import notify_shop_owner
    
    send_order_confirmation.delay(order_id)
    notify_shop_owner.delay(order_id)
    
    return {"order_id": order_id, "status": "processed"}


@celery_app.task(name='cancel_unpaid_orders')
def cancel_unpaid_orders():
    """Cancel unpaid orders older than 24 hours"""
    db = SessionLocal()
    try:
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        orders = db.query(Order).filter(
            Order.status == OrderStatus.PENDING,
            Order.payment_status == "pending",
            Order.created_at < cutoff_time
        ).all()
        
        cancelled_count = 0
        for order in orders:
            order.status = OrderStatus.CANCELLED
            cancelled_count += 1
            
            # Send cancellation email
            from app.tasks.email_tasks import send_order_cancelled
            send_order_cancelled.delay(order.id)
        
        db.commit()
        print(f"Cancelled {cancelled_count} unpaid orders")
        return {"cancelled_orders": cancelled_count}
    finally:
        db.close()
