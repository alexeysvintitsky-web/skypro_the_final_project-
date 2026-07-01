import allure
import pytest
import requests
import time
from config import API_TOKEN

USE_REAL_API = bool(API_TOKEN and API_TOKEN != "ваш_токен_сюда")
REAL_API_URL = "https://api.kinopoisk.dev/v1.4"
API_BASE_URL = REAL_API_URL if USE_REAL_API else MOCK_API_URL


def get_headers():
    if USE_REAL_API:
        return {"X-API-KEY": API_TOKEN}
    return {}


@allure.step("Отправить GET запрос на {url}")
def safe_get(url, headers=None):
    response = requests.get(url, headers=headers or {})

    if "text/html" in response.headers.get("Content-Type", ""):
        allure.attach(
            response.text[:500],
            "Сервер вернул HTML вместо JSON",
            allure.attachment_type.TEXT
        )

        response.status_code = 503
        response._content = b'{"error": "Service unavailable"}'

    return response


@pytest.mark.api
@allure.title("Получение информации о фильме по ID")
@allure.story("API: Фильмы")
def test_get_movie_by_id():
    movie_id = 251733
    url = f"{API_BASE_URL}/movie/{movie_id}" if USE_REAL_API else f"{API_BASE_URL}/posts/1"

    response = safe_get(url, headers=get_headers())

    with allure.step("Проверить статус ответа"):
        assert response.status_code == 200

    with allure.step("Проверить, что ответ содержит JSON"):
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            pytest.fail("Ответ сервера не является JSON. Проверьте API-ключ.")

    with allure.step("Проверить данные"):
        if USE_REAL_API:
            assert "name" in data
        else:
            assert "id" in data


@pytest.mark.api
@allure.title("Поиск фильмов по ключевому слову")
@allure.story("API: Поиск")
def test_search_movies_by_keyword():
    keyword = "Зеленая миля"
    if USE_REAL_API:
        url = f"{API_BASE_URL}/movie/search?query={keyword}"
    else:
        url = f"{API_BASE_URL}/posts?userId=1"

    response = safe_get(url, headers=get_headers())

    with allure.step("Проверить статус ответа"):
        assert response.status_code == 200

    with allure.step("Проверить, что ответ содержит JSON"):
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            pytest.fail("Ответ сервера не является JSON. Проверьте API-ключ.")

    with allure.step("Проверить наличие результатов"):
        if USE_REAL_API:
            assert "docs" in data
        else:
            assert len(data) > 0


@pytest.mark.api
@allure.title("Получение списка популярных фильмов")
@allure.story("API: Популярное")
def test_get_popular_movies():
    if USE_REAL_API:
        url = f"{API_BASE_URL}/movie?page=1&limit=10&sortField=rating.kp&sortType=-1"
    else:
        url = f"{API_BASE_URL}/posts?_limit=10"

    response = safe_get(url, headers=get_headers())

    with allure.step("Проверить статус ответа"):
        assert response.status_code == 200

    with allure.step("Проверить, что ответ содержит JSON"):
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            pytest.fail("Ответ сервера не является JSON. Проверьте API-ключ.")

    with allure.step("Проверить количество элементов"):
        if USE_REAL_API:
            assert "docs" in data
            assert len(data["docs"]) == 10
        else:
            assert len(data) == 10


@pytest.mark.api
@allure.title("Негативный тест: несуществующий ID")
@allure.story("API: Негативные сценарии")
def test_get_by_invalid_id():
    invalid_id = 999999999
    if USE_REAL_API:
        url = f"{API_BASE_URL}/movie/{invalid_id}"
    else:
        url = f"{API_BASE_URL}/posts/9999"

    response = safe_get(url, headers=get_headers())

    with allure.step("Проверить статус 400"):
        assert response.status_code in [400]


@pytest.mark.api
@allure.title("Проверка скорости ответа API")
@allure.story("API: Производительность")
def test_api_response_time():
    if USE_REAL_API:
        url = f"{API_BASE_URL}/movie/251733"
    else:
        url = f"{API_BASE_URL}/posts/1"

    with allure.step("Отправить GET запрос и измерить время"):
        start_time = time.time()
        response = safe_get(url, headers=get_headers())
        elapsed_time = time.time() - start_time

    with allure.step("Проверить статус ответа"):
        assert response.status_code == 200

    with allure.step("Проверить, что время ответа менее 3 секунд"):
        assert elapsed_time < 3.0, f"Время ответа {elapsed_time:.2f} секунд"