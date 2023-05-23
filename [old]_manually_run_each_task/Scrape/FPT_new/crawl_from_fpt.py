#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
from Scrape.utils.base_class import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# In[30]:


class FptScraper(BaseScraper):

    def __init__(self):
        super(FptScraper, self).__init__(driver_type="chrome")
        self.driver.get("https://fptshop.com.vn/may-tinh-xach-tay")
        
        try:
            while True:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-light")))
                self.driver.find_element_by_css_selector(".btn-light").click()
        except:
            laptops = self.driver.find_elements_by_xpath('//div[@class="cdt-product-wrapper m-b-20"]/div/div/a')
                
        self.links = set([laptop.get_attribute('href') for laptop in laptops])

        
    def _go_to_first_tab(self) -> None:
        self.driver.switch_to.window(self.driver.window_handles[0])

    def _go_to_new_tab(self, *args, link=None) -> None:
        self.driver.execute_script(f'''window.open("{link}","new_window");''')
        self.driver.switch_to.window(self.driver.window_handles[1])


    def _parse_specifications(self, link):
        self.driver.get(link)

        specs_info = {'Tên': self.driver.find_element_by_css_selector('.st-name').text,
                      'Giá': int(self.driver.find_element_by_css_selector('.st-price-main').text.replace('₫', '').replace('.',''))}

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "Xem cấu hình chi tiết")))
        self.driver.find_element_by_link_text("Xem cấu hình chi tiết").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.c-modal__content > div.c-modal__row > table.st-table td")))
        list_specs = self.driver.find_elements_by_css_selector(
            "div.c-modal__content > div.c-modal__row > table.st-table td")
        for i in range(0, len(list_specs) - 1, 2):
            specs_info[list_specs[i].text] = list_specs[i + 1].text

        table_specs = self.driver.find_elements_by_css_selector("ul.st-list > li")
        for info in table_specs:
            key, value = info.text.split(":  \n")
            specs_info[key] = value
        return specs_info
    
    def parse(self, *args, export=True) -> None:
        output = pd.DataFrame([])
        for link in self.links:
            try:
                basic_info = self._parse_specifications(link)
                output = pd.concat([output, pd.DataFrame.from_dict([basic_info])])
            except BaseException as e:
                print(e)
                print("Lỗi sản phẩm", link)
        output.to_csv('raw_data_FPT_new.csv', encoding='UTF-8', index=False)


# In[31]:


bot = FptScraper()
bot.parse()

