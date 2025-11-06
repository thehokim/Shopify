from app.celery_app import celery_app


@celery_app.task(name='notify_shop_owner')
def notify_shop_owner(order_id: int):
    """Notify shop owner about new order"""
    from app.database import SessionLocal
    from app.models import Order
    
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            message = f"""
 <b>Новый заказ!</b>

Номер: #{order.order_number}
Сумма: ${order.total}
Товаров: {len(order.items)}

Клиент: {order.customer.full_name}
Email: {order.customer.email}
Телефон: {order.customer.phone or 'Не указан'}
            """
            
            # TODO: Send Telegram message
            print(f"📱 Telegram notification:")
            print(message)
            
            # Example:
            # from app.services.telegram_service import send_message
            # send_message(chat_id=order.tenant.owner.telegram_id, text=message)
            
        return {"order_id": order_id, "status": "sent"}
    finally:
        db.close()


@celery_app.task(name='send_sms')
def send_sms(phone: str, message: str):
    """Send SMS notification"""
    print(f"SMS to {phone}: {message}")
    
    # TODO: Integrate with Eskiz
    # from app.services.sms_service import send_sms
    # send_sms(phone, message)
    
    return {"phone": phone, "status": "sent"}


@celery_app.task(name='send_telegram_message')
def send_telegram_message(chat_id: str, message: str):
    """Send Telegram message"""
    print(f"Telegram to {chat_id}: {message}")
    return {"chat_id": chat_id, "status": "sent"}