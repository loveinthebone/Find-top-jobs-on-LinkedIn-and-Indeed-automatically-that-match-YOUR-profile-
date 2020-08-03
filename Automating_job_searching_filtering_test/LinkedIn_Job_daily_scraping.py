# Import modules
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import os
from googletrans import Translator
from datetime import datetime
import time

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

# In[] main cell
def main():
    driver = initialize()
    scroll_down(driver)
    show_all_posts(driver)
    goto_first_page(driver)
    jobs_list = extract_information(driver)
    driver.close()

    # Save the data
    rel_path = r"data\Linkedin_job_posts_daily.csv"
    path = os.path.join(script_dir, rel_path)
    save_to_file(jobs_list, path)

# In[] Initialize a browser
def initialize():
    rel_path = r"chromedriver"
    DRIVER_PATH = os.path.join(script_dir, rel_path)
    
    # options = Options()
    # options.headless = True
    # options.add_argument("--window-size=1920,1200")
    # driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    driver = webdriver.Chrome(executable_path=DRIVER_PATH)

    driver.implicitly_wait(10) # seconds
    query = '((engineer OR scientist OR researcher OR engineering OR technician) AND (master OR m.sc OR msc OR phd OR masters) -internship -intern)'
    location = 'Netherlands'
    one_day_job_url = 'https://www.linkedin.com/jobs/search?keywords={}&location={}&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0&f_TP=1'.format(query, location)
    # A url for test:
    # https://www.linkedin.com/jobs/search?keywords=%28engineer%20OR%20scientist%20OR%20researcher%20OR%20engineering%20OR%20technician%29%20AND%20%28master%20OR%20M.Sc%20OR%20MSc%20OR%20PhD%29%20-internship%20-intern&location=Netherlands&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0&f_TP=1
    driver.get(one_day_job_url)
    # time.sleep(3)

    # # get how many jobs in total
    # driver.execute_script("window.scrollTo(0, 0);")  
    return driver

# test 
# driver = initialize()

# In[] test scroll to the end
#source from: https://stackoverflow.com/questions/48850974/selenium-scroll-to-end-of-page-in-dynamically-loading-webpage
def scroll_down(driver):
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
     
        # Wait to load the page.
        time.sleep(1) # if this wait is not long enough, maybe the scrolling is not executed yet, then the if statement below will be true

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            # maybe the page is not refreshed fast enough, give it one more long chance:
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

        last_height = new_height

# scroll_down(driver)

# In[] Go back to first page
def goto_first_page(driver):
    driver.execute_script("window.scrollTo(0, 0);")

# In[3] translate a string to english

def translate(string):
    translator = Translator()
    result = translator.translate(string, src = 'nl')
    return result.text

# In[]
def show_all_posts(driver):
    more_jobs_selector = '//*[@id="main-content"]/div/section/button'

    # # Use following xpath doesn't work because this element is always there, even when there are more jobs to be loaded
    # all_jobs_shown = '//span[@class = "inline-notification__text"]'
    
    # after load 1000 jobs, the "See more jobs" button is still clickable, but doesn't really load more jobs.
    # So maximum jobs can be scraped a time is 1000. 
    #/
    # After load 1000 jobs, the "See more jobs" button is still clickable, but doesn't really load more jobs.
    # So maximum jobs can be scraped a time is 1000. Here is how to avoid a infinite look of clicking the
    # "see more jobs" button:
    # 1. remeber the scrollHeight before the nth click of the button
    # 2. scroolIntoView of the button, click it
    # 3. wait until the button is clickable again
    # 4. get the current scrollHeight, if it is the same as previous, means the position of current button is the 
    # same as last time. So no more jobs can be loaded
    # 5. If the button never become clickable again in the maximum waiting time, it means the total jobs is less than 1000.
    # Then just break the while loop.#/
    # use the method in the scroll down function, if the scroll height doesn't change anymore, break the while loop
    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, more_jobs_selector))))
            # print("great! click it!")
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, more_jobs_selector))))
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, more_jobs_selector)))
        except:
            break
        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height


