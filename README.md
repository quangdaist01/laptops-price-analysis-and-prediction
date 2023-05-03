# Laptops price analysis and prediction on Thegioididong.com

This is the final project of the course Data analysis and visualization (DS103). In the project, we collect, preprocess and analyze the the price of second-hand laptops on [thegioididong](https://www.thegioididong.com/may-doi-tra/laptop). We also build a simple model to predict the price of an used laptop based on our deduced important features. The deployment of the model is at https://tgdd-laptop-price-prediction.herokuapp.com/

Our main work includes:
1. Scrape all laptops' features on [thegioididong](https://www.thegioididong.com/may-doi-tra/laptop) (11:35, 28/10/2021).
2. Data cleansing on the raw dataset
3. Transforming features based on the original ones
4. Performing EDA on the tidy dataset
5. Build a model to predict the second-hand prices
6. Deploy the model on a cloud platform.

Our dataset contains 1234 rows and 35 features. After analyzing, we found that the most important features consists of brand, material, cpu_type, gpu_type, ram, has_touchscreen, weight, ppi. Our best model (Ridge Regression with 5th polonomial degree) achieves R2 score of 0.775 on the test set.

## Note
Beside collecting on thegioididong.com, at first, we have successfully scraped the laptops from some other websites:
- dienmayxanh.com (new laptops): 144 rows, 31 features
- tiki.vn (new laptops): 104 rows, 41 features
- fptshop.com.vn (new laptops): 144 rows, 67 features
- gearvn.com (new laptops): 96 rows, 41 features
- fptshop.com.vn (second-hand laptops): 28 rows, 69 features
