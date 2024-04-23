import aiohttp


async def photo_link(photo: str) -> str:
    from loader import bot
    with open(photo, 'rb') as file:
        form = aiohttp.FormData()
        form.add_field(
            name='file',
            value=file,
        )
        session = await bot.get_session()
        async with session.post('https://telegra.ph/upload', data=form) as response:
            img_src = await response.json()
            if 'error' in img_src:
                error_message = img_src['error']
                print("Xato:", error_message)
                return ""  # Yoki siz bu erorning o'zgartirilgan versiyasini chiqaring
            else:
                link = 'http://telegra.ph/' + img_src[0]["src"]
                return link

