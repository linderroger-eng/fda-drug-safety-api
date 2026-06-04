# 💊 FDA Drug & Safety API

![Build](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
[![RapidAPI](https://img.shields.io/badge/RapidAPI-Subscribe-blue?style=flat-square&logo=rapidapi)](https://rapidapi.com)

> Clean REST API for FDA drug data — adverse events, drug labels, device recalls. Query by name, not FDA syntax.

**Live API:** `https://fda-drug-safety-api.onrender.com` · **[Interactive Docs](https://fda-drug-safety-api.onrender.com/docs)** · **[RapidAPI Listing](https://rapidapi.com)**

---

## ✨ Features

- 🔍 **Search drugs by name** — query by brand or generic name (e.g. `ozempic`, `ibuprofen`) with no FDA query syntax required
- ⚠️ **Adverse event reports** — pull real FAERS data including patient reactions, outcomes, and serious criteria (death, hospitalization, disability)
- 📋 **Full drug labels** — access FDA-approved package inserts with warnings, dosage, contraindications, and drug interactions
- 🏥 **Device recalls & enforcement** — search medical device recalls by keyword or classification, and track FDA enforcement actions across all product categories

---

## 🚀 Quick Start

No API key required for the free tier. Start querying immediately:

**1. Health check**
```bash
curl https://fda-drug-safety-api.onrender.com/health
```

**2. Search for a drug**
```bash
curl "https://fda-drug-safety-api.onrender.com/drug/search?name=metformin&limit=5"
```

**3. Adverse events for Ozempic**
```bash
curl "https://fda-drug-safety-api.onrender.com/drug/adverse-events?name=ozempic&serious=true&limit=10"
```

**4. Device recalls for insulin pumps**
```bash
curl "https://fda-drug-safety-api.onrender.com/device/recalls?keyword=insulin+pump&classification=Class+I"
```

---

## 📡 Endpoints

**Base URL:** `https://fda-drug-safety-api.onrender.com`

- **GET `/drug/search`**
  - Params: `name` *(required)*, `limit` (1–50, default 10)
  - Returns brand/generic info, manufacturer, NDC codes, active ingredients

- **GET `/drug/adverse-events`**
  - Params: `name` *(required)*, `serious` (true/false), `limit` (1–50, default 10)
  - Returns FAERS adverse event reports with patient reactions and outcomes

- **GET `/drug/label`**
  - Params: `name` *(required)*
  - Returns full FDA-approved package insert: warnings, dosage, contraindications, interactions

- **GET `/device/recalls`**
  - Params: `keyword`, `limit` (1–50), `classification` (Class I / Class II / Class III)
  - Returns device recall records with reason, firm, and distribution details

- **GET `/enforcement`**
  - Params: `keyword`, `product_type` (Drugs / Devices / Food / Biologics), `limit` (1–50)
  - Returns FDA enforcement actions (recalls, withdrawals, alerts) across all product types

> Full interactive documentation with request/response schemas: [`/docs`](https://fda-drug-safety-api.onrender.com/docs)

---

## 🐍 Python Example — Adverse Event Monitor

```python
import requests

BASE = "https://fda-drug-safety-api.onrender.com"

def monitor_adverse_events(drug_name: str, serious_only: bool = True):
    """Fetch and summarize adverse event reports for a given drug."""
    resp = requests.get(f"{BASE}/drug/adverse-events", params={
        "name": drug_name,
        "serious": serious_only,
        "limit": 20
    })
    resp.raise_for_status()
    data = resp.json()

    print(f"\n🔬 Adverse Events for {drug_name.upper()}")
    print(f"Total reports on file: {data['total_reports']:,}")
    for event in data["results"][:5]:
        reactions = ", ".join(event["reactions"] or [])
        print(f"  [{event['receive_date']}] {event['patient_sex']}, age {event['patient_age']} — {reactions}")

monitor_adverse_events("ozempic")
```

---

## 💰 Pricing

| Tier | Price | Requests / Month |
|------|-------|-----------------|
| **BASIC** | Free | 100 |
| **PRO** | $9 | 1,000 |
| **ULTRA** | $29 | 10,000 |
| **MEGA** | $99 | 100,000 |

Subscribe on [RapidAPI](https://rapidapi.com) — no credit card required for BASIC.

---

## 📊 Data Source

All data is sourced from **[openFDA](https://open.fda.gov/)**, the official open data initiative by the U.S. Food & Drug Administration.

- ✅ Public domain — no licensing restrictions
- ✅ Updated continuously by FDA
- ✅ Covers drugs, devices, food, and biologics
- 🔗 Source: [https://open.fda.gov](https://open.fda.gov) · [FDA.gov](https://www.fda.gov)

---

## 📄 License

```
MIT License

Copyright (c) 2024 FDA Drug & Safety API

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">Built on <a href="https://open.fda.gov">openFDA</a> public data · Powered by <a href="https://fastapi.tiangolo.com">FastAPI</a></p>
