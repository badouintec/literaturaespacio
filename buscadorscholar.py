import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy

# Cargar el modelo de lenguaje de spaCy en español
nlp = spacy.load("es_core_news_md")

def get_google_scholar_results(query, num_results=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = query.replace(' ', '+')
    url = f"https://scholar.google.com/scholar?q={query}&hl=en&num={num_results}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for item in soup.find_all('div', class_='gs_ri'):
            title = item.find('h3').text
            link = item.find('a')['href'] if item.find('a') else ''
            snippet = item.find('div', class_='gs_rs').text
            results.append({'title': title, 'link': link, 'snippet': snippet})
        
        return pd.DataFrame(results)
    else:
        print("Error fetching results")
        return None

def extract_keywords(text):
    doc = nlp(text)
    keywords = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
    return keywords

def categorize_article(keywords, categories):
    for keyword in keywords:
        for category in categories:
            if category.lower() in keyword.lower():
                return category
    return 'Otros'

# Categorías de ejemplo
categories = ['Landsat', 'MODIS', 'Centro de Investigación X', 'Estado Y']

query = "percepción remota México"
results_df = get_google_scholar_results(query, num_results=50)

if results_df is not None:
    results_df['keywords'] = results_df['snippet'].apply(extract_keywords)
    results_df['category'] = results_df['keywords'].apply(lambda x: categorize_article(x, categories))
    results_df.to_csv('google_scholar_results_with_categories.csv', index=False)
    print(results_df)
else:
    print("No se encontraron resultados")