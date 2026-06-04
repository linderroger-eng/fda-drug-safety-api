"""
FDA Drug & Safety API
Wraps openFDA public API into clean, developer-friendly endpoints
Free tier: 100 req/month | Pro: $9/1000 | Ultra: $29/10000 | Mega: $99/100000
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx, asyncio
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="FDA Drug & Safety API",
    description="Clean REST API for FDA drug labels, adverse events, recalls, and enforcement actions. No API key needed for free tier.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FDA_BASE = "https://api.fda.gov"

async def fda_get(path: str, params: dict) -> dict:
    """Make a request to openFDA API"""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.get(f"{FDA_BASE}{path}", params=params)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="No FDA records found for this query")
            raise HTTPException(status_code=502, detail=f"FDA API error: {e.response.status_code}")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"FDA API unavailable: {str(e)}")


@app.get("/", tags=["Info"])
async def root():
    return {
        "api": "FDA Drug & Safety API",
        "version": "1.0.0",
        "endpoints": ["/drug/search", "/drug/adverse-events", "/drug/label", "/device/recalls", "/enforcement", "/health"],
        "docs": "/docs",
        "source": "openFDA (public domain)",
        "rapidapi": "https://rapidapi.com"
    }


@app.get("/health", tags=["Info"])
async def health():
    """Health check"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{FDA_BASE}/drug/event.json?limit=1")
            fda_status = "up" if r.status_code == 200 else "degraded"
    except:
        fda_status = "down"
    return {
        "status": "healthy",
        "fda_upstream": fda_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/ping", tags=["Info"])
async def ping():
    return {"pong": True}


@app.get("/drug/search", tags=["Drugs"])
async def drug_search(
    name: str = Query(..., description="Brand or generic drug name (e.g. 'aspirin', 'tylenol', 'ozempic')"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (max 50)")
):
    """
    Search FDA drug database by brand or generic name.
    Returns drug info including manufacturer, active ingredients, NDC codes.
    """
    data = await fda_get("/drug/label.json", {
        "search": f"openfda.brand_name:{name}+openfda.generic_name:{name}",
        "limit": limit
    })
    results = []
    for r in data.get("results", []):
        openfda = r.get("openfda", {})
        results.append({
            "brand_name": openfda.get("brand_name", [None])[0],
            "generic_name": openfda.get("generic_name", [None])[0],
            "manufacturer": openfda.get("manufacturer_name", [None])[0],
            "product_type": openfda.get("product_type", [None])[0],
            "route": openfda.get("route", []),
            "ndc": openfda.get("product_ndc", []),
            "purpose": r.get("purpose", [None])[0],
            "warnings": r.get("warnings", [None])[0],
            "dosage": r.get("dosage_and_administration", [None])[0],
            "ingredients": openfda.get("substance_name", [])
        })
    return {
        "drug": name,
        "total_found": data.get("meta", {}).get("results", {}).get("total", 0),
        "results": results
    }


@app.get("/drug/adverse-events", tags=["Drugs"])
async def drug_adverse_events(
    name: str = Query(..., description="Drug name (brand or generic, e.g. 'ozempic', 'ibuprofen')"),
    serious: Optional[bool] = Query(None, description="Filter to serious adverse events only"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (max 50)")
):
    """
    Get FDA adverse event reports (FAERS) for a drug.
    Returns patient reactions, outcomes, and reporter info.
    """
    search = f"patient.drug.medicinalproduct:{name}"
    if serious:
        search += "+serious:1"

    data = await fda_get("/drug/event.json", {"search": search, "limit": limit})
    results = []
    for r in data.get("results", []):
        patient = r.get("patient", {})
        results.append({
            "report_id": r.get("safetyreportid"),
            "receive_date": r.get("receivedate"),
            "serious": r.get("serious") == "1",
            "serious_criteria": {
                "death": r.get("seriousnessdeath") == "1",
                "hospitalization": r.get("seriousnesshospitalization") == "1",
                "life_threatening": r.get("seriousnesslifethreatening") == "1",
                "disability": r.get("seriousnessdisabling") == "1",
            },
            "patient_age": patient.get("patientonsetage"),
            "patient_sex": {"1": "male", "2": "female"}.get(str(patient.get("patientsex", "")), "unknown"),
            "reactions": [rx.get("reactionmeddrapt") for rx in patient.get("reaction", [])],
            "drugs_taken": [d.get("medicinalproduct") for d in patient.get("drug", [])],
            "outcome": patient.get("patientdeath", {})
        })
    return {
        "drug": name,
        "total_reports": data.get("meta", {}).get("results", {}).get("total", 0),
        "results": results
    }


@app.get("/drug/label", tags=["Drugs"])
async def drug_label(
    name: str = Query(..., description="Brand or generic drug name"),
):
    """
    Get FDA-approved drug label (package insert) for a drug.
    Returns warnings, dosage, contraindications, and more.
    """
    data = await fda_get("/drug/label.json", {
        "search": f"openfda.brand_name:{name}",
        "limit": 1
    })
    if not data.get("results"):
        raise HTTPException(status_code=404, detail=f"No FDA label found for '{name}'")

    r = data["results"][0]
    openfda = r.get("openfda", {})
    return {
        "brand_name": openfda.get("brand_name", [None])[0],
        "generic_name": openfda.get("generic_name", [None])[0],
        "manufacturer": openfda.get("manufacturer_name", [None])[0],
        "warnings": r.get("warnings", [None])[0],
        "warnings_boxed": r.get("boxed_warning", [None])[0],
        "indications": r.get("indications_and_usage", [None])[0],
        "dosage": r.get("dosage_and_administration", [None])[0],
        "contraindications": r.get("contraindications", [None])[0],
        "adverse_reactions": r.get("adverse_reactions", [None])[0],
        "drug_interactions": r.get("drug_interactions", [None])[0],
        "pregnancy": r.get("pregnancy", [None])[0],
        "storage": r.get("storage_and_handling", [None])[0],
        "active_ingredients": openfda.get("substance_name", []),
    }


@app.get("/device/recalls", tags=["Medical Devices"])
async def device_recalls(
    keyword: Optional[str] = Query(None, description="Search keyword (e.g. 'insulin pump', 'pacemaker')"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (max 50)"),
    classification: Optional[str] = Query(None, description="Recall class: 'Class I', 'Class II', or 'Class III'")
):
    """
    Search FDA medical device recalls.
    Class I = most dangerous, Class III = least dangerous.
    """
    search_parts = []
    if keyword:
        search_parts.append(f"product_description:{keyword}")
    if classification:
        search_parts.append(f"classification:{classification.replace(' ', '+')}")

    params = {"limit": limit}
    if search_parts:
        params["search"] = "+".join(search_parts)

    data = await fda_get("/device/recall.json", params)
    results = []
    for r in data.get("results", []):
        results.append({
            "recall_number": r.get("recall_number"),
            "date_initiated": r.get("event_date_initiated"),
            "classification": r.get("classification"),
            "product_description": r.get("product_description"),
            "reason": r.get("reason_for_recall"),
            "firm": r.get("firm_fei_number"),
            "product_quantity": r.get("product_quantity"),
            "distribution": r.get("distribution_pattern"),
            "status": r.get("status")
        })
    return {
        "keyword": keyword,
        "total_found": data.get("meta", {}).get("results", {}).get("total", 0),
        "results": results
    }


@app.get("/enforcement", tags=["Enforcement"])
async def enforcement_actions(
    keyword: Optional[str] = Query(None, description="Search keyword (product, company, or reason)"),
    product_type: Optional[str] = Query(None, description="Filter by: 'Drugs', 'Devices', 'Food', 'Biologics'"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (max 50)")
):
    """
    Search FDA enforcement actions (recalls, withdrawals, alerts) across all product types.
    """
    search_parts = []
    if keyword:
        search_parts.append(f"reason_for_recall:{keyword}")
    if product_type:
        search_parts.append(f"product_type:{product_type}")

    params = {"limit": limit}
    if search_parts:
        params["search"] = "+".join(search_parts)

    data = await fda_get("/drug/enforcement.json", params)
    results = []
    for r in data.get("results", []):
        results.append({
            "recall_number": r.get("recall_number"),
            "recall_initiation_date": r.get("recall_initiation_date"),
            "classification": r.get("classification"),
            "product_description": r.get("product_description"),
            "reason": r.get("reason_for_recall"),
            "recalling_firm": r.get("recalling_firm"),
            "state": r.get("state"),
            "status": r.get("status"),
            "voluntary_mandated": r.get("voluntary_mandated"),
            "distribution_pattern": r.get("distribution_pattern")
        })
    return {
        "total_found": data.get("meta", {}).get("results", {}).get("total", 0),
        "results": results
    }
