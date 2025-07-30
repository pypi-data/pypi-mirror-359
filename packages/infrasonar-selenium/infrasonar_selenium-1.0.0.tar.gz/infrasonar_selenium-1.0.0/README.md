# InfraSonar Selenium Test Suite

## Requirements

* Python (3.12 or higher)
* Docker

## Usage

Make sure the lib is installed:
```bash
pip install infrasonar_selenium
```

Start Selenium:
```bash
docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome
```

Write a test: _(for example, save the following to `mytest.py`)_

```python
from infrasonar_selenium import TestBase
from selenium import webdriver
from selenium.webdriver.common.by import By


class MyTest(TestBase):

    description = 'Example test'
    url = 'https://www.selenium.dev/selenium/web/web-form.html'
    version = 'v0'

    @classmethod
    def test(cls, driver: webdriver.Remote):
        title = driver.title
        assert title == "Web form"

        driver.implicitly_wait(0.5)

        text_box = driver.find_element(by=By.NAME, value="my-text")
        submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

        text_box.send_keys("Selenium")
        submit_button.click()

        message = driver.find_element(by=By.ID, value="message")
        value = message.text

        assert value == "Received!"


export = MyTest

if __name__ == '__main__':
    MyTest().print_run()  # Prints the output
```

Start the test:
```bash
python mytest.py
```


With the following link you can view your scripts in action:

http://localhost:7900/?autoconnect=1&resize=scale&password=secret

> The same applies for scripts running with InfraSonar, except replace `localhost` with your appliance server address.
