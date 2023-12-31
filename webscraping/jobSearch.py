import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def runJob(skills, location):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    # Create lists to store the job titles, company names, and links
    job_titles = []
    company_names = []
    links = []

    base_url = "https://uk.indeed.com"
    driver.get("https://uk.indeed.com/jobs?q=" + skills + "&l=" + location)
    print("https://www.indeed.com/jobs?q=" + skills + "&l=" + location)
    content = driver.page_source

    soup = BeautifulSoup(content, "html.parser")

    print("fetch done")

    # Find the container containing job cards
    job_cards_container = soup.find(id="mosaic-provider-jobcards")

    # Check if the container exists
    if job_cards_container:
        # Iterate through each job card
        for job_card in job_cards_container.find_all('div', class_='cardOutline'):
            # Find the job title, company name, and link within each job card
            job_title = job_card.find('span', {'id': lambda x: x and x.startswith('jobTitle-')}).text
            company_name = job_card.find('span', {'data-testid': 'company-name'}).text
            link = job_card.find('a', {'data-jk': True})['href']

            # Append the information to the respective lists
            job_titles.append(job_title)
            company_names.append(company_name)
            links.append(link)

    # Create a list of dictionaries
    jobs_list = []

    for title, company, link in zip(job_titles, company_names, links):
        job_dict = {
            "Job Title": title,
            "Company Name": company,
            "Link": base_url + link
        }
        jobs_list.append(job_dict)

    # Save the data as JSON
    with open('jobs_data.json', 'w') as json_file:
        json.dump(jobs_list, json_file)

    return jobs_list
