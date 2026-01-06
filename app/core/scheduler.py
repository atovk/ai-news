from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.services.news_aggregator import NewsAggregatorService
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def fetch_news_job():
    """
    Scheduled job to fetch news from all sources.
    """
    logger.info("Starting scheduled news fetch...")
    db: Session = SessionLocal()
    try:
        aggregator = NewsAggregatorService(db)
        # We rely on aggregator to check fetch_interval for each source
        result = await aggregator.fetch_all_sources()
        logger.info(f"Scheduled news fetch completed: {result}")
    except Exception as e:
        logger.error(f"Error in scheduled news fetch: {e}")
    finally:
        db.close()

def start_scheduler():
    """Start the scheduler"""
    if not scheduler.running:
        # Run every minute, but the service will check if the source actually needs updating
        scheduler.add_job(
            fetch_news_job,
            trigger=IntervalTrigger(minutes=1),
            id="fetch_news_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduler started")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
