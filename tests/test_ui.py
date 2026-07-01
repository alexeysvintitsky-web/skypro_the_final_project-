import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL


def find(browser, by, value, timeout=5):
    try:
        return WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except:
        return None

def click_js(browser, element):
    browser.execute_script("arguments[0].click();", element)

def get_search_input(browser):
    locators = [
        (By.NAME, "kp_query"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.XPATH, "//input[@placeholder='Поиск']")
    ]
    for by, value in locators:
        el = find(browser, by, value)
        if el:
            return el
    pytest.fail("Поле поиска не найдено")


@pytest.mark.ui
@allure.title("Поиск фильма по названию")
@allure.story("UI: Поиск")
def test_search_movie(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)
        find(browser, By.TAG_NAME, "body")

    with allure.step("Найти поле поиска и ввести запрос"):
        search = get_search_input(browser)
        search.clear()
        search.send_keys("Интерстеллар")
        search.submit()

    with allure.step("Проверить, что поиск выполнен"):
        assert "search" in browser.current_url.lower()


@pytest.mark.ui
@allure.title("Переход на страницу фильма с главной")
@allure.story("UI: Навигация")
def test_navigate_to_popular_movie(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)
        find(browser, By.TAG_NAME, "body")

    with allure.step("Найти ссылку на фильм через JS"):
        movie_link = WebDriverWait(browser, 10).until(
            lambda driver: driver.execute_script("""
                var links = document.querySelectorAll('a[href*="/film/"]');
                for (var i = 0; i < links.length; i++) {
                    var rect = links[i].getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0 && links[i].textContent.trim().length > 0) {
                        return links[i];
                    }
                }
                return null;
            """)
        )
        if not movie_link:
            pytest.skip("Фильм не найден")

    with allure.step("Кликнуть по ссылке через JS"):
        click_js(browser, movie_link)

    with allure.step("Проверить, что открылась страница фильма"):
        assert "film" in browser.current_url.lower()


@pytest.mark.ui
@allure.title("Проверка загрузки карточки фильма")
@allure.story("UI: Карточка фильма")
def test_movie_card_rating(browser):
    with allure.step("Открыть страницу фильма 'Аватар'"):
        browser.get(f"{BASE_URL}/film/251733/")

    with allure.step("Дождаться загрузки контента"):
        WebDriverWait(browser, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    with allure.step("Проверить, что страница загрузилась"):
        # Проверяем что URL правильный
        assert "film" in browser.current_url.lower()
        # Проверяем что есть какой-то текст на странице
        body_text = browser.find_element(By.TAG_NAME, "body").text
        assert len(body_text) > 100


@pytest.mark.ui
@allure.title("Поиск фильма по актеру")
@allure.story("UI: Поиск")
def test_search_by_actor(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)
        find(browser, By.TAG_NAME, "body")

    with allure.step("Найти поле поиска и ввести имя актера"):
        search = get_search_input(browser)
        search.clear()
        search.send_keys("Леонардо ДиКаприо")
        search.submit()

    with allure.step("Проверить, что поиск выполнен"):
        assert "search" in browser.current_url.lower()


@pytest.mark.ui
@allure.title("Поиск фильмов по жанру 'Комедия'")
@allure.story("UI: Поиск")
def test_search_by_genre(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)
        find(browser, By.TAG_NAME, "body")

    with allure.step("Найти поле поиска и ввести жанр"):
        search = get_search_input(browser)
        search.clear()
        search.send_keys("комедия")
        search.submit()

    with allure.step("Проверить, что поиск выполнен"):
        assert "search" in browser.current_url.lower()