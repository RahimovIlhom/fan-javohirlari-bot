import asyncio
import os
from PIL import Image, ImageDraw, ImageFont

from data.config import sciences_dict
from .transliterate import to_latin

FONT_FOLDER = 'data/fonts'
CERTIFICATE_FOLDER = 'data/certificates'
FONT_KAUSHAN_SCRIPT = os.path.join(FONT_FOLDER, 'KaushanScript-Regular.otf')
FONT_MONTSERRAT_BOLD = os.path.join(FONT_FOLDER, 'Montserrat-Bold.otf')
FONT_MONTSERRAT_REGULAR = os.path.join(FONT_FOLDER, 'Montserrat-Regular.otf')
TEXT_COLOR = (39, 64, 121)
VALID_IMAGE_INDEX_RANGE = range(4)
IMAGES = ['cer001', 'cer002', 'cer003', 'cer004']


async def create_certificate(user_id, image_index, fullname, science, language='uzbek'):
    if image_index not in VALID_IMAGE_INDEX_RANGE:
        return ValueError("Invalid image index")

    font1 = ImageFont.truetype(FONT_KAUSHAN_SCRIPT, 180)
    font2 = ImageFont.truetype(FONT_KAUSHAN_SCRIPT, 200)
    font_science = ImageFont.truetype(FONT_MONTSERRAT_BOLD, 68)
    font_id = ImageFont.truetype(FONT_MONTSERRAT_REGULAR, 65)

    img = Image.open(os.path.join(CERTIFICATE_FOLDER, f'{IMAGES[image_index]}.jpg'))

    draw = ImageDraw.Draw(img)
    if language != 'uzbek':
        fullname = to_latin(fullname).title()
    else:
        fullname = fullname.title()

    if image_index != 3:
        if language == 'uzbek':
            science_text = f"“{science.upper()}” FANIDAN"
        else:
            science_text = f"“{sciences_dict[science.upper()]}” FANIDAN"

        text_bbox = draw.textbbox((1750, 1070), fullname, font=font1)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (1750 - text_width / 2, 1030)
        draw.text(text_position, fullname, font=font1, fill=TEXT_COLOR)

        text_bbox = draw.textbbox((1750, 1070), science_text, font=font_science)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (1750 - text_width / 2, 1355)
        draw.text(text_position, science_text, font=font_science, fill=TEXT_COLOR)
    else:
        text_bbox = draw.textbbox((1750, 1070), fullname, font=font2)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (1750 - text_width / 2, 1450)
        draw.text(text_position, fullname, font=font2, fill=TEXT_COLOR)

    draw.text((550, 2300), f"id: {user_id}", fill=(0, 0, 0), font=font_id)

    save_image_name = os.path.join(CERTIFICATE_FOLDER, f"{user_id}.jpg")
    img.save(save_image_name)

    return save_image_name
