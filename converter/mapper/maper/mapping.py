import xml.etree.ElementTree as ET
from .stoplist_encoding import stoplist_encoding


def parse_element(element):
    result = {}

    # Парсинг атрибутов
    result.update(element.attrib)

    # Парсинг текстового содержимого
    if element.text and element.text.strip():
        result["_text"] = element.text.strip()

    # Парсинг дочерних элементов
    for child in element:
        child_data = parse_element(child)
        tag = child.tag

        # Обработка дублирующихся тегов, преобразование их в списки
        if tag in result:
            if type(result[tag]) is list:
                result[tag].append(child_data)
            else:
                result[tag] = [result[tag], child_data]
        else:
            result[tag] = child_data

    return result


# Функция для создания элементов в оффере
def creating_element_in_offer(key, parent_element, element_tag):
    if "_text" in key:
        offer_element_price = ET.SubElement(parent_element, element_tag)
        offer_element_price.text = key["_text"]


def xml_mapping(path_to_xml, stop_list_csv):
    # Массив, который будет заполняться именами совпадающих по именам товаров, если таковые есть
    deleted_goods_names = []
    deleted_company_names = []

    # Переменные, которые будут запрашиваться у пользователя, необязательные
    shop_name = ""
    shop_company = ""
    shop_url = ""

    # Конвенртируем стоп-лист из csv в список
    list_of_stop_vendor = stoplist_encoding(stop_list_csv)

    # Парсинг XML строки
    tree = ET.parse(path_to_xml)  # Введите путь к вашему xml
    root = tree.getroot()
    parsed_dict = parse_element(root)

    try:
        # Создание нового XML-документа, обязательный
        root = ET.Element("yml_catalog", date=parsed_dict["date"])

        # Создание элемента shop, обязательный
        shop_element = ET.SubElement(root, "shop")

        # Добавление информации о магазине, необязательный

        if shop_name:
            shop_name_element = ET.SubElement(shop_element, "name")
            shop_name_element.text = shop_name
        if shop_company:
            shop_compamy_element = ET.SubElement(shop_element, "company")
            shop_compamy_element.text = shop_company
        if shop_url:
            shop_url_element = ET.SubElement(shop_element, "url")
            shop_url_element.text = shop_url

        # Создание элемента currencies, обязательный
        currencies_element = ET.SubElement(shop_element, "currencies")
        currency = parsed_dict["shop"]["currencies"]["currency"]

        if isinstance(currency, list):
            for item in currency:
                currency_element = (
                    ET.SubElement(
                        currencies_element,
                        "currency",
                        id=item["id"] if "id" in item else None,
                        rate=item["rate"] if "rate" in item else None,
                    ),
                )
        else:
            currency_element = ET.SubElement(
                currencies_element,
                "currency",
                id=currency["id"] if "id" in currency else None,
                rate=currency["rate"] if "rate" in currency else None,
            )

        # Создание элемента categories, обязательный
        categories_element = ET.SubElement(shop_element, "categories")
        category = parsed_dict["shop"]["categories"]["category"]

        if isinstance(category, list):
            for item in category:
                if "_text" in item:
                    category_element = ET.SubElement(
                        categories_element,
                        "category",
                        id=item["id"] if "id" in item else None,
                    )
                    category_element.text = item["_text"]
        else:
            if "_text" in category:
                category_element = ET.SubElement(
                    categories_element,
                    "category",
                    id=category["id"] if "id" in category else None,
                )
                category_element.text = category["_text"]

        # Создание элемента offers , обязательный
        offers_element = ET.SubElement(shop_element, "offers")
        offer = parsed_dict["shop"]["offers"]["offer"]

        # Перебор всех элементов предложений
        for item in offer:
            # Проверка на свопадение имен, если в документе есть товары с одинаковыми именами - они удаляются из документа
            name_is_unic = True
            for each in offer:
                if item["id"] == each["id"]:
                    pass
                elif (
                    " ".join(item["name"]["_text"].split()).lower()
                    == " ".join(each["name"]["_text"].split()).lower()
                ):
                    deleted_goods_names.append(item["name"]["_text"])
                    name_is_unic = False

            vendor_allowed = True
            for company in list_of_stop_vendor:
                if (
                    " ".join(item["vendor"]["_text"].split()).lower()
                    == " ".join(company[0].split()).lower()
                ):
                    vendor_allowed = False
                    deleted_company_names.append(item["vendor"]["_text"])

            if isinstance(item, dict) and name_is_unic and vendor_allowed:
                # Создание элемента offer , обязательный
                offer_element = ET.SubElement(
                    offers_element,
                    "offer",
                    id=item["id"] if "id" in item else None,
                    available=item["available"] if "available" in item else None,
                )

                # Создание элемента price , обязательный
                creating_element_in_offer(item["price"], offer_element, "price")

                # Создание элемента currencyId , обязательный
                creating_element_in_offer(
                    item["currencyId"], offer_element, "currencyId"
                )

                # Создание элемента categoryId , обязательный
                creating_element_in_offer(
                    item["categoryId"], offer_element, "categoryId"
                )

                # Создание элементов picture , обязательный
                if isinstance(item["picture"], list):
                    for picture in item["picture"]:
                        if "_text" in picture:
                            offer_element_picture = ET.SubElement(
                                offer_element, "picture"
                            )
                            offer_element_picture.text = picture["_text"]
                else:
                    if "_text" in item["picture"]:
                        offer_element_picture = ET.SubElement(offer_element, "picture")
                        offer_element_picture.text = item["picture"]["_text"]

                # Создание элементов vendore , обязательный
                creating_element_in_offer(item["vendor"], offer_element, "vendor")

                # Создание элемента quantity_in_stock , обязательный
                creating_element_in_offer(
                    item["quantity_in_stock"], offer_element, "stock_quantity"
                )

                # Создание элемента name , обязательный
                creating_element_in_offer(item["name"], offer_element, "name")

                # Создание элемента model , необязательный
                creating_element_in_offer(item["model"], offer_element, "model")

                # Создание элемента desciption , обязательный
                creating_element_in_offer(
                    item["description"], offer_element, "description"
                )

                # Создание элементов param , обязательный
                if isinstance(item["param"], list):
                    for param in item["param"]:
                        if "_text" in param:
                            offer_element_param = ET.SubElement(
                                offer_element,
                                "param",
                                name=param["name"] if "name" in param else None,
                            )
                            offer_element_param.text = param["_text"]
                else:
                    if "_text" in item["param"]:
                        offer_element_param = ET.SubElement(
                            offer_element,
                            "param",
                            name=item[param]["name"] if "name" in item[param] else None,
                        )
                        offer_element_param.text = item["param"]["_text"]

        # Создание XML файла
        tree = ET.ElementTree(root)
        tree.write("media/output.xml", encoding="utf-8", xml_declaration=True)

    except Exception as e:
        print("Неподходящая структура файла")


# Пример вызова функции
# xml_mapping("products.xml", "stop_list.csv")
