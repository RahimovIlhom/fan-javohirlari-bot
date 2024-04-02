import aiohttp


# async def photo_link(photo: str) -> str:
#     from loader import bot
#     with open(photo, 'rb') as file:
#         form = aiohttp.FormData()
#         form.add_field(
#             name='file',
#             value=file,
#         )
#         async with await bot.get_session() as session:
#             async with session.post('https://telegra.ph/upload', data=form) as response:
#                 img_src = await response.json()
#
#     link = 'http://telegra.ph/' + img_src[0]["src"]
#     return link


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

    link = 'http://telegra.ph/' + img_src[0]["src"]
    return link
