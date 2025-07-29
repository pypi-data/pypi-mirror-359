import asyncio
from asyncio import Lock
import logging

import requests
from aiohttp import ClientSession
from . import storage


task_lock = Lock()
logger = logging.getLogger(__name__)


async def publish_message_async(session: ClientSession, webhook_url: str, text: str):
    async with task_lock:
        data = {"content": f"```ansi\n{text[:1900]}```"}
        async with session.post(webhook_url, data=data) as response:
            if not response.ok:
                try:
                    response.raise_for_status()
                except Exception:
                    logger.exception("Error posting to webhook: %s", await response.text())

                if response.status == 429:
                    retry = int(response.headers.get(
                        "X-RateLimit-Reset-After", 0))
                    await asyncio.sleep(retry)
                    await publish_message_async(session, webhook_url, text)


def publish_message_sync(webhook_url: str, text: str):
    data = {"content": f"```ansi\n{text[:1900]}```"}
    response = requests.post(webhook_url, json=data)
    if not response.ok:
        try:
            response.raise_for_status()
        except Exception:
            logger.exception("Error posting to webhook: %s", response.text)


def publish_message(text: str):
    webhook_url = storage.webhook_url
    session = storage.session
    if webhook_url is None:
        return

    if session is not None:
        session.loop.create_task(
            publish_message_async(session, webhook_url, text))
    else:
        publish_message_sync(webhook_url, text)
