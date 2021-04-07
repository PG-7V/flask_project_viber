import requests
import json

url = 'https://store.tildacdn.com/api/getproductslist/?storepartuid=133030198409&recid=132953886&getparts=true&getoptions=true&size=500'

def write_json(data):
    with open('catalog1.json', 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


write_json(requests.get(url).json())
def main():



    # data = requests.get(url).json() # Работа напрямую с запросом

    count = 0
    list_data_json = []

    # write_json(r.json())
    data = json.load(open('cat.json'))
    for product in data['products']:
        count += 1
        print(f'{count}+++++++')
        title = ''
        text = ''
        quantity = ''
        price = 0
        descr_resize = 1
        descr = ''
        mark = ''
        brand = ''
        # items = [{'title': ''}, {'text': ''}, {'quantity': ''}, {'price': ''},
        #          {'descr': ''}, {'mark': ''}, {'brand': ''}]

        try:
            title = product['title']
        except:
            title = ''

        try:
            text = product['text']
        except:
            text = ''

        try:
            quantity = int(product['quantity'])
        except:
            quantity = ''

        try:
            price = int(float(product['price']))
        except:
            price = 0

        try:
            descr = product['descr']
            descr1 = descr.split(" ")
            descr2 = descr1[1].split("-")
            descr = f"{descr1[0]} {int(descr2[0]) + int(descr_resize)}-{int(descr2[1]) + int(descr_resize)}"
            # descr = product['descr'].split(' ').split
        except:
            descr = ''

        try:
            mark = product['mark']
        except:
            mark = ''

        try:
            brand = product['brand']
        except:
            brand = ''

        photos = []
        try:
            # links = json.loads(product['gallery'])
            # for link in links:
            #     photos.append(link['img'])
            links = json.loads(product['gallery'])
            profile = 0
            tk_ph = ''
            for link in links:
                if not profile:
                    print('Функция нанесения информации на главную')
                if len(links) > 2:
                    if profile == 1:
                        tk_ph = links.pop(-1)
                        # print(tk_ph)
                    # print(len(links))
                    # print('Печатать дополнительные фото')
                    photos.append(link['img'])
                profile += 1
            if tk_ph:
                print(tk_ph)

        except:
            print('error')

        finally:

            data = {'title': title,
                    'text': text,
                    'quantity': quantity,
                    'price': price,
                    'descr': descr,
                    'mark': mark,
                    'brand': brand,
                    'photos': photos,
                    }
            # return data
            print(data)



# if __name__ == '__main__':
#     main()