import streamlit as st
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
client = OpenAI(api_key = st.secrets["OPENAI"])

company_name = st.text_input("Company Name")


@st.cache_data
def perform_function(company_name, data):

    messages = [{"role": "system", "content": 'You are financial market analyzer, skilled in generating financial and economic analysis from news articles about a company. Your answers should be short but to the point (Detailed Analysis, Sentiment Analysis, Risk Assessment, Opportunity Identification)'},
                {"role": "user", "content": "Do Analysis for "+company_name+'\n\n'+data}]
    
    chat = client.chat.completions.create( 
            model="gpt-4-1106-preview", messages=messages)
    reply = chat.choices[0].message.content 

    return reply


@st.cache_data
def fetch_news(company_name):
    # Initialize the NewsApiClient with your API key
    newsapi = NewsApiClient(api_key=st.secrets['API'])

    date_a_month_ago = datetime.now() - timedelta(days=30)
    formatted_date = date_a_month_ago.strftime('%Y-%m-%d')
    
    # /v2/everything
    all_articles = newsapi.get_everything(q=company_name+" AND (earnings OR revenue OR stock OR market cap)",
                                          from_param=formatted_date,
                                          sort_by='relevancy',
                                          language='en',
                                          domains='businessinsider.com, markets.businessinsider.com')
    
    return all_articles

@st.cache_data
def get_data(url):
    response = requests.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')

        filtered_paragraphs = [paragraph.get_text().strip() for paragraph in paragraphs if len(paragraph.get_text().split()) >= 5]

        article_text = '\n'.join(filtered_paragraphs)

        return article_text[:5000]

button = st.button("Submit")
if company_name and button:

    st.markdown(f"### Financial report for {company_name}")
    prediction_container = st.empty()

    try:
        articles = fetch_news(company_name)
        source_text = ""
        news_text = ""
        
        if articles['status'] == 'ok':
            for article in articles['articles'][:5]:
                source_text+=(f"[**{article['title']}**]({article['url']})\n\n")
                news_text+=(f"Title: {article['title']}\n\n")

                news_text+=f"Content: {get_data(article['url'])}\n\n"
                source_text+=(f"{article['description']}\n\n")
        else:
            st.error("No articles found for the given company.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
    
    prediction_container.markdown(perform_function(company_name, news_text))
    st.expander("Source").markdown(source_text)

    

