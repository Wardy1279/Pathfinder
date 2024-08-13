import openai
import pandas as pd
import os

# Function to prepare the prompt for ChatGPT
def prepare_prompt(resume_text, jobs_df):
    prompt = (f"Rank the following jobs based on their suitability to my resume. Provide a list from the most suitable "
              f"to the least suitable. Please note that this is my first role out of university and I need a job with "
              f"minimal required experience. Please respond with the job title and company, the url, and the reasons "
              f"for suitability or otherwise. My resume is as follows:\n\n{resume_text}\n\nJobs:\n")
    for index, row in jobs_df.iterrows():
        prompt += f"{index + 1}. Job Title: {row['job_title']}, Company: {row['company_name']}, URL: {row['url']}, Description: {row['description']}\n"
    return prompt

# Function to get rankings from ChatGPT
def get_job_rankings(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who compares my resume to a list of jobs and provides a list from most to least suitable."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )
    return response.choices[0].message['content'].strip()


# Set up OpenAI API key
openai.api_key = os.environ['PATHFINDER_API']

# Paths to your files
csv_path = 'jobs.csv'

# Extract text from resume
resume_text = open('resume.txt', 'r').read()

# Read job listings from CSV
jobs_df = pd.read_csv(csv_path)

# Prepare the prompt for ChatGPT
prompt = prepare_prompt(resume_text, jobs_df)

# Get job rankings
rankings = get_job_rankings(prompt)

# Print the rankings
print("Job Suitability Rankings:")
print(rankings)
