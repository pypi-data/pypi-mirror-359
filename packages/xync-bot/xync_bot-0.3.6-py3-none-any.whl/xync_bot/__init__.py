import logging
from asyncio import run

from PGram import Bot
from aiogram.client.default import DefaultBotProperties
from x_model import init_db

from xync_bot.routers.cond import r

if __name__ == '__main__':
    from xync_bot.loader import dp, TOKEN, TORM

    logging.basicConfig(level=logging.INFO)

    async def main() -> None:
        cn = await init_db(TORM)
        bot = Bot(TOKEN, [r], cn, default=DefaultBotProperties(parse_mode='HTML'))
        await bot.start()

    run(main())
