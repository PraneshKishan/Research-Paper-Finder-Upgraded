import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Function to scrape research papers
def scrape_papers(search_query):
    search_query = search_query.replace(' ', '+')
    url = f"https://scholar.google.com/scholar?q={search_query}"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    papers = []
    for result in soup.select('.gs_ri'):
        title = result.select_one('.gs_rt').text.strip()
        link = result.select_one('.gs_rt a')['href'] if result.select_one('.gs_rt a') else "No link available"
        
        # Get full abstract without cutting
        abstract_element = result.select_one('.gs_rs')
        abstract = abstract_element.text.strip() if abstract_element else "No abstract available"
        
        # Ensure the abstract starts correctly by removing unnecessary characters
        abstract = abstract.lstrip("…").rstrip("…")

        # Extract authors & publication year
        meta_info = result.select_one('.gs_a').text if result.select_one('.gs_a') else "Unknown authors, Unknown year"
        meta_parts = meta_info.split(',')
        author = meta_parts[0].strip()  # First part is the author(s)
        year = meta_parts[-1].strip() if len(meta_parts) > 1 else "Unknown Year"  # Last part is likely the year

        papers.append({
            'title': title,
            'abstract': abstract,
            'link': link,
            'author': author,
            'year': year
        })

    return papers

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    if query:
        results = scrape_papers(query)
        return jsonify({'results': results})
    return jsonify({'results': []})

if __name__ == '__main__':
    app.run(debug=True)
