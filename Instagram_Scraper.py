from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from bs4 import BeautifulSoup
import time
import logging
from tqdm import tqdm
import pandas as pd
import argparse
import os
import wget

logger = logging.getLogger('InstaScraper')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

class InstaScraper():
    def __init__(self, username, password):
        self.__driver = webdriver.Chrome()
        self.__driver.get("http://www.instagram.com")
        self.__login(username, password)

    def __login(self, username_ig, password_ig):
        #Wait until the element be clickable => load it in the webpage
        username = WebDriverWait(self.__driver, 10).\
            until(EC.element_to_be_clickable\
                ((By.CSS_SELECTOR, "input[name='username']")))

        password = WebDriverWait(self.__driver, 10).\
            until(EC.element_to_be_clickable\
                ((By.CSS_SELECTOR, "input[name='password']")))

        #Cleaning the fields
        username.clear()
        username.send_keys(username_ig)
        password.clear()
        password.send_keys(password_ig)

        #Login
        login_button = WebDriverWait(self.__driver, 10)\
            .until(EC.element_to_be_clickable\
                ((By.CSS_SELECTOR, "button[type='submit']"))).click()

        #Skipping not now
        not_now = WebDriverWait(self.__driver, 10).\
            until(EC.element_to_be_clickable\
                ((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()
        #Use only if necessary!!!
	     #not_now2 = WebDriverWait(self.__driver, 10).\
            #until(EC.element_to_be_clickable\
                #((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()      

    def search(self, keyword):
        self.__driver.get("http://www.instagram.com/explore/tags/" + keyword + "/")

    def __lcondition(self, link):
        return '.com/p/' in link.get_attribute('href')

    def __get_user(self):
        '''
        Getting user
        '''
        xpath1 = '//div[contains(@id, "mount_0_0_")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section\
              /main/div/div[1]/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[1]/div/span/div/div/a'
        xpath2 = '//div[contains(@id, "mount_0_0_")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section\
              /main/div/div[1]/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[1]/span/div[1]/div/a'
        xpath3 = '//div[contains(@id, "mount_0_0_")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section\
        /main/div/div[1]/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[1]/span/div[2]/div/a'      
        

        try:
            user_element = self.__driver.find_element(By.XPATH, xpath1)
            user = user_element.get_attribute('href').split('/')[-2]
            return user
        except NoSuchElementException:
            # If the first XPath doesn't find an element, try the second XPath
            try:
                user_element1 = self.__driver.find_element(By.XPATH, xpath2)
                user1 = user_element1.get_attribute('href').split('/')[-2]
                return user1
            except NoSuchElementException:
                # If neither XPath finds an element, raise an error
                raise ValueError("Both XPath expressions failed to find an element")

    def filter_links(self, links):
        '''
        Filter post links
        '''
        post_links = []
        for link in links:
            try:
                if '.com/p/' in link.get_attribute('href'):
                    post_links.append(link)
            except:
                logger.warning("A https://www.instagram.com/p/ link was not found")
                continue
        return post_links


    def __get_links(self, nscrolls, scroll_pause_time):
        '''
        Getting posts links
        '''
        saved_links = {}
        rank = 0
        # Get scroll height
        last_height = \
            self.__driver.execute_script("return document.body.scrollHeight")

        for j in tqdm(range(nscrolls)):
            self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            links = self.__driver.find_elements(By.TAG_NAME, 'a')

            valid_links =  self.filter_links(links)

            for i in range(len(valid_links)):
                link = valid_links[i].get_attribute('href')
                if link not in saved_links.keys():
                    saved_links[link] = rank
                    rank += 1

            # Wait to load page
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = \
                self.__driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                # If heights are the same it will exit the function
                break
            last_height = new_height

        return saved_links

    def __get_caption(self):
        caption_xpath = '//div[contains(@id, "mount_0_0_")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section\
        /main/div/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/span/div/span'    
        caption = self.__driver.find_element(By.XPATH, caption_xpath)
        caption = caption.get_attribute('innerHTML')
        return caption
    
    def __get_likes(self):
        likes_xpath = '//div[contains(@id, "mount_0_0_")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section\
        /main/div/div[1]/div/div[2]/div/div[3]/section/div/div/span/a/span'
        likes_elements = self.__driver.find_elements(By.XPATH, likes_xpath)
        likes_list = []

        for likes in likes_elements:
            likes_text = likes.get_attribute('innerHTML')
            likes_list.append(likes_text)

        return likes_list

    def __get_date(self):
        '''
        Getting date
        '''
        date_xpath = '//div[contains(@id, "mount_0_0_")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section\
        /main/div/div[1]/div/div[2]/div/div[3]/div[2]/div/a/span/time'
        date = self.__driver.find_element(By.XPATH, date_xpath)
        date = date.get_attribute('datetime')
        return date


    def __get_image_data(self, link):
        '''
        Get image data
        '''
        infos = {}
        infos['type'] = 'image'
        infos['user'] = self.__get_user()
        infos['caption'] = self.__get_caption()
        infos['likes'] = self.__get_likes()
        infos['date'] = self.__get_date()
        infos['link'] = link

        return infos
    
    def download_images(self, keyword):
        self.search(keyword)
        time.sleep(5)

        # Scroll down to scrape more images
        self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Target all images on the page
        images = self.__driver.find_elements(By.TAG_NAME, 'img')
        images = [image.get_attribute('src') for image in images]
        images = images[:-2]

        print('Number of scraped images: ', len(images))

        path = os.getcwd()
        path = os.path.join(path, keyword + "s")

        # Create the directory
        os.mkdir(path)

        counter = 0
        for image in images[3:]:
            save_as = os.path.join(path, keyword + str(counter) + '.jpg')
            wget.download(image, save_as)
            counter += 1

        print("Images Saved Successfully!!!")


    def get_data(self, nscrolls, scroll_pause_time):
        '''
        Get all hashtag data
        '''
        links = self.__get_links(nscrolls, scroll_pause_time)
        logger.info(str(len(links)) + " links were found.")

        processed_data = []
        for link,rank in tqdm(links.items()):
            infos = {}

            #Accessing the post
            self.__driver.get(link)
            time.sleep(1)

            try:
                infos = self.__get_image_data(link)

            except:
                logger.warning("Failed to retrieve " + link + ' data. Skipping.')
                time.sleep(3)
                continue

            if infos not in processed_data and infos is not None:
                processed_data.append(infos)
            time.sleep(1)

        return processed_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', required=True, help="Instagram login")
    parser.add_argument('-p', '--password', required=True, help="Instagram password")
    parser.add_argument('-s', '--search', default='test', required=True, help="Hashtag to be searched")
    parser.add_argument('-n', '--n_scrolls', default=100, required=True, help="Number of scrolls")
    parser.add_argument('-o', '--output', default='test.csv', required=True, help="Output filename")

    args = parser.parse_args()

    my_bot = InstaScraper(username=args.login, password=args.password)

    time.sleep(5)
    my_bot.search(args.search)
    time.sleep(5)

    data = my_bot.get_data(nscrolls=int(args.n_scrolls), scroll_pause_time=5)

    logger.info(str(len(data)) + " links were found.")

    df = pd.DataFrame(data)
    df.to_csv(args.output, index=False)
    logger.info("Results saved at " + args.output)

    # Download images
    my_bot.download_images(args.search)
    print("Process completed successfully")

if __name__ == "__main__":
    main()
