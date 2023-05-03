#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from bs4 import BeautifulSoup as soup
from time import sleep
import pandas as pd


# In[2]:


links = ['https://tiki.vn/laptop-truyen-thong/c29010?src=c.1846.hamburger_menu_fly_out_banner', 
         'https://tiki.vn/laptop-gaming/c5584?src=c.1846.hamburger_menu_fly_out_banner',
        'https://tiki.vn/laptop-2-trong-1/c29008?src=c.1846.hamburger_menu_fly_out_banner',
        'https://tiki.vn/macbook-imac/c2458?src=c.1846.hamburger_menu_fly_out_banner',
        'https://tiki.vn/chromebooks/c29012?src=c.1846.hamburger_menu_fly_out_banner']


# In[3]:


product_urls = set()

def getUrls(link):
    """ Lấy url dẫn đến trang chứa thông tin các sản phẩm """
    driver = webdriver.Chrome()
    driver.get(link)
    current_page = 1
    while True:
        product_items = driver.find_elements_by_class_name('product-item')

        for product_item in product_items:
            if 'https://tka.tiki.vn' not in product_item.get_attribute('href'):
                product_urls.add(product_item.get_attribute('href'))
                
        try:
            next_button = driver.find_elements_by_xpath('//*[@data-view-id="product_list_pagination_item"]')[-1]
        except:
            break
            
        next_page = int(next_button.get_attribute('data-view-label'))
        if current_page < next_page:  
            current_page = next_page
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            next_button.click()
            sleep(2)
        else:
            break
    driver.close()

for link in links:
    getUrls(link)
print('Completed crawling product\'s urls')


# In[12]:


def getDetailedInformation(driver):
    page_source = soup(driver.page_source, "html.parser")

    keys = []
    values = []
    
    try:
        # Handle trường hợp hết hàng (lúc này không hiện bảng cấu hình)
        thongTinChiTiet = page_source.find('div', class_="content has-table").find_all('tr')
    except:
        return 0
    
    try:
        # Handle trường hợp không tìm thấy sản phẩm
        name = page_source.find('h1', class_="title").get_text().strip()
    except:
        return 0
        
    keys.append('Tên sản phẩm')
    values.append(name)

    brand = page_source.find('a', {"data-view-id" : "pdp_details_view_brand"}).get_text().strip()
    keys.append('Thương hiệu')
    values.append(brand)
    
    seller_name = page_source.find('span', class_="seller-name").get_text().strip()
    keys.append('Nhà bán')
    values.append(seller_name)
    
    current_price = page_source.find('div', class_="product-price__current-price")
    if current_price:
        current_price = int(current_price.get_text().replace('₫','').replace('.',''))
    else:
        # Hanlde trường hợp giá đang được flash sale
        return 0
    keys.append('Giá hiện tại')
    values.append(current_price)
    
    for thongTin in thongTinChiTiet:
        thongTin = thongTin.find_all('td')
        thongTin[0] = thongTin[0].get_text()
        thongTin[1] = thongTin[1].get_text()
        keys.append(thongTin[0])
        values.append(thongTin[1])
    
    dictThongTin = dict(zip(keys, values))
    return dictThongTin


# In[13]:


product_urls = list(product_urls)
df = pd.DataFrame([])

driver = webdriver.Chrome()
for url in product_urls:
    driver.get(url)
    
    df_temp = getDetailedInformation(driver)
    if df_temp == 0:
        continue
    df_temp = pd.DataFrame.from_dict([df_temp])
    df = pd.concat([df, df_temp])


# In[16]:


df.to_excel('laptop.csv', encoding='UTF-8', index=False)