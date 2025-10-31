import requests
import time
import json
import os
from urllib.parse import quote_plus
from datetime import datetime
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import bibtexparser  # ✅ for local BibTeX merging

# === General configuration ===
OUTDIR = 'collect_pqc_output'
os.makedirs(OUTDIR, exist_ok=True)
AUDIT_LOG = os.path.join(OUTDIR, 'audit_log.txt')

TERMS = [
    "post-quantum cryptography",
    "hybrid key exchange",
    "PQC migration",
    "hybrid KEM",
    "TLS PQC",
    "KEMTLS",
]

HEADERS = {
    'User-Agent': 'CollectPQCBot/1.0 (+mailto:your-email@example.com)',
    'Accept': 'application/json, application/atom+xml, application/xml, text/html;q=0.9'
}

RATE_LIMIT_SECONDS = 1.0
START_YEAR = 2016
END_YEAR = 2025
MAX_CROSSREF_RESULTS = 400  # ✅ limit to 400 papers

def log(msg):
    ts = datetime.utcnow().isoformat() + 'Z'
    with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{ts}] {msg}\n')

log('Collection script started')

counts = {
    'arxiv': 0,
    'crossref': 0,
    'dblp': 0,
    'iacr': 0,
    'springer': 0
}

# --------------------------
# === arXiv ===
# --------------------------
arxiv_query = quote_plus(' OR '.join(TERMS))
arxiv_url = f'https://export.arxiv.org/api/query?search_query=all:{arxiv_query}&start=0&max_results=100'
print(f"Sending request to arXiv: {arxiv_url}")

r = requests.get(arxiv_url, headers=HEADERS, timeout=30)
if r.status_code == 200:
    with open(os.path.join(OUTDIR, 'arxiv_results.atom'), 'wb') as f:
        f.write(r.content)
    tree = ET.fromstring(r.content)
    counts['arxiv'] = len(tree.findall('{http://www.w3.org/2005/Atom}entry'))
time.sleep(RATE_LIMIT_SECONDS)

# --------------------------
# === CrossRef ===
# --------------------------
crossref_results = []
crossref_rows = 200
crossref_offset = 0

while True:
    crossref_query = quote_plus(' '.join(TERMS))
    crossref_url = (
        f'https://api.crossref.org/works?query.bibliographic={crossref_query}'
        f'&filter=from-pub-date:{START_YEAR}-01-01,until-pub-date:{END_YEAR}-12-31'
        f'&rows={crossref_rows}&offset={crossref_offset}'
    )

    print(f"Sending request to CrossRef: {crossref_url}")

    r = requests.get(crossref_url, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        log(f'CrossRef request failed with status {r.status_code}')
        break

    data = r.json()
    items = data.get('message', {}).get('items', [])
    if not items:
        break

    crossref_results.extend(items)
    counts['crossref'] += len(items)

    if len(crossref_results) >= MAX_CROSSREF_RESULTS:
        crossref_results = crossref_results[:MAX_CROSSREF_RESULTS]
        break

    crossref_offset += crossref_rows
    time.sleep(RATE_LIMIT_SECONDS)

with open(os.path.join(OUTDIR, 'crossref_results.json'), 'w', encoding='utf-8') as f:
    json.dump(crossref_results, f, indent=2)

# --------------------------
# === DBLP ===
# --------------------------
dblp_query = quote_plus(' '.join(TERMS))
dblp_url = f'https://dblp.org/search/publ/api?q={dblp_query}&format=json&h=200'
print(f"Sending request to DBLP: {dblp_url}")

r = requests.get(dblp_url, headers=HEADERS, timeout=30)
if r.status_code == 200:
    data = r.json()
    hits = data.get('result', {}).get('hits', {}).get('hit', [])
    if isinstance(hits, dict):
        hits = [hits]
    counts['dblp'] = len(hits)
    with open(os.path.join(OUTDIR, 'dblp_results.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
time.sleep(RATE_LIMIT_SECONDS)

# --------------------------
# === IACR ===
# --------------------------
HEADERS_IACR = HEADERS.copy()
HEADERS_IACR['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

iacr_query = quote_plus('post-quantum cryptography')
iacr_url = f'https://eprint.iacr.org/search?search={iacr_query}'
print(f"Sending request to IACR: {iacr_url}")

r = requests.get(iacr_url, headers=HEADERS_IACR, timeout=30)
if r.status_code == 200:
    with open(os.path.join(OUTDIR, 'iacr_search.html'), 'w', encoding='utf-8') as f:
        f.write(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    counts['iacr'] = len(soup.find_all('a', href=True, class_='list-title'))
time.sleep(RATE_LIMIT_SECONDS)

# --------------------------
# === Springer ===
# --------------------------
SPRINGER_API_KEY = os.environ.get('SPRINGER_API_KEY')
if SPRINGER_API_KEY:
    springer_query = quote_plus(' '.join(TERMS))
    springer_url = (
        f'http://api.springernature.com/metadata/json?q={springer_query}'
        f'&api_key={SPRINGER_API_KEY}&p=100'
    )
    print(f"Sending request to Springer: {springer_url}")
    r = requests.get(springer_url, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        counts['springer'] = len(data.get('records', []))
        with open(os.path.join(OUTDIR, 'springer_results.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
else:
    log('SPRINGER_API_KEY not set — skipping Springer')

time.sleep(RATE_LIMIT_SECONDS)

# --------------------------
# === Merge with local BibTeX library ===
# --------------------------
BIB_FILE = 'export.bib'
BIB_OUTPUT = os.path.join(OUTDIR, 'DB_results.json')

if os.path.exists(BIB_FILE):
    with open(BIB_FILE, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    bib_entries = []
    for entry in bib_database.entries:
        bib_entries.append({
            'title': entry.get('title', 'N/A'),
            'author': entry.get('author', 'N/A'),
            'year': entry.get('year', 'N/A'),
            'doi': entry.get('doi', 'N/A'),
            'url': entry.get('url', 'N/A'),
            'journal': entry.get('journal', entry.get('booktitle', 'N/A')),
            'source': 'local_bib'
        })

    crossref_file = os.path.join(OUTDIR, 'crossref_results.json')
    if os.path.exists(crossref_file):
        with open(crossref_file, encoding='utf-8') as f:
            crossref_results = json.load(f)
    else:
        crossref_results = []

    DB_results = crossref_results + bib_entries

    with open(BIB_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(DB_results, f, indent=2)

else:
    log('No local BibTeX file found — skipping merge')

# --------------------------
# === End of script ===
# --------------------------
print("End of requests...")
