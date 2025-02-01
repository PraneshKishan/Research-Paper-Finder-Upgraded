from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape research papers
def scrape_papers(search_query):
    search_query = search_query.replace(' ', '+')
    url = f"https://scholar.google.com/scholar?q={search_query}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    papers = []
    for result in soup.select('.gs_ri'):
        title_tag = result.select_one('.gs_rt')
        title = title_tag.text.strip() if title_tag else "No title available"
        link = title_tag.a['href'] if title_tag and title_tag.a else "No link available"
        
        abstract_tag = result.select_one('.gs_rs')
        abstract = abstract_tag.text.strip() if abstract_tag else "No abstract available"
        abstract = abstract.lstrip("…").strip()  # Remove leading ellipses
        
        papers.append({'title': title, 'abstract': abstract, 'link': link})
    
    return papers

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    search_query = data.get('query', '')
    
    if not search_query.strip():
        return jsonify({'error': 'Please enter a valid search query'}), 400
    
    papers = scrape_papers(search_query)
    return jsonify({'results': papers})

if __name__ == '__main__':
    app.run(debug=True)
