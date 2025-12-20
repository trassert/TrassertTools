import asyncio

from telethon.sync import TelegramClient
from loguru import logger
from sys import stderr
import config

logger.remove()
logger.add(
    stderr,
    format="[{time:HH:mm:ss} <level>{level}</level>]:"
    " <green>{file}:{function}</green>"
    " <cyan>></cyan> {message}",
    level="INFO",
    colorize=True,
    backtrace=False,
    diagnose=False,
)
logger.info("Start logging")

client = TelegramClient(
    session="ads",
    api_id=config.ads_app_id,
    api_hash=config.ads_app_hash,
    system_version="4.16.30-vxCUSTOM",
    device_model=config.device_model,
    system_lang_code="ru",
    connection_retries=-1,
    retry_delay=2,
)


async def ads():
    while True:
        for id in config.ads_chat:
            try:
                await client.forward_messages(
                    id,
                    config.ad_id,
                    config.ad_chat,
                )
                logger.info(f"Реклама отправлена, чат {id}")
                await asyncio.sleep(config.ad_sleep)
            except Exception:
                logger.error("Не получилось отправить рекламу")


async def main():
    await client.start()
    await ads()


if __name__ == "__main__":
    asyncio.run(main())
