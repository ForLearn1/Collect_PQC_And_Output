# Collect_PQC_And_Output

**Post-Quantum Cryptography Article Collector (2016–2025)**

This repository provides a Python-based automated script for collecting metadata and bibliographic records of scientific articles related to Post-Quantum Cryptography (PQC) and hybrid key exchange mechanisms from multiple academic sources between 2016 and 2025.
The project enables reproducible research collection by combining APIs from arXiv, CrossRef, DBLP, IACR, Springer, and IEEE Xplore.
All requests are timestamped, logged, and the outputs are stored in structured formats (.json, .atom, .html).

**Objectives**

Systematic aggregation of research publications related to Post-Quantum Cryptography (PQC).

Analysis and comparison of publication trends across major academic repositories.

Export of metadata in structured, transparent, and machine-readable formats to facilitate further processing.

Reproducible data collection, ensuring that queries and temporal ranges can be consistently repeated for verification or longitudinal studies.

**Targeted Research Keywords**

The following key terms are automatically queried across all supported databases:

post-quantum cryptography

hybrid key exchange

PQC migration

hybrid KEM

TLS PQC

KEMTLS

**Collection Period**

The script collects publications between January 1, 2016 and December 31, 2025 (inclusive).

**Requirements**

Python 3.8+
Required libraries:
pip install requests beautifulsoup4

Optional (for extended sources):

Environment variables for private APIs
export SPRINGER_API_KEY="your_springer_key"
export IEEE_API_KEY="your_ieee_key"

**Sources and Query APIs**

| **Source**          | **Access Method**             | **Output Format** | **Notes**                                                    |
| ------------------- | ----------------------------- | ----------------- | ------------------------------------------------------------ |
| **arXiv**           | Open API                      | `.atom`           | Returns up to 100 results per batch.                         |
| **CrossRef**        | REST API                      | `.json`           | Main and most comprehensive metadata source.                 |
| **DBLP**            | JSON API                      | `.json`           | May yield zero results if API rate limits apply.             |
| **IACR ePrint**     | HTML scraping                 | `.html`           | Subject to `robots.txt` restrictions and access limitations. |
| **Springer Nature** | REST API *(API key required)* | `.json`           | Requires a valid `SPRINGER_API_KEY`.                         |
| **IEEE Xplore**     | REST API *(API key required)* | `.json`           | Requires a valid `IEEE_API_KEY`.                             |


**Output Files**

All results are saved under the collect_pqc_output/ directory:

| **File**                | **Description**                                            |
| ----------------------- | ---------------------------------------------------------- |
| `audit_log.txt`         | Contains detailed logs with timestamps and queried URLs.   |
| `arxiv_results.atom`    | Raw metadata retrieved directly from the arXiv API.        |
| `crossref_results.json` | Structured bibliographic metadata collected from CrossRef. |
| `dblp_results.json`     | Publication records extracted from the DBLP database.      |
| `iacr_search.html`      | Full HTML snapshot of the IACR search results page.        |
| `springer_results.json` | Springer metadata output (requires a valid API key).       |
| `ieee_results.json`     | IEEE Xplore metadata output (requires a valid API key).    |



🔍 Reproducibility

Each execution automatically logs the exact date and time of every query, records the full API endpoints used, and maintains consistent parameters and year ranges ensuring complete transparency and reproducibility of the data collection process.

🧱 Folder Structure
.
├── collect_pqc.py
├── collect_pqc_output/
│   ├── audit_log.txt
│   ├── arxiv_results.atom
│   ├── crossref_results.json
│   ├── dblp_results.json
│   ├── iacr_search.html
│   ├── springer_results.json
│   └── ieee_results.json
└── README.md

**Future Improvements**

Add automated deduplication and citation merging across sources.

Integrate visualization dashboards (e.g., publication trends by year).

Expand to additional repositories such as Scopus, Semantic Scholar, or HAL.

Support export in BibTeX and CSV for academic referencing.

🧑‍💻 **Author**

Abdoul Ahad FALL
Cryptography Engineer & Researcher
