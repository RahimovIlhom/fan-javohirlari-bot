import logging
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InputFile

from data.config import CHANNELS
from keyboards.inline.checksubs import make_check_channels_subs
from states import PINFLStateGroup
from utils.misc import subscription
from loader import bot, db


class BigBrother(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        if update.message:
            if update.message.text in ['ПРОЙТИ ТЕСТ', 'TEST TOPSHIRISH']:
                user = update.message.from_user.id
            elif update.message.text in ['/start', '/help', '/re_register']:
                user = update.message.from_user.id
                if await db.select_user(user) is None:
                    return
            else:
                return
        elif update.callback_query:
            if update.callback_query.data == "start_test":
                user = update.callback_query.from_user.id
            else:
                return
        else:
            return
        user_db = await db.select_user(user)
        if user_db:
            if user_db[2] == 'uzbek':
                result = "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n"
            else:
                result = "⚠️ Подпишитесь на следующие каналы для использования бота:\n"
        else:
            await update.message.answer("Siz hali ro'yxatdan o'tmagansiz.\n"
                                        "Ro'yxatdan o'tish uchun - /start\n\n"
                                        "Вы еще не зарегистрировались.\nДля регистрации - /start")
            return
        final_status = True
        channels = []
        for channel in CHANNELS:
            status = await subscription.check(user_id=user,
                                              channel=channel)
            final_status *= status
            channel = await bot.get_chat(channel)
            if not status:
                channels.append(channel)

        if not final_status:
            if update.callback_query:
                await update.callback_query.message.answer(result,
                                                           reply_markup=await make_check_channels_subs(channels, lang=user_db[2]),
                                                           disable_web_page_preview=True)
            else:
                await update.message.answer(result, reply_markup=await make_check_channels_subs(channels, lang=user_db[2]),
                                            disable_web_page_preview=True)
            raise CancelHandler()
