import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils import clean_text, get_value_from_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
URL = "https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html"


def get_data(url: str) -> BeautifulSoup | None:
    logger.info(f"Get data from: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    if driver.page_source:
        soup = BeautifulSoup(driver.page_source, "html.parser")
    else:
        logger.error(f"Page not found: {url}")
        return

    driver.quit()
    return soup


def collect_items(soup: BeautifulSoup) -> dict:
    menu_info = {}
    products = soup.find_all(class_="cmp-category__item")
    for item in products:
        product_id = item.get("data-product-id")
        product_url = f"https://www.mcdonalds.com/ua/uk-ua/product/{product_id}.html"
        product_page = get_data(product_url)
        if product_page is None:
            logger.error(f"Page not found: {product_url}")
        menu_info[product_id] = get_product_info(product_page)

    return menu_info


def get_product_info(product: BeautifulSoup) -> dict | None:
    name = description = calories = fats = carbs = proteins = unsaturated_fats = sugar = salt = portion = None

    if product.find(class_="cmp-product-details-main__heading-title"):
        name = product.find(class_="cmp-product-details-main__heading-title").text
    else:
        logger.info(f"Product name not found")
        return

    description = clean_text(
        product.find(class_="cmp-product-details-main__description").text
    )

    nutrients = product.find_all("span", class_="sr-only sr-only-pd")
    try:
        calories = clean_text(nutrients[3].text).replace(" ", "")
        fats = clean_text(nutrients[6].text).replace(" ", "")
        carbs = clean_text(nutrients[9].text).replace(" ", "")
        proteins = clean_text(nutrients[12].text).replace(" ", "")
        secondary_nutritions = product.find_all("li", class_="label-item")
        unsaturated_fats = clean_text(
            get_value_from_string(secondary_nutritions[0].extract().text)
        )
        sugar = clean_text(
            get_value_from_string(secondary_nutritions[1].extract().text)
        )
        salt = clean_text(get_value_from_string(secondary_nutritions[2].extract().text))
        portion = clean_text(
            get_value_from_string(secondary_nutritions[3].extract().text)
        )
    except IndexError:
        logger.info(f"Nutrients not found for product: {name}")

    return {
        "name": name,
        "description": description,
        "calories": calories,
        "fats": fats,
        "carbs": carbs,
        "proteins": proteins,
        "unsaturated_fats": unsaturated_fats,
        "sugar": sugar,
        "salt": salt,
        "portion": portion,
    }
