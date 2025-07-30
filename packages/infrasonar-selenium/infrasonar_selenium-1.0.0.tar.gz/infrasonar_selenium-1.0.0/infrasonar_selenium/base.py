import abc
import time
import pprint
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


class TestBase(abc.ABC):
    url: str
    description: str
    version: str

    def __init_subclass__(cls, **kwargs):
        for key in ('url', 'description', 'version'):
            if not hasattr(cls, key):
                raise NotImplementedError(f'`{key}` not implemented')
            if not isinstance(getattr(cls, key), str):
                raise NotImplementedError(f'`{key}` must be type str')
        return super().__init_subclass__(**kwargs)

    @classmethod
    def run(cls, name: str | None = None,
            driver: webdriver.Remote | None = None):
        '''
        Used to run the test

        Arguments:
         - `name`: the unique name for the test
         - `driver`: can be used to specify a (local) webdriver
        '''
        if driver is None:
            options = webdriver.ChromeOptions()
            driver = webdriver.Remote(
                options=options,
                command_executor="http://localhost:4444")

        t0 = time.time()
        success = True
        error = None

        try:
            driver.get(cls.url)
            cls.test(driver)
        except WebDriverException as e:
            success = False
            error = e.msg or type(e).__name__
        except Exception as e:
            success = False
            error = str(e) or type(e).__name__
        finally:
            driver.quit()
        return {
            'name': name or  cls.__name__,  # str
            'test': cls.__name__,  # str
            'url': cls.url,  # str
            'success': success,  # int
            'error': error,  # str?
            'duration': time.time() - t0,  # float
            'description': cls.description,  # str
            'version': cls.version,  # str
        }

    @classmethod
    def print_run(cls, name: str | None = None,
                  driver: webdriver.Remote | None = None):
        res = cls.run(name=name, driver=driver)
        pprint.pprint(res)

    @classmethod
    def test(cls, driver: webdriver.Remote):
        ...
