from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import math
import time


options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=chrome_options)

#Ввод стартовой страницы для поиска
start_link = "https://online.metro-cc.ru/category/ovoshchi-i-frukty/ovoshchi"

#Города
city_list = ['Москва', 'Санкт-Петербург']


def main():
    try:
        # Максимизация окна браузера для перехода в полноэкранный режим
        driver.maximize_window()

        df = pd.DataFrame(columns=['ГОРОД', 'ID ПРОДУКТА', 'НАИМЕНОВАНИЕ', 'БРЕНД', 'АКТУАЛЬНАЯ ЦЕНА', 'СТАРАЯ ЦЕНА', 'ССЫЛКА'])

        #Цикл для каждого города
        for city in city_list:
            # Открытие страницы
            driver.get(start_link)
            time.sleep(2)

            #Нажатие на кнопку с адресом
            if city == city_list[0]:
                address_button = driver.find_element(By.XPATH, "//button[@class='header-address__receive-button offline']")
                address_button.click()

                # Переключение на вкладку самовывоза
                delivery_tab = driver.find_element(By.XPATH, "//div[@class='delivery__tab']")
                delivery_tab.click()
            else:
                address_button = driver.find_element(By.XPATH,"//button[@class='header-address__receive-button pickup']")
                address_button.click()

            # Нажатие на ссылку "Изменить"
            edit_link = driver.find_element(By.XPATH, "//span[@class='reset-link active-blue-text']")
            edit_link.click()

            # Очистка и ввод текста в поле ввода города
            city_input = driver.find_element(By.XPATH, "//input[@label='Введите название города']")
            city_input.clear()
            city_input.send_keys(city)

            time.sleep(1)
            # Выбор города из списка
            city_item = driver.find_elements(By.XPATH, "//div[@class='modal-city__center scroll']")
            city_item[0].click()

            # Нажатие на кнопку "Выбрать"
            select_button = driver.find_element(By.XPATH, "//span[@class='simple-button__text'][text()='Выбрать']")
            select_button.click()

            time.sleep(2)
            parser(city, df)

        df.to_csv('data.csv', index=False, encoding='utf-8-sig')

    except Exception as e:
        print(e)


def parser(city, df):

    time.sleep(4)
    # Получение исходного кода страницы
    div_user = driver.page_source

    # Создание объекта BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(div_user, 'html.parser')

    # Нахождение элемента с общим количеством продуктов
    total_products_element = soup.find('span', class_='heading-products-count subcategory-or-type__heading-count').text.split()
    total_products_count = int(total_products_element[0])

    # Расчет количества страниц на основе общего количества продуктов
    pages = math.ceil(total_products_count / 30)

    # Нажатие на элемент для фильтрации по бренду
    brand_element = driver.find_element(By.XPATH, "//div[@class='catalog-filters-block__title'][contains(text(), 'Бренд')]")
    brand_element.click()

    # Извлекаем значения атрибута "data-filter-text" из найденных элементов
    div_elements = soup.find_all('div', class_="v-scrollbox__content")
    all_brands = div_elements[0].text.split('\n')
    substrings = [line.strip().lower() for line in all_brands if line.strip()]
    print(substrings)

    products_page = []
    for i in range(2, pages+1):
        # Получение исходного кода страницы
        div_user = driver.page_source

        # Создание объекта BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(div_user, 'html.parser')

        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        section_element = soup.find('div', id="products-inner").find_all('div', class_="catalog-2-level-product-card")  # Находим элемент <div>
        if section_element:  # Проверяем, что элемент был найден

            for el in section_element:
                try:
                    element_with_text = el.find('div', class_='product-card__content').find('span', class_='simple-button__text')
                    if element_with_text.text == 'Сообщить о поступлении':
                        continue
                except Exception:
                    pass

                title = el.find('a', class_='product-card-name')['title']  # Получаем атрибут 'title' из тега 'a' внутри элемента 'el'
                href_link = el.find('a', class_='product-card-name')['href']
                link_product = f'https://online.metro-cc.ru{href_link}'
                product_id = el['id']  # Получаем значение атрибута 'id' из элемента 'el'
                try:
                    penny = str(el.find('span', class_='product-price__sum').find('span', class_='product-price__sum-penny').text.strip())
                except Exception:
                    penny = '.00'
                price = str(el.find('span', class_='product-price__sum-rubles').text.strip()) + penny + str(el.find('span', class_='product-price__unit').text.strip())  # Получаем текстовое содержимое тега 'span' внутри элемента 'el'
                price_old = 'Отсутствует'
                product_brand = 'Без бренда'
                for brand in substrings:
                    if brand in str(title.lower()):
                        product_brand = brand.capitalize()
                try:
                    price_old = el.find('div', class_='product-unit-prices__old-wrapper').find('span', class_='product-price__sum-rubles').text.strip()
                except Exception:
                    pass
                print(city, product_id, title.capitalize(), product_brand, price, price_old, link_product)

                df.loc[len(df)] = [city, product_id, title, product_brand, price, price_old, link_product]




        driver.get(f"https://online.metro-cc.ru/category/ovoshchi-i-frukty/ovoshchi?from=under_search&page={i}")
        time.sleep(2)


if __name__ == "__main__":
    main()
    print('Парсинг завершен')

