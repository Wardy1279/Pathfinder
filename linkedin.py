from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os
import random

# Set up the browser (make sure you have the ChromeDriver installed)
driver = webdriver.Chrome()

# Go to LinkedIn login page
driver.get("https://www.linkedin.com/login")

# Log in
username = driver.find_element(By.ID, "username")
username.send_keys("wardy2524@gmail.com")
password = driver.find_element(By.ID, "password")
linkedin_pword = os.environ['LINKEDIN_PWORD']
password.send_keys(linkedin_pword)
password.send_keys(Keys.RETURN)

# Wait for login to complete and for the job search page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-search")))

# Define keyword and location
keyword = 'Engineer'
location = 'Sydney'

# List to store all job data
jobs = []

# Function to scrape job listings on the current page
def scrape_current_page():
    # Improved scrolling function for specific element with specific class name
    def scroll_element(class_name):
        jobs_container = driver.find_element(By.CLASS_NAME, class_name)
        last_height = driver.execute_script("return arguments[0].scrollHeight", jobs_container)

        while True:
            # Scroll incrementally
            driver.execute_script("arguments[0].scrollTop += 500", jobs_container)

            # Wait for new content to load
            time.sleep(random.uniform(1.5, 3.0))  # Randomize delay

            # Calculate new height and compare with last height
            new_height = driver.execute_script("return arguments[0].scrollHeight", jobs_container)
            if new_height == last_height:
                break
            last_height = new_height

    # Perform scrolling within the jobs container
    scroll_element("jobs-search-results-list")

    # Get page content and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Check if the job listings are found
    job_listings = soup.find_all('li', class_='jobs-search-results__list-item')
    print(f"Number of job listings found: {len(job_listings)}")

    # For Each Listing
    for listing in job_listings:
        job_data = {}

        # Get Role Title
        title_element = listing.find('span', class_='visually-hidden')
        if title_element:
            job_data["job_title"] = title_element.get_text(strip=True)

        # Get Company
        company_element = listing.find('span', class_='job-card-container__primary-description')
        if company_element:
            job_data["company_name"] = company_element.get_text(strip=True)

        # Get ID and Construct URL
        ID_element = listing.find('a', class_='job-card-container__link')
        if ID_element:
            href_value = ID_element['href']
            segments = [segment for segment in href_value.split('/') if segment]
            if len(segments) > 2:  # Ensure segments have enough parts
                job_data["url"] = 'https://www.linkedin.com/jobs/view/' + segments[2]
            else:
                print(f"URL segment issue: {href_value}")

        if job_data.get("url") is None:
            print(f"Missing URL for job data: {job_data}")

        # Add the job data to the list
        jobs.append(job_data)

# Iterate through the first 4 pages
for page_number in range(4):
    # Construct the search URL with pagination
    start = page_number * 25
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}&start={start}"
    driver.get(search_url)

    # Wait for the job listings container to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list")))

    # Scrape the current page
    scrape_current_page()

# After collecting all job URLs, iterate through them to find descriptions
for job in jobs:
    if 'url' not in job:
        print(f"Skipping job with missing URL: {job}")
        continue

    driver.get(job['url'])

    # Random delay before loading the job description
    time.sleep(random.uniform(3, 6))

    try:
        # Wait for the job description to load (adjust the time as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-description__content--condensed")))

        # Extract the job description
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        description_div = soup.find('div', class_='jobs-description__content--condensed')

        job_description = description_div.get_text(strip=True) if description_div else "Description not available"
        job['description'] = job_description  # Save the description to the job dictionary

    except Exception as e:
        print(f"Error loading job description for {job['url']}: {e}")
        job['description'] = "Description not available"

# Close the browser
driver.quit()

# Define the CSV file name
csv_file = 'linkedin_jobs.csv'

# Specify the keys of your dictionary that you want as columns in the CSV
fieldnames = ['job_title', 'company_name', 'url', 'description']

# Writing to the CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    # Write the header (field names)
    writer.writeheader()

    # Write the data rows
    for job in jobs:
        writer.writerow(job)

print(f"Data successfully saved to {csv_file}")
