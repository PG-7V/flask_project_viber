import csv

def search_info(art):
    with open('for_pdf.csv', encoding='utf-8') as f:
        fieldnames = ['Tilda UID', 'Brand', 'SKU', 'Mark', 'Category', 'Title', 'Description', 'Text', 'Photo',
                      'Price', 'Quantity', 'Price Old', 'Editions', 'Modifications', 'External ID', 'Parent UID',
                      'Characteristics:Состав', 'Weight', 'Length', 'Width', 'Height']
        reader = csv.DictReader(f, delimiter=";", fieldnames=fieldnames)
        index = 0
        descr = ''
        art_if = ''
        link = ''
        price = 0
        char = ''
        for row in reader:
            if row['Title'] and row['Description']:
                if art in row['Title']:
                    descr = row['Description'].strip()
                    char = row['Characteristics:Состав'].strip()
                    index = 1
                    continue
            elif index:
                if art in row['SKU'].strip():
                    if 'Артикул' in row['Title']:
                        art_if = 'Артикул ' + row['SKU'].strip()
                        price = row['Price'].strip()
                        link = row['Photo'].strip()
                        break
                    elif row['SKU'].strip().split(' ')[1] == art:
                        art_if = row['SKU'].strip()
                        price = row['Price'].strip()
                        link = row['Photo'].strip()
                        break



        data = {'art_if': art_if,
                'descr': descr,
                'price': price,
                'link': link,
                'char': char,
                }

    return data

# art = input(str('введите артикул: '))
# print(search_info(art))
