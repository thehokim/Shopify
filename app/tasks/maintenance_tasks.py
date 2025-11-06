from app.celery_app import celery_app
from datetime import datetime, timedelta


@celery_app.task(name='cleanup_old_carts')
def cleanup_old_carts():
    """Remove abandoned carts older than 7 days"""
    from app.database import SessionLocal
    from app.models import CartItem
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted = db.query(CartItem).filter(
            CartItem.updated_at < cutoff_date
        ).delete()
        db.commit()
        
        print(f"Cleaned up {deleted} old cart items")
        return {"deleted_carts": deleted}
    finally:
        db.close()


@celery_app.task(name='update_product_statistics')
def update_product_statistics():
    """Update product view counts and sales stats"""
    print("Updating product statistics...")
    return {"status": "updated"}


@celery_app.task(name='backup_database')
def backup_database():
    """Create database backup"""
    import subprocess
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'/backups/db_backup_{timestamp}.sql.gz'
    
    # TODO: Implement actual backup
    print(f"Creating database backup: {backup_file}")
    
    return {"backup_file": backup_file, "status": "completed"}


@celery_app.task(name='reindex_elasticsearch')
def reindex_elasticsearch():
    """Reindex products in Elasticsearch"""
    from app.services.elasticsearch_service import es_service
    
    print("Reindexing Elasticsearch...")
    # TODO: Implement reindexing
    
    return {"status": "reindexed"}


@celery_app.task(name='system_health_check')
def system_health_check():
    """Check system health"""
    from app.database import SessionLocal
    import redis
    
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "database": False,
        "redis": False,
        "elasticsearch": False,
    }
    
    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        health_status["database"] = True
        db.close()
    except Exception as e:
        print(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        import os
        r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))
        r.ping()
        health_status["redis"] = True
    except Exception as e:
        print(f"Redis health check failed: {e}")
    
    if all(health_status.values()):
        print("All systems healthy")
    else:
        print(f"Health check issues: {health_status}")
    
    return health_status


@celery_app.task(name='generate_daily_sales_report')
def generate_daily_sales_report():
    print("Generating daily sales report...")
    return {"status": "generated"}


@celery_app.task(name='generate_weekly_analytics')
def generate_weekly_analytics():
    print("Generating weekly analytics...")
    return {"status": "generated"}


@celery_app.task(name='generate_monthly_report')
def generate_monthly_report():
    print("Generating monthly report...")
    return {"status": "generated"}