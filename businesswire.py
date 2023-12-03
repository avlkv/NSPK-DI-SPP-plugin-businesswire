"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time
from selenium.webdriver.common.by import By
from src.spp.types import SPP_document
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class BUSINESSWIRE:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'businesswire'
    HOST = 'https://www.businesswire.com/portal/site/home/news/'
    _content_document: list[SPP_document]

    def __init__(self, webdriver, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []

        self.driver = webdriver
        self.wait = WebDriverWait(self.driver, timeout = 20)

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        self._parse()
        self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self, abstract=None):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        # driver_path = r'C:\Users\Artyom\Documents\1_UTILITY\chromedriver-win64\chromedriver.exe'
        #
        # chrome_options = webdriver.ChromeOptions()
        # """Объект опций запуска драйвера браузера Chrome"""
        #
        # # chrome_options.add_argument('--headless')
        # """Опция Chrome - Запуск браузера без пользовательского интерфейса (в фоне)"""
        #
        # # chrome_options.add_experimental_option('prefs', {'download.default_directory': downloads_dir, # Переопределение пути сохранения файлов для текущего запуска драйвера браузера Chrome
        # #                                                 'profile.default_content_setting_values.automatic_downloads': 1}) # Разрешить автоматическую загрузку файла без доп. согласия
        #
        # chrome_options.page_load_strategy = 'none'
        #
        # s = Service(executable_path=driver_path)
        # driver = webdriver.Chrome(service=s, options=chrome_options)
        # wait = WebDriverWait(driver, timeout=20)

        self.driver.get("https://www.businesswire.com/portal/site/home/news/")  # Открыть страницу со списком RFC в браузере
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bwNewsList')))

        while len(self.driver.find_elements(By.CLASS_NAME, 'pagingNext')) > 0:
            el_list = self.driver.find_element(By.CLASS_NAME, 'bwNewsList').find_elements(By.TAG_NAME, 'li')
            for el in el_list:
                article_link = el.find_element(By.CLASS_NAME, 'bwTitleLink')
                web_link = article_link.get_attribute('href')
                title = article_link.text
                pub_date = el.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(web_link)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bw-release-story')))
                text_content = self.driver.find_element(By.CLASS_NAME, 'bw-release-story').text
                # print(web_link)
                # print(title)
                # print(pub_date)
                # print(text_content)
                # print('-' * 45)

                document = SPP_document(
                    None,
                    title=title,
                    abstract=abstract if abstract else None,
                    text=text_content,
                    web_link=web_link,
                    local_link=None,
                    other_data=None,
                    pub_date=pub_date,
                    load_date=None,
                )
                # Логирование найденного документа
                self.logger.info(self._find_document_text_for_logger(document))

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.get(
                self.driver.find_element(By.CLASS_NAME, 'pagingNext').find_element(By.TAG_NAME, 'a').get_attribute('href'))
            # print('=== NEW_PAGE ===')
            # print('=' * 90)


        # ---
        # ========================================
        ...

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"