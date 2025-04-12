import os
import asyncio

from typing import AsyncGenerator, Dict, Any

from pyrogram import Client
from pyrogram.types import ChatMember
from pyrogram.enums import ChatMemberStatus

from src.database import Database

from config import API_HASH, API_ID, GIFT_IDS

MAX_GIFTS = 20


async def get_client():
    session = [file for file in os.listdir('session') if file.split('.')[-1] == 'session']

    if not session:
        session = ['main']

    client = Client(
        name=f'session/{session[0].replace(".session", "")}',
        api_id=API_ID,
        api_hash=API_HASH,
        system_version="4.16.30-vxCUSTOM"
    )
    await client.start()
    return client


async def parse_members(client: Client, admin_id: int, chat: str) -> AsyncGenerator[
    tuple[list[Dict[str, Any]], int, str], None]:
    try:
        async for user in client.get_chat_members(chat):
            if not Database.get_user_is_parser(admin_id):
                return

            user: ChatMember
            if user.status == ChatMemberStatus.MEMBER:
                gifts, user_id, username = await get_user_gifts(client, admin_id, user.user.id, user.user.username)

                if gifts:
                    yield gifts, user_id, username

    except Exception as e:
        print(e)


async def get_user_gifts(client: Client, admin_id: int, user_id: int, username: str, result: list | None = None,
                         level: int = 1):
    if result is None:
        result = []

    if not Database.get_user_is_parser(admin_id):
        return

    user_mode = Database.get_user_mode(admin_id)
    user_level = Database.get_user_level(admin_id)

    if user_mode == 2 and level > user_level:
        return result, user_id, username

    try:
        async for gift in client.get_user_gifts(user_id):
            if gift.is_limited and gift.is_upgraded is None and gift.id in GIFT_IDS:
                result.append({
                    "gift": gift.id,
                    "user_id": user_id,
                    "username": username,
                    "name": GIFT_IDS[gift.id],
                    "level": level
                })

                if len(result) >= MAX_GIFTS:
                    break  # остановим цикл, не собираем больше

            if user_mode == 2 and gift.from_user and len(result) < MAX_GIFTS:
                await get_user_gifts(
                    client,
                    admin_id,
                    gift.from_user.id,
                    gift.from_user.username,
                    result,
                    level + 1
                )

    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return [], user_id, username

    return result, user_id, username


async def main():
    client = await get_client()
    print(client)


if __name__ == '__main__':
    asyncio.run(main())
