import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL


def wait_element(browser, by, value, timeout=10):
    """Ожидаем появления конкретного элемента"""
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def click_js(browser, element):
    browser.execute_script("arguments[0].click();", element)


def get_search_input(browser):
    """Ждем именно поле поиска"""
    locators = [
        (By.NAME, "kp_query"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.XPATH, "//input[@placeholder='Поиск']")
    ]
    for by, value in locators:
        try:
            return wait_element(browser, by, value, timeout=5)
        except:
            continue
    pytest.fail("Поле поиска не найдено")


@pytest.mark.ui
@allure.title("Поиск фильма по названию")
@allure.story("UI: Поиск")
def test_search_movie(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)

    with allure.step("Найти поле поиска и ввести запрос"):
        search = get_search_input(browser)
        search.clear()
        search.send_keys("Интерстеллар")
        search.submit()

    with allure.step("Дождаться результатов поиска"):
        WebDriverWait(browser, 10).until(
            lambda driver: "search" in driver.current_url.lower()
        )
        assert "search" in browser.current_url.lower()


@pytest.mark.ui
@allure.title("Переход на страницу фильма с главной")
@allure.story("UI: Навигация")
def test_navigate_to_popular_movie(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)

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

    with allure.step("Дождаться загрузки страницы фильма"):
        WebDriverWait(browser, 10).until(
            lambda driver: "film" in driver.current_url.lower()
        )
        assert "film" in browser.current_url.lower()


@pytest.mark.ui
@allure.title("Проверка наличия рейтинга на странице фильма")
@allure.story("UI: Карточка фильма")
def test_movie_card_rating(browser):
    with allure.step("Открыть страницу фильма 'Аватар'"):
        browser.get(f"{BASE_URL}/film/251733/")

    with allure.step("Найти элемент с рейтингом через JavaScript"):
        rating_text = WebDriverWait(browser, 10).until(
            lambda driver: driver.execute_script("""
                var elements = document.querySelectorAll('*');
                for (var i = 0; i < elements.length; i++) {
                    var text = elements[i].textContent.trim();
                    if (text && /^\\d+[.,]\\d+$/.test(text)) {
                        return text;
                    }
                }
                return null;
            """)
        )

    with allure.step("Проверить, что рейтинг найден"):
        assert rating_text is not None
        rating_value = float(rating_text.replace(',', '.'))
        assert rating_value > 0


@pytest.mark.ui
@allure.title("Поиск фильма по актеру")
@allure.story("UI: Поиск")
def test_search_by_actor(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)

    with allure.step("Найти поле поиска и ввести имя актера"):
        search = get_search_input(browser)
        search.clear()
        search.send_keys("Леонардо ДиКаприо")
        search.submit()

    with allure.step("Дождаться результатов поиска"):
        WebDriverWait(browser, 10).until(
            lambda driver: "search" in driver.current_url.lower()
        )
        assert "search" in browser.current_url.lower()


@pytest.mark.ui
@allure.title("Поиск фильмов по жанру 'Комедия'")
@allure.story("UI: Поиск")
def test_search_by_genre(browser):
    with allure.step("Открыть главную страницу"):
        browser.get(BASE_URL)

    with allure.step("Найти поле поиска и ввести жанр"):
        search = get_search_input(browser)
        search.clear()
        search.send_keys("комедия")
        search.submit()

    with allure.step("Дождаться результатов поиска"):
        WebDriverWait(browser, 10).until(
            lambda driver: "search" in driver.current_url.lower()
        )
        assert "search" in browser.current_url.lower()