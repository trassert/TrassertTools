import asyncio
import re

from typing import Optional
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from telethon.tl.custom import Message

from vkbottle import Bot
from vkbottle.tools import PhotoWallUploader

import config
from loguru import logger
from sys import stderr

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


class TelegramToVKTranslator:
    def __init__(self):
        self.telegram_client = TelegramClient(
            "tgtovk",
            config.tgtovk_app_id,
            config.tgtovk_app_hash,
        )

        self.vk_bot = Bot(token=config.vk_token)

    async def upload_photo_to_wall(self, file_path: str) -> Optional[str]:
        return await PhotoWallUploader(self.vk_bot.api).upload(file_path)

    def format_message(self, text) -> str:
        try:
            text = text.replace("**", "")
            text = text.replace("__", "")
            text = re.sub(r"\[.*?\]\(.*?\)", "", text)
            text = (
                f"📢 Из Telegram - t.me/{config.telegram_ch}\n\n{text.strip()}"
            )
            return text[:4096]
        except Exception:
            return f"📢 Из Telegram - t.me/{config.telegram_ch}"

    async def process_telegram_message(self, message: Message):
        """Обработка сообщения из Telegram и публикация на стене VK"""
        try:
            attachments = []

            if message.media:
                file_path = await message.download_media(file=bytes)
                if isinstance(message.media, MessageMediaPhoto):
                    photo_attachment = await self.upload_photo_to_wall(
                        file_path
                    )
                    logger.info(f"Загружен {photo_attachment}")
                    attachments.append(photo_attachment)
            response = await self.vk_bot.api.wall.post(
                owner_id=config.vk_group_id,
                message=self.format_message(message.text),
                attachments=attachments,
            )
            logger.info(f"Отправлен пост. ID: {response.post_id}")
        except Exception as e:
            logger.info(f"Ошибка обработки сообщения: {e}")

    async def start(self):
        """Запуск транслятора"""

        await self.telegram_client.start()
        logger.info("Telegram клиент запущен")

        self.telegram_client.add_event_handler(
            self.process_telegram_message,
            events.NewMessage(chats=config.telegram_ch),
        )
        logger.info(
            f"Транслятор запущен. Отслеживаем канал: {config.telegram_ch}"
        )
        logger.info(f"Публикуем в группу VK с ID: {config.vk_group_id}")
        await self.telegram_client.run_until_disconnected()


async def main():
    translator = TelegramToVKTranslator()
    await translator.start()


if __name__ == "__main__":
    asyncio.run(main())
