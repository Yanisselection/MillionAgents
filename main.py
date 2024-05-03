from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import math
import time


options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=chrome_options)

city_list = ['Москва', 'Санкт-Петербург']
def main():
    try:
        # Максимизация окна браузера для перехода в полноэкранный режим
        driver.maximize_window()

        #Цикл для каждого города
        for city in city_list:
            # Открытие страницы
            driver.get("https://online.metro-cc.ru/category/ovoshchi-i-frukty/ovoshchi?from=under_search&page=1")

            if city == city_list[1]:
                print('ok')

            #Нажатие на кнопку с адресом
            time.sleep(1)
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

            parser()

    except Exception as e:
        print(e)


def parser():
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
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        section_element = soup.find('div', id="products-inner")  # Находим элемент <div>
        if section_element:  # Проверяем, что элемент был найден
            article_elements = section_element.find_all('div')  # Находим все элементы <div> внутри найденного <div>

            for article in article_elements:

                print(article.get_text())

                if 'нет в наличии' in str(article):
                    continue
        driver.get(f"https://online.metro-cc.ru/category/ovoshchi-i-frukty/ovoshchi?from=under_search&page={i}")
        time.sleep(2)


if __name__ == "__main__":
    main()
    time.sleep(500)

