import asyncio
import aiohttp
from sys import stderr

from loguru import logger
from . import config
from telethon.sync import TelegramClient

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

client = TelegramClient(
    session="ads",
    api_id=config.app_id,
    api_hash=config.app_hash,
    system_version="4.16.30-vxCUSTOM",
    device_model=config.device_model,
    system_lang_code="ru",
    connection_retries=-1,
    retry_delay=2,
)


def check_nodes_status(data):
    try:
        return any("address" in item for node in data.values() for item in node)
    except TypeError:
        return True


async def check_port(ip: str, port: int) -> bool:
    """Проверяет открыт ли порт через API check-host.net."""
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=5),
        headers={"Accept": "application/json"},
    ) as session:
        async with session.get(
            f"https://check-host.net/check-tcp?host={ip}:{port}&max_nodes=3",
        ) as response:
            if response.status == 200:
                data = await response.json()
        await asyncio.sleep(5)
        async with session.get(
            f"https://check-host.net/check-result/{data['request_id']}",
        ) as response:
            return check_nodes_status(await response.json())


async def port_checks() -> None:
    while True:
        try:
            if await check_port(config.status_ip, 25565) is False:
                logger.warning("Все ноды ответили о закрытом порту!")
                await client.send_message(
                    entity=config.status_chat,
                    message="❌ : Кажется, сервер упал! @trassert",
                )
                await asyncio.sleep(900)
            else:
                logger.info("Сервер работает стабильно.")
                await asyncio.sleep(1800)
        except Exception as e:
            logger.error(f"Ошибка при проверке порта: {e}")
            await asyncio.sleep(60)


async def main():
    await client.start(bot_token=config.status_bot_token)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
