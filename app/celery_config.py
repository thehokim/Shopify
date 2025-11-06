from celery.schedules import crontab
from kombu import Queue, Exchange
import os


class CeleryConfig:
    """Celery configuration class"""
    
    broker_url = os.getenv(
        'RABBITMQ_URL', 
        'amqp://admin:admin@rabbitmq:5672'
    )
    
    result_backend = os.getenv(
        'REDIS_URL',
        'redis://redis:6379/0'
    )
    
    broker_connection_retry_on_startup = True
    

    broker_connection_retry = True
    broker_connection_max_retries = 10
    
    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    
    timezone = 'Asia/Tashkent'
    enable_utc = True
    
    task_track_started = True
    task_acks_late = True 
    task_reject_on_worker_lost = True
    
    task_soft_time_limit = 300    
    task_time_limit = 600           
    
    result_expires = 3600
    
    task_compression = 'gzip'
    result_compression = 'gzip'
    

    worker_prefetch_multiplier = 4
    
    worker_max_tasks_per_child = 1000
    
    worker_concurrency = 4  
    
    worker_pool = 'prefork'  
    
    worker_disable_rate_limits = False
    
    task_queues = (
        Queue(
            'default',
            Exchange('default'),
            routing_key='default',
            queue_arguments={'x-max-priority': 10}
        ),
        
        Queue(
            'high_priority',
            Exchange('high_priority'),
            routing_key='high_priority',
            queue_arguments={'x-max-priority': 10}
        ),
        
        Queue(
            'low_priority',
            Exchange('low_priority'),
            routing_key='low_priority',
            queue_arguments={'x-max-priority': 10}
        ),
        
        Queue(
            'email',
            Exchange('email'),
            routing_key='email',
        ),
        
        Queue(
            'notifications',
            Exchange('notifications'),
            routing_key='notifications',
        ),
    )
    
    task_default_queue = 'default'
    task_default_exchange = 'default'
    task_default_routing_key = 'default'
    
    task_routes = {
        'send_order_confirmation': {
            'queue': 'email',
            'routing_key': 'email',
            'priority': 9
        },
        'send_welcome_email': {
            'queue': 'email',
            'routing_key': 'email',
            'priority': 7
        },
        'send_order_cancelled': {
            'queue': 'email',
            'routing_key': 'email',
            'priority': 8
        },
        
        'notify_shop_owner': {
            'queue': 'notifications',
            'routing_key': 'notifications',
            'priority': 9
        },
        'send_sms': {
            'queue': 'notifications',
            'routing_key': 'notifications',
            'priority': 8
        },
        'send_telegram_message': {
            'queue': 'notifications',
            'routing_key': 'notifications',
            'priority': 8
        },
        
        'process_new_order': {
            'queue': 'high_priority',
            'routing_key': 'high_priority',
            'priority': 10
        },
        
        'cancel_unpaid_orders': {
            'queue': 'low_priority',
            'routing_key': 'low_priority',
            'priority': 3
        },
        'cleanup_old_carts': {
            'queue': 'low_priority',
            'routing_key': 'low_priority',
            'priority': 2
        },
        'generate_sales_report': {
            'queue': 'low_priority',
            'routing_key': 'low_priority',
            'priority': 4
        },
    }
    

    task_autoretry_for = (Exception,)
    task_retry_backoff = True
    task_retry_backoff_max = 600  
    task_retry_jitter = True
    task_max_retries = 3
    
    worker_send_task_events = True
    task_send_sent_event = True
    
    event_queue_expires = 60
    event_queue_ttl = 5
    
    worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
    worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
    
    
    beat_schedule = {
        'cancel-unpaid-orders-hourly': {
            'task': 'cancel_unpaid_orders',
            'schedule': crontab(minute=0),  
            'options': {'queue': 'low_priority'}
        },
        
        'cleanup-carts-daily': {
            'task': 'cleanup_old_carts',
            'schedule': crontab(hour=3, minute=0),
            'options': {'queue': 'low_priority'}
        },
        
        'update-product-stats': {
            'task': 'update_product_statistics',
            'schedule': crontab(minute='*/30'),
            'options': {'queue': 'default'}
        },
        
        'daily-sales-report': {
            'task': 'generate_daily_sales_report',
            'schedule': crontab(hour=9, minute=0),
            'options': {'queue': 'low_priority'}
        },
        
        'weekly-analytics-report': {
            'task': 'generate_weekly_analytics',
            'schedule': crontab(hour=10, minute=0, day_of_week=1),
            'options': {'queue': 'low_priority'}
        },
        
        'monthly-report': {
            'task': 'generate_monthly_report',
            'schedule': crontab(hour=9, minute=0, day_of_month=1),
            'options': {'queue': 'low_priority'}
        },
        
        'backup-database': {
            'task': 'backup_database',
            'schedule': crontab(hour=2, minute=0),
            'options': {'queue': 'low_priority'}
        },
        
        'reindex-elasticsearch': {
            'task': 'reindex_elasticsearch',
            'schedule': crontab(minute=0, hour='*/6'),
            'options': {'queue': 'default'}
        },
        
        'health-check': {
            'task': 'system_health_check',
            'schedule': crontab(minute='*/5'),
            'options': {'queue': 'default'}
        },
    }
    
    beat_scheduler = 'celery.beat:PersistentScheduler'
    
    task_always_eager = False  
    task_eager_propagates = True
    
    result_accept_content = ['json']
    
    redis_max_connections = 50
    redis_socket_timeout = 5
    redis_socket_connect_timeout = 5
    
    redis_retry_on_timeout = True
    redis_socket_keepalive = True
    
    
    worker_pool_restarts = True
    
    worker_max_memory_per_child = 200000  # 200MB in KB
    
    worker_prefetch_multiplier = 4
    
    task_acks_late = True
    
    task_ignore_result = False
    
    task_store_errors_even_if_ignored = True



task_annotations = {
    'send_order_confirmation': {
        'rate_limit': '100/m',  # 100 emails per minute
        'time_limit': 30,
        'soft_time_limit': 20,
    },
    'send_sms': {
        'rate_limit': '50/m',  # 50 SMS per minute
        'time_limit': 30,
    },
    'generate_sales_report': {
        'rate_limit': '10/h',  # 10 reports per hour
        'time_limit': 600,  # 10 minutes
    },
    'backup_database': {
        'rate_limit': '1/h',
        'time_limit': 3600,  # 1 hour
    },
}



class DevelopmentConfig(CeleryConfig):
    """Development configuration"""
    task_always_eager = True  # Execute tasks synchronously
    task_eager_propagates = True
    worker_concurrency = 2


class ProductionConfig(CeleryConfig):
    """Production configuration"""
    task_always_eager = False
    worker_concurrency = 8
    worker_max_tasks_per_child = 1000
    
    task_compression = 'gzip'
    result_compression = 'gzip'
    
    task_max_retries = 5
    task_retry_backoff_max = 3600  

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig


Config = get_config()