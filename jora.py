from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Configure Selenium to use headless Chrome browser
chrome_options = Options()
chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

try:
    # URL of the Jora page to scrape
    url = 'https://au.jora.com/j?sp=homepage&trigger_source=homepage&q=Engineer&l=Sydney'

    # Open the webpage
    driver.get(url)

    # Wait for jobresults to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobresults')))

    # Get the page source after JavaScript has executed
    html = driver.page_source

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all job listings within the divs with class 'job-card'
    job_results = soup.find_all('div', class_='job-card')

    # Initialize lists to store the extracted data
    roles = []
    companies = []
    job_urls = []

    # Loop through each job listing and extract the necessary information
    for job in job_results:
        # Extract the role title
        role_tag = job.find('a', class_='show-job-description')
        role = role_tag.text.strip()

        # Extract the company name
        company_tag = job.find('span', class_='job-company')
        company = company_tag.text.strip()

        # Extract the job URL
        #job_url = role_tag['href']

        # Append the data to the respective lists
        roles.append(role)
        companies.append(company)
        #job_urls.append(job_url)

    # Print the extracted data
    for idx, (role, company) in enumerate(zip(roles, companies), 1):
        print(f'Job {idx}:')
        print(f'Role: {role}')
        print(f'Company: {company}')
        #print(f'Job URL: {job_url}\n')

finally:
    # Close the browser
    driver.quit()
