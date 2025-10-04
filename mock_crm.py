from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Optional
from datetime import datetime
import csv
import os
from pathlib import Path

app = FastAPI(title="Mock CRM")

# CSV file paths
LEADS_CSV = "crm_leads.csv"
VISITS_CSV = "crm_visits.csv"
UPDATES_CSV = "crm_updates.csv"

# Initialize CSV files with headers if they don't exist
def initialize_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    if not os.path.exists(LEADS_CSV):
        with open(LEADS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['lead_id', 'name', 'phone', 'city', 'source', 'status', 'created_at'])
        print(f"✓ Created {LEADS_CSV}")

    if not os.path.exists(VISITS_CSV):
        with open(VISITS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['visit_id', 'lead_id', 'visit_time', 'notes', 'status', 'created_at'])
        print(f"✓ Created {VISITS_CSV}")

    if not os.path.exists(UPDATES_CSV):
        with open(UPDATES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['lead_id', 'old_status', 'new_status', 'notes', 'updated_at'])
        print(f"✓ Created {UPDATES_CSV}")

# Initialize CSV files on startup
initialize_csv_files()

class LeadCreate(BaseModel):
    name: str
    phone: str
    city: str
    source: Optional[str] = None
    

class VisitCreate(BaseModel):
    lead_id: str
    visit_time: datetime
    notes: Optional[str] = None

class LeadStatusUpdate(BaseModel):
    status: str = Field(pattern="^(NEW|IN_PROGRESS|FOLLOW_UP|WON|LOST)$")
    notes: Optional[str] = None

# In-memory stores
LEADS = {}
VISITS = {}

@app.post("/crm/leads")
def create_lead(payload: LeadCreate):
    lead_id = str(uuid4())
    created_at = datetime.now().isoformat()

    lead_data = {
        **payload.dict(),
        "lead_id": lead_id,
        "status": "NEW",
        "created_at": created_at
    }
    LEADS[lead_id] = lead_data

    # Print to terminal
    print("\n" + "="*60)
    print("📝 NEW LEAD CREATED")
    print("="*60)
    print(f"Lead ID    : {lead_id}")
    print(f"Name       : {payload.name}")
    print(f"Phone      : {payload.phone}")
    print(f"City       : {payload.city}")
    print(f"Source     : {payload.source or 'N/A'}")
    print(f"Status     : NEW")
    print(f"Created At : {created_at}")
    print("="*60 + "\n")

    # Save to CSV
    with open(LEADS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            lead_id,
            payload.name,
            payload.phone,
            payload.city,
            payload.source or '',
            "NEW",
            created_at
        ])

    return {"lead_id": lead_id, "status": "NEW"}

@app.post("/crm/visits")
def create_visit(payload: VisitCreate):
    if payload.lead_id not in LEADS:
        print(f"\n❌ ERROR: Lead {payload.lead_id} not found!\n")
        raise HTTPException(status_code=404, detail="Lead not found")

    visit_id = str(uuid4())
    created_at = datetime.now().isoformat()

    visit_data = {
        **payload.dict(),
        "visit_id": visit_id,
        "status": "SCHEDULED",
        "created_at": created_at
    }
    VISITS[visit_id] = visit_data

    # Get lead info for display
    lead = LEADS[payload.lead_id]

    # Print to terminal
    print("\n" + "="*60)
    print("📅 VISIT SCHEDULED")
    print("="*60)
    print(f"Visit ID   : {visit_id}")
    print(f"Lead ID    : {payload.lead_id}")
    print(f"Lead Name  : {lead.get('name', 'N/A')}")
    print(f"Visit Time : {payload.visit_time}")
    print(f"Notes      : {payload.notes or 'N/A'}")
    print(f"Status     : SCHEDULED")
    print(f"Created At : {created_at}")
    print("="*60 + "\n")

    # Save to CSV
    with open(VISITS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            visit_id,
            payload.lead_id,
            str(payload.visit_time),
            payload.notes or '',
            "SCHEDULED",
            created_at
        ])

    return {"visit_id": visit_id, "status": "SCHEDULED"}

@app.post("/crm/leads/{lead_id}/status")
def update_lead_status(lead_id: str, payload: LeadStatusUpdate):
    if lead_id not in LEADS:
        print(f"\n❌ ERROR: Lead {lead_id} not found!\n")
        raise HTTPException(status_code=404, detail="Lead not found")

    # Get old status for logging
    old_status = LEADS[lead_id].get("status", "UNKNOWN")
    updated_at = datetime.now().isoformat()

    # Update lead
    LEADS[lead_id]["status"] = payload.status
    if payload.notes:
        LEADS[lead_id]["notes"] = payload.notes

    # Get lead info for display
    lead = LEADS[lead_id]

    # Print to terminal
    print("\n" + "="*60)
    print("🔄 LEAD STATUS UPDATED")
    print("="*60)
    print(f"Lead ID      : {lead_id}")
    print(f"Lead Name    : {lead.get('name', 'N/A')}")
    print(f"Old Status   : {old_status}")
    print(f"New Status   : {payload.status}")
    print(f"Notes        : {payload.notes or 'N/A'}")
    print(f"Updated At   : {updated_at}")
    print("="*60 + "\n")

    # Save to CSV
    with open(UPDATES_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            lead_id,
            old_status,
            payload.status,
            payload.notes or '',
            updated_at
        ])

    return {"lead_id": lead_id, "status": payload.status}

@app.get("/crm/leads")
def list_leads():
    """List all leads (for debugging)"""
    return {"leads": list(LEADS.values())}

@app.get("/crm/visits")
def list_visits():
    """List all visits (for debugging)"""
    return {"visits": list(VISITS.values())}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  🚀 MOCK CRM SERVER STARTING")
    print("="*60)
    print(f"  Server URL   : http://localhost:8001")
    print(f"  Leads CSV    : {LEADS_CSV}")
    print(f"  Visits CSV   : {VISITS_CSV}")
    print(f"  Updates CSV  : {UPDATES_CSV}")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)
