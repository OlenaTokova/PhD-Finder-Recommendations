from flask import Flask, request, jsonify, render_template, send_file
import requests
import xml.etree.ElementTree as ET
from flask_cors import CORS
from datetime import datetime
from fpdf import FPDF
import os

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Function to scrape GitHub
def scrape_github(interest, min_stars=10, num_results=5):
    url = f"https://api.github.com/search/repositories?q={interest}+stars:>{min_stars}&sort=stars&per_page={num_results}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json().get("items", [])[:num_results]
        
        print(f"✅ GitHub API Response: {len(repos)} results found.")
        
        return [
            {
                "field": "GitHub",
                "topic": repo.get("name", "Unknown"),
                "link": repo.get("html_url", "#"),
                "stars": repo.get("stargazers_count", 0),
                "rating": min(int(repo.get("stargazers_count", 0) / 1000), 5)
            }
            for repo in repos
        ]
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub API Error: {e}")
        return []

# Function to scrape arXiv
def scrape_arxiv(interest, start_year=2019, num_results=5):
    url = f"http://export.arxiv.org/api/query?search_query=all:{interest}&start=0&max_results={num_results}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        results = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            published_date = entry.find("{http://www.w3.org/2005/Atom}published").text
            pub_year = int(published_date[:4]) if published_date else None
            
            if pub_year and pub_year >= start_year:
                results.append({
                    "field": "arXiv",
                    "topic": entry.find("{http://www.w3.org/2005/Atom}title").text,
                    "link": entry.find("{http://www.w3.org/2005/Atom}id").text,
                    "year": pub_year,
                    "rating": 5 if pub_year >= start_year else 3
                })

        print(f"✅ arXiv API Response: {len(results)} results found.")
        return results
    except requests.exceptions.RequestException as e:
        print(f"❌ arXiv API Error: {e}")
        return []

# Function to fetch CrossRef data
def fetch_crossref(interest, num_results=5):
    url = f"https://api.crossref.org/works?query={interest}&rows={num_results}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        papers = response.json().get("message", {}).get("items", [])[:num_results]
        
        print(f"✅ CrossRef API Response: {len(papers)} results found.")
        
        return [
            {
                "field": "CrossRef",
                "topic": paper.get("title", ["Unknown"])[0],
                "link": paper.get("URL", "#"),
                "year": paper.get("published-print", {}).get("date-parts", [[None]])[0][0],
                "rating": 5 if "DOI" in paper else 3
            }
            for paper in papers
        ]
    except requests.exceptions.RequestException as e:
        print(f"❌ CrossRef API Error: {e}")
        return []

# Function to fetch OpenAlex data
def fetch_openalex(interest, num_results=5):
    url = f"https://api.openalex.org/works?search={interest}&per_page={num_results}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        papers = response.json().get("results", [])[:num_results]

        print(f"✅ OpenAlex API Response: {len(papers)} results found.")

        results = []
        for paper in papers:
            title = paper.get("title", "Unknown")
            year = paper.get("publication_year", "N/A")
            link = paper.get("id", "#")
            citations = paper.get("cited_by_count", 0)

            rating = (
                5 if citations > 1000 else
                4 if citations > 500 else
                3 if citations > 100 else
                2 if citations > 10 else 1
            )

            results.append({
                "field": "OpenAlex",
                "topic": title,
                "link": link,
                "year": year,
                "rating": rating
            })

        return results

    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAlex API Error: {e}")
        return []

# Function to generate PDF
def generate_pdf(results):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, "PhD Research Recommendations", ln=True, align="C")
    pdf.ln(10)

    for result in results:
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, f"{result['field']}: {result['topic']}", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, f"Link: {result['link']}")
        pdf.cell(0, 8, f"Rating: {'⭐' * result['rating']}", ln=True)
        pdf.ln(5)

    pdf_filename = "PhD_Recommendations.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    
    if not data or "interest" not in data or "sites" not in data:
        return jsonify({"error": "Invalid input. Please provide 'interest', 'sites', and optional filters."}), 400

    interest = data["interest"]
    sites = data["sites"]
    num_results = int(data.get("num_results", 5))

    results = []
    
    if "github" in sites:
        results.extend(scrape_github(interest, num_results=num_results))

    if "arxiv" in sites:
        results.extend(scrape_arxiv(interest, num_results=num_results))

    if "crossref" in sites:
        results.extend(fetch_crossref(interest, num_results))

    if "openalex" in sites:
        results.extend(fetch_openalex(interest, num_results))

    if not results:
        return jsonify([{"field": "None", "topic": "No recommendations found.", "link": "#"}])

    print(f"📊 Final Results: {len(results)} entries")
    return jsonify(results)

import os

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf_route():
    data = request.get_json()
    results = data.get("results", [])

    if not results:
        return jsonify({"error": "No results available for PDF generation"}), 400

    pdf_filename = generate_pdf(results)

    if os.path.exists(pdf_filename):
        print(f"📄 PDF successfully created: {pdf_filename}")  # Debugging
        return send_file(pdf_filename, as_attachment=True, download_name=pdf_filename, mimetype="application/pdf")
    else:
        print("❌ Error: PDF file was not created")
        return jsonify({"error": "PDF generation failed"}), 500

def generate_pdf(results):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, "PhD Research Recommendations", ln=True, align="C")
    pdf.ln(10)

    for result in results:
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, f"{result['field']}: {result['topic']}", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, f"Link: {result['link']}")
        pdf.cell(0, 8, f"Rating: {'⭐' * result['rating']}", ln=True)
        pdf.ln(5)

    pdf_filename = "PhD_Recommendations.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

if __name__ == "__main__":
    app.run(debug=True)
