"""Exploit timeseries DS in Redis to cache trade data"""

import redis.asyncio as redis

from trade_price_etl.settings.base_settings import settings


r = redis.Redis(
    host=settings.REDIS.HOST,
    port=settings.REDIS.PORT,
    db=settings.REDIS.DB
)

REDIS_TS = r.ts()


async def async_write_price(price_name: str, price: float):
    async with REDIS_TS.pipeline(transaction=True) as pipe:
        await pipe.add(
                price_name, "*", price, 
                retension_msecs=settings.REDIS.RETENTION_TIME,
                duplicate_policy="LAST"
            ).execute()
    