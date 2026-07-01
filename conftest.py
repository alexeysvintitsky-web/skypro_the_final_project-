import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import BASE_URL

def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome",
        help="Browser: chrome or firefox"
    )

@pytest.fixture(scope="function")
def browser(request):
    browser_name = request.config.getoption("--browser")
    if browser_name == "chrome":
        options = Options()
        driver = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        driver = webdriver.Firefox()
    else:
        raise ValueError("Unsupported browser")

    driver.get(BASE_URL)
    yield driver
    driver.quit()

# Рег. маркеры
def pytest_configure(config):
    config.addinivalue_line("markers", "ui: mark test as UI test")
    config.addinivalue_line("markers", "api: mark test as API test")