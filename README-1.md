# Coforge PE Intelligence Platform — V2

A Streamlit account-intelligence workspace designed for Coforge's private-equity targeting and research workflow.

## What changed in V2

The original prototype has been expanded into a multi-source PE intelligence product covering **16 target firms**:

- CVC Capital Partners
- Apax Partners
- Permira (the search also recognises the `Pereira` typo/alias)
- Hg
- Bridgepoint
- TDR Capital
- Coller Capital
- TowerBrook Capital Partners
- Cinven
- KKR
- Blackstone
- Apollo Global Management
- Advent International Europe
- EQT
- Gresham House
- Maven Capital Partners

## Main workspaces

### 1. Command Center
A pre-meeting executive view of the selected PE account:
- account-priority score
- portfolio/investment count
- priority leadership count
- relevant technology hiring count
- technology-signal count
- company bio
- data-confidence score
- "Why now?" buying signals
- top Coforge AI opportunities
- latest account news

### 2. Portfolio
- Public official-site portfolio extraction where feasible
- Clear scope note so counts are not misrepresented across asset classes
- Search/filter by company, sector, region, status and fund
- Sector/region charts
- CSV export
- Portfolio-company quick research: bio + latest company news
- PitchBook CSV/XLSX/JSON upload override for exhaustive coverage

### 3. Leadership
- Scans official people/team directories
- Searchable full directory where public pagination can be discovered
- Coforge-relevance score for each person
- People ranked by potential buying influence (technology, AI/data, portfolio operations/value creation, senior sponsors)
- Click/select a person to show role, Coforge relevance and official-site biography
- Link back to the source profile
- CSV export

### 4. Hiring & Skills
- Scans configured public career pages when server-rendered roles are visible
- Accepts uploaded job exports for Workday/JavaScript-heavy sites
- Coforge-relevance scoring per role
- Skill extraction from job descriptions: AI/GenAI, Python, data engineering, Databricks, Snowflake, Azure/AWS/GCP, cloud native, cybersecurity, automation, architecture, Salesforce, ServiceNow and more
- Role inspection with source link
- Aggregate skill-demand chart

### 5. Technology Signals
- Detects technology themes across jobs plus recent public news/insights
- Separates job evidence from news evidence
- Evidence inspector for every detected technology
- Explicitly treats mentions as **signals**, not proof of enterprise-wide adoption

### 6. Newsroom
- Google News RSS
- Official website news/insight extraction where possible
- Uploaded/internal account research
- Automatic categorisation: AI & Technology, M&A / Deal, Fundraising, Portfolio, Leadership, Growth, Other
- Search/filter by signal type and source

### 7. Opportunity Lab
- Explainable account-priority score
- Score decomposition across AI/technology evidence, hiring, growth triggers, stakeholder coverage and portfolio scale
- Maps only the Coforge capability library currently loaded in `data/coforge_capabilities.json`
- Suggests the strongest buyer from the leadership evidence
- Exports a full account briefing in Markdown

### 8. AI Analyst
- Evidence-grounded account research copilot
- Can use a local Ollama model such as Gemma 3
- If Ollama is absent, the application uses a deterministic signal engine instead of failing
- System prompt explicitly prevents inventing people, companies, jobs, technologies or initiatives

### 9. Data Hub
- Accepts CSV, XLSX and JSON
- Portfolio, leadership, jobs and insight uploads
- Designed for PitchBook exports
- Session uploads override local files; local files override public extraction
- Persistent folder structure for reusable account data

## Data precedence

For portfolio, leadership and jobs:

1. Current Streamlit session upload
2. Local account file under `data/<firm_key>/`
3. Public official-site extraction

News/insights are merged from uploads + local data + Google News + official-site sources.

## Persistent data folders

Create folders such as:

```text
data/
  kkr/
    portfolio.xlsx
    leadership.csv
    jobs.csv
    insights.csv
  bridgepoint/
    portfolio.csv
    leadership.csv
    jobs.csv
    insights.csv
  coforge_capabilities.json
```

The app accepts `.json`, `.csv` or `.xlsx` for each account dataset. Templates are in `data/_templates/`.

## Run the app

### Windows
Double-click:

```text
run_app.bat
```

Or from a terminal:

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

### macOS / Linux

```bash
pip install -r requirements.txt
./run_app.sh
```

## Optional local AI

The app works without Ollama. To enable the local LLM analyst:

```bash
pip install ollama
ollama pull gemma3
ollama serve
```

Then use the **AI Analyst** page. The default model name is `gemma3` and can be changed in the UI.

## Public-source limitations

This application is deliberately conservative about public web data:

- PE firms publish different portfolio scopes; some list current holdings, some historical investments, some multiple asset classes, and some only selected case studies.
- Public people directories can be JavaScript-rendered or paginated. The app attempts to discover public pagination on the Leadership page, but an uploaded verified directory remains the strongest option for exhaustive coverage.
- Career pages frequently use Workday, Greenhouse or other JavaScript-heavy systems. When the public scanner cannot see roles, upload a jobs export instead.
- Public websites change. All source failures are handled gracefully so one broken scraper does not crash the product.

## Files

- `app.py` — Streamlit UI
- `pe_core.py` — firm configuration, data adapters, scrapers, scoring and AI logic
- `data/coforge_capabilities.json` — editable Coforge capability model
- `data/_templates/` — upload templates
- `requirements.txt` — dependencies
- `run_app.bat` / `run_app.sh` — launchers
