from PIL import Image, ImageDraw, ImageFont


async def create_certificate(user_id, image_index, fullname):
    """
    image_index: value distance [0:3]
    """
    images = ['0001', '0002', '0003', '0004']
    img = Image.open(f'data/certificates/{images[image_index]}.jpg')

    draw = ImageDraw.Draw(img)

    font_path = 'data/fonts/KaushanScript-Regular.otf'
    font1 = ImageFont.truetype(font_path, 180)
    font2 = ImageFont.truetype(font_path, 200)
    font_id = ImageFont.truetype("FreeMono.ttf", 65)

    text_color = (39, 64, 121)

    if image_index != 3:
        text_bbox = draw.textbbox((1750, 1070), fullname, font=font1)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (1750 - text_width / 2, 1030)
        draw.text(text_position, fullname, font=font1, fill=text_color)
    else:
        text_bbox = draw.textbbox((1750, 1070), fullname, font=font2)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (1750 - text_width / 2, 1450)
        draw.text(text_position, fullname, font=font2, fill=text_color)

    draw.text((550, 2300), f"id: {user_id}", fill=(0, 0, 0), font=font_id)
    save_image_name = f"data/certificates/{user_id}.jpg"
    img.save(save_image_name)
    return save_image_name
