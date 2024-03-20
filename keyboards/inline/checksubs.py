from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def make_check_channels_subs(channels: list, lang: str):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        invite_link = await channel.export_invite_link()
        button = InlineKeyboardButton(text=channel.title, url=invite_link)
        markup.insert(button)
    if lang == 'uzbek':
        check_btn = InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_subs")
    else:
        check_btn = InlineKeyboardButton(text="✅ Подписался", callback_data="check_subs")
    markup.insert(check_btn)
    return markup