# # test
# show_all_posts(driver)

# print(num_results)

# In[] extract all information
def extract_information(driver):
    # driver.implicitly_wait(10) # seconds
    selector = "//h1/span[1]"
    try:
        num_results = driver.find_element_by_xpath(selector).text
    except Exception as e:
        num_results = None
        print("can't get the estimated job posts number from the page!")
    start_time = time.time()
    all_jobs_list = []

    # since I search everyday, don't need to extract the publish date information from web
    job_publish_date = dateString = datetime.strftime(datetime.now(), '%Y_%m_%d')

    description_selector = '//*[@id="main-content"]/section/div[2]/section[2]/div/section/div'

    job_list_xpath = '//*[@id="main-content"]/div/section/ul/li'
    job_posts_number = len(driver.find_elements_by_xpath(job_list_xpath))
    
    for index in range(job_posts_number): # For testing, replace job_posts_numver with a small number, like 10.
        job_post_xpath = job_list_xpath + '[{}]'.format(index+1)

        # Now get the descriptions
        # click on every job post, then extract description
        driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_element_by_xpath(job_post_xpath))
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, job_post_xpath))))

        job_title_xpath = job_post_xpath + '/a/span'
        # job_title = driver.find_element_by_xpath(job_title_xpath).get_attribute('innerHTML')
        # print(job_title)

        company_xpath = job_post_xpath + '/div[1]/h4'
        # job_company = driver.find_element_by_xpath(company_xpath).text
        # print(job_company)

        # publish_date_xpath = job_post_xpath + '/div[1]/div/time'
        # job_publish_date = driver.find_element_by_xpath(publish_date_xpath).get_attribute('datetime')
        # print(job_publish_date)

        # job url xpath example: //*[@id="main-content"]/div/section[2]/ul/li[4]/a
        job_url_path = job_post_xpath + "/a"

        try:
            job_title = driver.find_element_by_xpath(job_title_xpath).get_attribute('innerHTML')
            job_company = driver.find_element_by_xpath(company_xpath).text
            job_url = driver.find_element_by_xpath(job_url_path).get_attribute('href')

            # description = "test"
            # Here I wait for the apply now button clickable to extract the job description
            wait = WebDriverWait(driver, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-content"]/section/div[2]/section[1]/div[1]/div[2]')))

            description = driver.find_element_by_xpath(description_selector).get_attribute('innerText') # Here avoid click the "More" button on the webpage
            description = os.linesep.join([s for s in description.splitlines() if s])
            description = translate(description) # no matter the text is in nl or en, it will become english with this code
        except:
            print("extract from child url failed: {}.".format(job_url))
            continue
        all_jobs_list.append([job_title, job_company, job_publish_date, job_url, description])
        print("Extracted the {}th job.".format(index+1))

    end_time = time.time()
    print("estimated job posts number: {}".format(num_results))
    print("Time take for extracting all jobs is : {} seconds".format(end_time-start_time))
    return all_jobs_list


# # Test:
# driver = initialize()
# test = extract_information(driver)
# driver.close()

# In[] save data to a file
def save_to_file(data, save_path):
    import csv

    jobs_list = data
    # jobs_list = [[1,2,3],[3,4,5]]

    # Save data to a csv file
    file_name = save_path
    # file_name = r'E:\Python3732\Scripts\web_scraping\Web_scraping_Selenium\linkedin-jobs-scraper-master\linkedin-jobs-scraper-master\linkedin_job_scraping.csv' # r here means "raw strings"
    file_exists = os.path.isfile(file_name)
    with open(file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["job_title", "job_company", "search_date", "description", "job_url"])
        writer.writerows(jobs_list)

# # test
# jobs_list = [[1,2,3,4],[3,4,5,19]]
# file_name = r'E:\Python3732\Scripts\web_scraping\Web_scraping_Selenium\linkedin-jobs-scraper-master\linkedin-jobs-scraper-master\linkedin_job_scraping.csv' # r here means "raw strings"
# save_to_file(jobs_list, file_name)

# In[] Run
if __name__ == "__main__":
    main()