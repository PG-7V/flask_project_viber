from PIL import Image, ImageDraw, ImageFont
import json
import os
import requests
import shutil


def create_bool(a, b, string):
    if a in string:
        string = True
    elif b in string:
        string = False
    return string


def get_file(url):
    r = requests.get(url, stream=True)
    return r


def save_image(name, file_object):
    with open(name, 'wb') as fo:
        for chunk in file_object.iter_content(8192):
            fo.write(chunk)


def main(data):
    collection = ""
    proc = data['proc']
    name_output_catalog = 'catalog111'
    if_quantity = create_bool("Только в наличии", 'Все', data['quantity'])
    if_create_brand = create_bool("Да", "Нет", data['if_create_brand'])
    if_material = create_bool('Да', 'Нет', data['if_material'])
    if_add_photos = create_bool('Да', 'Нет', data['if_add_photos'])
    if data['season'] == 'Все платья':
        if_collection = False
    else:
        if_collection = True
    if if_collection:
        collection = data['season']
    if_characteristics = create_bool('Да', 'Нет', data['if_characteristics'])
    if_descr = if_descr_resize = True
    descr_resize = data['descr_resize']
    if_price_resize = data['if_price_resize']
    price_resize = data['price_resize']
    if_price = create_bool('Да', 'Нет', data['view_price'])
    if 'Нет' in data['valute']:
        valute = ''
    else:
        valute = data['valute']

    if_create_logo = create_bool('Да', 'Нет', data['if_create_logo'])

    list_png = []
    path_o = data['filename']
    font_path = path_o + '/' + 'Roboto-Light.ttf'
    file_csv = path_o + '/' + 'for_pdf.csv'
    try:
        shutil.rmtree(os.path.abspath('folder'))
    except:
        pass
    if not os.path.exists('folder'):
        os.makedirs('folder')
    path = os.path.abspath('folder')
    path_folder = path

    category = 0
    count = 0
    character = ''
    descr_count = 0
    count = 0
    list_data_json = []

    # write_json(r.json())
    # data_j = json.load(open('catalog1.json'))
    url_j = 'https://store.tildacdn.com/api/getproductslist/?storepartuid=133030198409&recid=132953886&getparts=true&getoptions=true&size=500'
    data_j = requests.get(url_j).json()
    for product in data_j['products']:
        count += 1
        title = ''
        comment_text = ''
        character = ''
        quantity = ''
        price = ''
        descr = ''
        sale = ''
        brand = ''
        tk_ph = ''

        try:
            title = product['title']
        except:
            title = ''
        try:
            comment_text = product['text']
        except:
            comment_text = ''
        try:
            quantity = int(product['quantity'])
        except:
            quantity = ''
        # try:
        #     price = float(round((float(product['price'])), 2))
        # except:
        #     price = ''
        try:
            descr = product['descr']
        except:
            descr = ''
        try:
            sale = product['mark']
        except:
            sale = ''
        try:
            brand = product['brand']
        except:
            brand = ''
        try:
            links = json.loads(product['gallery'])
        except:
            print('Error parse "gallery"')
            continue
        try:
            character = product['characteristics'][0]['value']
        except:
            character = ''
        profile = 0
        tk_ph = ''
        if len(links) > 1:
            tk_ph = links.pop(-1)['img']
        for link in links:
            if profile == 0:  # Основное фото
                count += 1
                profile +=1
                save_image(path + '/' + str(count) + '.jpg', get_file(link['img']))
                im = Image.open(path + '/' + str(count) + '.jpg')
                im = im.resize((900, 1200))
                draw_text = ImageDraw.Draw(im)
                font = ImageFont.truetype(font_path, size=18)

                if sale and if_create_logo:
                    if 'Sale' in sale:
                        draw_text.ellipse((40, 80, 90, 130), fill="red", outline="red")
                        draw_text.text((50, 93), 'sale', font=font, fill='white')

                    elif 'New' in sale:
                        draw_text.ellipse((40, 80, 90, 130), fill="green", outline="green")
                        draw_text.text((50, 93), 'new', font=font, fill='white')

                if if_create_brand and brand:
                    draw_text.text((30, 30), f'Бренд: {brand}',
                                   font=ImageFont.truetype(font_path, size=28), fill='black')

                if comment_text:
                    iter = len(comment_text) // 24
                    if iter > 0:
                        comment_text = list(comment_text)
                        for i in range(1, iter + 1):
                            comment_text.insert((i * 24) + i, '\n')
                        comment_text = ''.join(comment_text)
                    draw_text.text((550, 1050), f'{comment_text}',
                                   font=ImageFont.truetype(font_path, size=24), fill='black')

                font = ImageFont.truetype(font_path, size=28)
                if quantity:
                    draw_text.text(
                        (670, 30),
                        'В наличии',
                        font=font,
                        fill='#2a9926')
                    # quantity = 0
                else:
                    draw_text.text(
                        (670, 30),
                        'Под заказ',
                        font=font,
                        fill='red')

                draw_text.text(
                    (670, 65),
                    (title),
                    font=font,
                    fill='#1C0606')
                if if_descr:
                    if if_descr_resize:
                        if not descr_count:
                            descr1 = descr.split(" ")
                            descr2 = descr1[1].split("-")
                            descr = f"{descr1[0]} {int(descr2[0]) + int(descr_resize)}-{int(descr2[1]) + int(descr_resize)}"
                            descr_count = 1
                        elif descr_count:
                            descr = descr
                    draw_text.text(
                        (670, 100),
                        (descr.replace('Размеры', 'Размеры:')),
                        font=font,
                        fill='#1C0606')
                    if product['price']:
                        price = float(round((float(product['price'])), 2))
                        if if_price:
                            if valute:
                                price = str(round((price + if_price_resize) * price_resize)) + " " + valute
                            elif not valute:
                                price = str(round((price + if_price_resize) * price_resize))
                            draw_text.text(
                                (670, 135),
                                (f'Цена: {price}'),
                                font=font,
                                fill='#1C0606')
                elif product['price']:
                    price = float(round((float(product['price'])), 2))
                    if if_price:
                        if valute:
                            price = str(round((price + if_price_resize) * price_resize)) + " " + valute
                        elif not valute:
                            price = str(round((price + if_price_resize) * price_resize))
                        draw_text.text(
                            (670, 135),
                            (f'Цена: {price}'),
                            font=font,
                            fill='#1C0606')

                if if_characteristics and character:
                    if ';' in character.strip():
                        character = character.strip().replace('; ', '\n')
                    elif ',' in character.strip():
                        character = character.strip().replace(', ', '\n')
                    draw_text.text(
                        (670, 905),
                        'Состав:',
                        font=font,
                        fill='#2a9926')
                    draw_text.text(
                        (670, 940),
                        (character),
                        font=font,
                        fill='#1C0606')
                im.save(path + '/' + str(count) + 'a1.jpg', quality=100)
                if if_collection:
                    if category:
                        if if_quantity:
                            if quantity:
                                list_png.append(path + '/' + str(count) + 'a1.jpg')
                        else:
                            list_png.append(path + '/' + str(count) + 'a1.jpg')
                else:
                    if if_quantity:
                        if quantity:
                            list_png.append(path + '/' + str(count) + 'a1.jpg')
                    else:
                        list_png.append(path + '/' + str(count) + 'a1.jpg')
                # profile += 1
                # continue
                # print('end func')
            elif profile > 0:
                count += 1
                save_image(path + '/' + str(count) + '.jpg', get_file(link['img']))
                im = Image.open(path + '/' + str(count) + '.jpg')
                im = im.resize((900, 1200))
                im.save(path + '/' + str(count) + 'a1.jpg', quality=100)
                if if_add_photos:
                    if if_collection:
                        if category:
                            if if_quantity:
                                if quantity:
                                    list_png.append(path + '/' + str(count) + 'a1.jpg')
                            else:
                                list_png.append(path + '/' + str(count) + 'a1.jpg')
                    else:
                        if if_quantity:
                            if quantity:
                                list_png.append(path + '/' + str(count) + 'a1.jpg')
                        else:
                            list_png.append(path + '/' + str(count) + 'a1.jpg')

        if if_material:  # Ткань
            count += 1
            if tk_ph:
                save_image(path + '/' + str(count) + '.jpg', get_file(tk_ph))
                im = Image.open(path + '/' + str(count) + '.jpg')
                im = im.resize((900, 1200))
                im.save(path + '/' + str(count) + 'a1.jpg', quality=100)
                if if_material:
                    if if_collection:
                        if category:
                            if if_quantity:
                                if quantity:
                                    list_png.append(path + '/' + str(count) + 'a1.jpg')
                            else:
                                list_png.append(path + '/' + str(count) + 'a1.jpg')
                    else:
                        if if_quantity:
                            if quantity:
                                list_png.append(path + '/' + str(count) + 'a1.jpg')

                        else:
                            list_png.append(path + '/' + str(count) + 'a1.jpg')

    pdf1_filename = path_o + '/' + f"{name_output_catalog}.pdf"
    im_list_obj = []
    for i in list_png:
        im_list_obj.append(Image.open(i))
    imk = im_list_obj.pop(0)
    imk.save(pdf1_filename, "PDF", quality=proc, save_all=True, append_images=im_list_obj)
    path_folder = os.path.join(path_folder)
    shutil.rmtree(path_folder)


if __name__ == '__main__':
    main()

