# import Splinter and BeautifulSoup
from re import M
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import datetime as dt

def scrape_all():    
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'last_modified': dt.datetime.now(),
        'hemispheres': mars_hem(browser)
    }
    browser.quit()
    return data

def mars_news(browser):
    # visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    #optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')

        # use the parent element to find the first 'a' tag and save it as news_title
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

#Featured Images

def featured_image(browser):
    #visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # parse resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    #create url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    return df.to_html(classes='table table-striped table-hover').replace('dataframe ', '')

def mars_hem(browser):
    # Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hem_soup = soup(html, 'html.parser')

    try:
        # creates a list that holds the html of class 'description'
        img_url_rel = hem_soup.find_all('div', class_='description')
        # go through the html to find the names and links to the page containing the image
        for link in img_url_rel:
            # add the names into a variable
            name = link.find('a').find('h3').get_text()
            # get the link to the next page holding the full image
            link = link.find('a').get('href')
            # visit and parse the url
            browser.visit(url + link)
            html = browser.html
            hem_soup = soup(html, 'html.parser')
            # get the link to the image
            img_url = hem_soup.find('div', class_="downloads").find('ul').find('li').find('a').get('href')
            #add a dictionary of the names and link into the list
            hemisphere_image_urls.append({'img_url': url+img_url, 'title': name})
    except AttributeError:
        return None
    
    return hemisphere_image_urls

if __name__ == '__main__':
    print(scrape_all())


