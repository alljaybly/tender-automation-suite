import os
import json
import asyncio
import traceback
import shutil
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from pathlib import Path
import urllib.parse

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException, Body, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message
from starlette.requests import HTTPConnection

from env_loader import load_env_file

# Load .env before importing local modules that may consume environment variables.
BASE_DIR = Path(__file__).resolve().parent
load_env_file(BASE_DIR / ".env")

from pdf_processor import DocumentExtractor, PDFProcessor
from web_search import WebSearcher
from debate_council import DebateCouncil, ModelConfig
from pricing_engine import PricingEngine
from document_generator import DocumentGenerator

from backend.intelligence.pricing_intelligence import PricingIntelligence
from backend.intelligence.win_score_v2 import WinScoreV2

app = FastAPI(title="Automated Tender Response System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories relative to this file so the app works from any shell cwd.
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
WORKSPACE = BASE_DIR / "workspace"
BACKEND_WORKSPACE = BASE_DIR / "backend" / "workspace"
TENDER_DB = BACKEND_WORKSPACE / "tender_database"
TENDERS_JSON = TENDER_DB / "tenders.json"
INSIGHTS_JSON = TENDER_DB / "pricing_insights.json"

UPLOADS = WORKSPACE / "uploads"
OUTPUTS = WORKSPACE / "outputs"
HISTORY = WORKSPACE / "history"
MERGED = WORKSPACE / "merged"

for dir_path in [STATIC_DIR, TEMPLATES_DIR, WORKSPACE, UPLOADS, OUTPUTS, HISTORY, MERGED, TENDER_DB]:
    dir_path.mkdir(parents=True, exist_ok=True)

# --- SaaS Configuration ---
USAGE_FILE = WORKSPACE / "usage.json"
API_KEYS = {"PRO-TRIAL-2026": "pro", "DEV-KEY-999": "pro"}
TIERS = {
    "free": {"limit": 1, "features": ["basic_pricing"]},
    "pro": {"limit": float('inf'), "features": ["advanced_scoring", "benchmarking", "unlimited"]}
}

def get_usage_data() -> Dict:
    if not USAGE_FILE.exists():
        return {}
    try:
        with open(USAGE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_usage_data(data: Dict):
    with open(USAGE_FILE, 'w') as f:
        json.dump(data, f)

def get_client_tier(conn: HTTPConnection) -> str:
    # Check API Key first
    api_key = conn.headers.get("X-API-Key")
    if api_key in API_KEYS:
        return API_KEYS[api_key]
    
    # Check Session (Cookie)
    session_tier = conn.cookies.get("tier", "free")
    return session_tier

def check_usage_limit(conn: HTTPConnection):
    tier = get_client_tier(conn)
    if tier == "pro":
        return True
        
    client_ip = conn.client.host
    today = datetime.now().strftime("%Y-%m-%d")
    
    usage = get_usage_data()
    if today not in usage:
        usage[today] = {}
        
    current_count = usage[today].get(client_ip, 0)
    limit = TIERS["free"]["limit"]
    
    if current_count >= limit:
        return False
    return True

def increment_usage(conn: HTTPConnection):
    tier = get_client_tier(conn)
    if tier == "pro":
        return
        
    client_ip = conn.client.host
    today = datetime.now().strftime("%Y-%m-%d")
    
    usage = get_usage_data()
    if today not in usage:
        usage[today] = {}
        
    usage[today][client_ip] = usage[today].get(client_ip, 0) + 1
    save_usage_data(usage)

def update_tender_database(tender_data: dict, pricing: dict):
    """Update tenders.json with newly processed data for global intelligence."""
    try:
        if not TENDERS_JSON.exists():
            tenders = []
        else:
            with open(TENDERS_JSON, "r") as f:
                tenders = json.load(f)
        
        # Check if already exists by reference
        ref = tender_data.get("reference")
        if not ref:
            return

        new_entry = {
            "reference": ref,
            "title": tender_data.get("title", f"Tender {ref}"),
            "sector": tender_data.get("sector", "general"),
            "province": tender_data.get("location", "Unknown"),
            "closing_date": tender_data.get("closing_date", ""),
            "estimated_value": pricing.get("total_contract_value", tender_data.get("estimated_value", 0)),
            "duration": tender_data.get("duration_months", 12),
            "scraped_at": datetime.now().isoformat(),
            "source": "pdf_upload"
        }

        # Update or append
        updated = False
        for i, t in enumerate(tenders):
            if t.get("reference") == ref:
                tenders[i] = new_entry
                updated = True
                break
        
        if not updated:
            tenders.append(new_entry)

        with open(TENDERS_JSON, "w") as f:
            json.dump(tenders, f, indent=2)
            
        # Trigger pricing intelligence update
        pi = PricingIntelligence(str(TENDERS_JSON), str(INSIGHTS_JSON))
        pi.analyze()
            
    except Exception as e:
        print(f"Failed to update tender database: {e}")

# --- End SaaS Configuration ---

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # If no session cookie, show landing page
    if not request.cookies.get("session_active"):
        return templates.TemplateResponse("landing.html", {"request": request})
    
    tier = get_client_tier(request)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "tier": tier,
        "is_pro": tier == "pro"
    })

@app.post("/login")
async def login(response: Response):
    # Mock login sets a session cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_active", value="true")
    response.set_cookie(key="tier", value="free")
    return response

@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_active")
    response.delete_cookie("tier")
    return response

@app.post("/api/upgrade")
async def upgrade():
    return {
        "status": "pending",
        "message": "Upgrade coming soon! Our payment gateway is currently being integrated."
    }

@app.get("/api/pricing-insights")
async def get_pricing_insights():
    pi = PricingIntelligence(str(TENDERS_JSON), str(INSIGHTS_JSON))
    insights = pi.analyze()
    return insights

@app.post("/api/win-score-v2")
async def calculate_win_score_v2(data: dict = Body(...)):
    ws = WinScoreV2(str(INSIGHTS_JSON))
    result = ws.calculate(
        price=data.get("price", 0),
        sector=data.get("sector", "general"),
        province=data.get("province", "Unknown"),
        duration=data.get("duration", 12),
        workforce=data.get("workforce", 1)
    )
    return result

@app.get("/api/models")
async def list_models():
    return {"models": [
        {"id": "llama-3.3-70b-versatile", "source": "groq-cloud"},
        {"id": "mixtral-8x7b-32768", "source": "groq-cloud"},
        {"id": "gemma-2-9b-it", "source": "groq-cloud"}
    ]}

@app.post("/api/upload")
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    # Check usage limit
    if not check_usage_limit(request):
        raise HTTPException(403, "Daily limit reached for free tier (1 tender/day). Please upgrade to Pro for unlimited access.")
    
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.rtf', '.png', '.jpg', '.jpeg'}
    uploaded_files = []
    extracted_texts = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for file in files:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            continue
            
        safe_name = "".join(c if c.isalnum() or c in '._-' else '_' for c in file.filename)
        filename = f"{timestamp}_{safe_name}"
        file_path = UPLOADS / filename
        
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        uploaded_files.append(str(file_path))
        
        try:
            if file_ext in ['.docx', '.doc']:
                try:
                    from docx import Document
                    import io
                    doc = Document(io.BytesIO(content))
                    text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
                    extracted_texts.append(f"--- Document: {file.filename} ---\n{text}\n")
                except Exception as e:
                    print(f"DOCX extraction error: {e}")
                    import zipfile
                    try:
                        with zipfile.ZipFile(io.BytesIO(content)) as zf:
                            xml_content = zf.read('word/document.xml')
                            text = re.sub(r'<[^>]+>', '', xml_content.decode('utf-8', errors='ignore'))
                            extracted_texts.append(f"--- Document: {file.filename} ---\n{text}\n")
                    except:
                        pass
            elif file_ext in ['.txt', '.rtf']:
                text = content.decode('utf-8', errors='ignore')
                extracted_texts.append(f"--- Document: {file.filename} ---\n{text}\n")
        except Exception as e:
            print(f"Extraction error for {file.filename}: {e}")
    
    if not uploaded_files:
        raise HTTPException(400, "PDF too large or unclear – please try a smaller, clearer file")
    
    if len(extracted_texts) > 1 or any(Path(f).suffix.lower() in ['.docx', '.doc', '.txt'] for f in uploaded_files):
        merged_filename = f"{timestamp}_MERGED_PACKAGE.txt"
        merged_path = MERGED / merged_filename
        
        with open(merged_path, 'w', encoding='utf-8') as f:
            f.write(f"TENDER DOCUMENT PACKAGE\nGenerated: {datetime.now().isoformat()}\nOriginal Files: {len(uploaded_files)}\n{'='*60}\n\n")
            for i, text in enumerate(extracted_texts, 1):
                f.write(f"\n\n{'='*60}\nSECTION {i}\n{'='*60}\n{text}")
        
        return {
            "filename": merged_filename,
            "path": str(merged_path),
            "original_files": uploaded_files,
            "count": len(uploaded_files),
            "type": "merged_package"
        }
    
    return {
        "filename": Path(uploaded_files[0]).name,
        "path": uploaded_files[0],
        "original_files": uploaded_files,
        "count": 1,
        "type": "single"
    }

@app.get("/api/tender-comparison")
async def get_tender_comparison(
    tender_type: str = Query(...),
    location: str = Query(...),
    user_monthly: float = Query(None),
    user_contract: float = Query(None)
):
    history_files = list(HISTORY.glob("*.json"))
    similar_tenders = []

    for hist_file in history_files:
        try:
            with open(hist_file) as f:
                data = json.load(f)
                tender_data = data.get('tender_data', data)
                if tender_data.get('tender_type') == tender_type or tender_data.get('sector') == tender_type:
                    total_value = data.get('pricing', {}).get('total_contract_value', 0)
                    duration = tender_data.get('duration_months', data.get('pricing', {}).get('duration_months', 12))
                    if total_value == 0:
                        total_value = data.get('total_value', 0)
                    similar_tenders.append({
                        'total_value': total_value,
                        'duration_months': duration,
                        'monthly': total_value / max(duration, 1) if duration > 0 else 0
                    })
        except:
            continue

    if similar_tenders:
        total_monthly = sum(t.get('monthly', 0) for t in similar_tenders)
        avg_monthly = total_monthly / len(similar_tenders)
        avg_contract = sum(t.get('total_value', 0) for t in similar_tenders) / len(similar_tenders)

        avg_values = {
            'avg_monthly': avg_monthly,
            'avg_contract': avg_contract,
            'count': len(similar_tenders),
            'range_low': min(t.get('total_value', 0) for t in similar_tenders),
            'range_high': max(t.get('total_value', 0) for t in similar_tenders)
        }

        comparison_result = {
            'similar_tenders_found': len(similar_tenders),
            'averages': avg_values,
            'recommendation': 'Compare against CIDB published rates for verification'
        }

        if user_monthly is not None and user_monthly > 0:
            difference_percent = ((user_monthly - avg_monthly) / avg_monthly) * 100 if avg_monthly > 0 else 0

            if difference_percent > 15:
                position = "Overpriced"
                advice = f"Your monthly rate is {difference_percent:.1f}% above market average. Consider reducing margins or optimizing costs to improve competitiveness."
            elif difference_percent < -10:
                position = "Underpriced"
                advice = f"Your monthly rate is {abs(difference_percent):.1f}% below market average. You may be leaving money on the table – consider a modest increase."
            else:
                position = "Competitive"
                advice = f"Your pricing is within {abs(difference_percent):.1f}% of market average – well positioned for tender submission."

            comparison_result['avg_monthly'] = round(avg_monthly, 2)
            comparison_result['user_monthly'] = round(user_monthly, 2)
            comparison_result['difference_percent'] = round(difference_percent, 2)
            comparison_result['position'] = position
            comparison_result['advice'] = advice

        return comparison_result
    else:
        return {
            'similar_tenders_found': 0,
            'averages': {
                'avg_monthly': 0,
                'avg_contract': 0,
                'count': 0,
                'range_low': 0,
                'range_high': 0,
                'note': 'No historical data. Research market rates independently.'
            },
            'recommendation': 'Compare against CIDB published rates for verification'
        }

@app.post("/api/finalize-duration")
async def fix_duration_calculation(current_data: dict = Body(...)):
    tender_data = current_data.get('tender_data', {})
    raw_text = tender_data.get('raw_text', '')
    
    month_match = re.search(r'(\d{1,2})\s*months?', raw_text, re.IGNORECASE)
    if month_match:
        correct_months = int(month_match.group(1))
    else:
        if '12 month' in raw_text.lower():
            correct_months = 12
        elif '24 month' in raw_text.lower():
            correct_months = 24
        else:
            correct_months = 12
    
    if correct_months != tender_data.get('duration_months', 12):
        pricing = current_data.get('pricing', {})
        monthly = pricing.get('total_monthly', 0)
        
        pricing['duration_months'] = correct_months
        pricing['total_contract_value'] = monthly * correct_months
        pricing['recalculated'] = True
        pricing['original_duration'] = tender_data.get('duration_months', 12)
        
        return {
            'corrected': True,
            'correct_duration': correct_months,
            'corrected_pricing': pricing,
            'message': f'Duration corrected from {tender_data.get("duration_months", 12)} to {correct_months} months'
        }
    
    return {
        'corrected': False,
        'duration': correct_months,
        'message': 'Duration verified correct'
    }

@app.websocket("/ws/process")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        data = await websocket.receive_json()
        await process_tender(data, websocket)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"step": "error", "message": str(e)})
        except:
            pass
    finally:
        manager.disconnect(websocket)

async def send_safe(websocket, message: dict):
    try:
        await websocket.send_json(message)
        return True
    except:
        return False

async def process_tender(data: dict, websocket: WebSocket):
    filename = data.get("filename")
    
    if (MERGED / filename).exists():
        file_path = MERGED / filename
    elif (UPLOADS / filename).exists():
        file_path = UPLOADS / filename
    else:
        await send_safe(websocket, {"step": "error", "message": "No text could be extracted – try a different PDF", "progress": 0})
        return
    
    try:
        await send_safe(websocket, {"step": "start", "message": "Starting processing...", "progress": 5})
        
        await send_safe(websocket, {"step": "pdf", "message": "Extracting documents...", "progress": 10})
        
        try:
            extractor = DocumentExtractor()
            tender_data = await extractor.extract(str(file_path))
            
            if tender_data.get('workforce', {}).get('total_workers', 0) == 0:
                area = tender_data.get('scope', {}).get('area_sqm', 1000)
                estimated_workers = max(2, area // 400)
                tender_data['workforce']['total_workers'] = estimated_workers
                tender_data['workforce']['unskilled_workers'] = estimated_workers
                # Also set backward-compat fields
                tender_data['requirements']['workers'] = estimated_workers
                print(f"[CRITICAL] Estimated workers: {estimated_workers}")
            
            await send_safe(websocket, {"step": "extracted", "data": tender_data, "progress": 25})
            
            # Generate initial executive summary and scope description if missing
            if not tender_data.get('executive_summary'):
                sector = tender_data.get('tender_type', 'services')
                ref = tender_data.get('reference', 'TBC')
                location = tender_data.get('location', 'the specified site')
                duration = tender_data.get('duration_months', 12)
                tender_data['executive_summary'] = f"This proposal outlines our comprehensive approach to providing professional {sector} services for {ref}. With our extensive experience and commitment to excellence, we aim to deliver high-quality results at {location} over the {duration}-month contract period."
            
            if not tender_data.get('scope_description'):
                area = tender_data.get('scope', {}).get('area_sqm', 1000)
                workers = tender_data.get('workforce', {}).get('total_workers', 5)
                tender_data['scope_description'] = f"The scope of work involves the maintenance and service delivery across approximately {area} sqm. Our proposed solution includes a dedicated team of {workers} personnel equipped with industry-standard tools and materials to ensure all requirements are met efficiently."
        except Exception as e:
            print(f"Extraction failed: {e}")
            traceback.print_exc()
            tender_data = {
                'reference': f"TENDER-{datetime.now().strftime('%Y%m%d')}",
                'sector': 'cleaning',
                'tender_type': 'cleaning',
                'sub_type': 'standard',
                'duration_months': 12,
                'duration': {'value': 12, 'unit': 'months', 'months': 12, 'display': '12 months (default)', 'estimated': True},
                'location': 'South Africa',
                'workforce': {'total_workers': 5, 'unskilled_workers': 5, 'supervisors': 1, 'skilled_workers': 0},
                'scope': {'area_sqm': 1000, 'is_emergency': False, 'is_breakdown': False},
                'requirements': {'workers': 5, 'supervisors': 1, 'area_sqm': 1000, 'shifts': 1, 'shifts_per_day': 1, 'hours_per_day': 8, 'working_days_week': 5, 'total_staff': 6, 'equipment_required': [], 'materials_required': []},
                'client': {'type': 'Public Entity', 'name': 'Client'},
                'raw_text': ''
            }
            await send_safe(websocket, {"step": "extracted", "data": tender_data, "warning": "Used default values", "progress": 25})
        
        await send_safe(websocket, {"step": "search", "message": "Searching industry rates...", "progress": 30})
        
        try:
            searcher = WebSearcher()
            rates = await asyncio.wait_for(searcher.search_all_rates(tender_data), timeout=30)
            await send_safe(websocket, {"step": "rates", "rates": rates, "progress": 50})
        except:
            rates = {}
            await send_safe(websocket, {"step": "rates", "rates": {}, "progress": 50})
        
        await send_safe(websocket, {"step": "debate", "message": "Starting Cloud Debate...", "progress": 55})
        
        try:
            council = DebateCouncil(None, websocket)
            debate_result = await asyncio.wait_for(council.deliberate(tender_data, rates, []), timeout=300)
            await send_safe(websocket, {"step": "debate_complete", "result": debate_result, "progress": 85})
        except asyncio.TimeoutError:
            await send_safe(websocket, {"step": "error", "message": "Processing took too long – refresh and try again", "progress": 0})
            return
        except Exception as e:
            print(f"Debate error: {e}")
            traceback.print_exc()
            await send_safe(websocket, {"step": "error", "message": "Something went wrong. Please refresh the page and try again.", "progress": 0})
            return
        
        await send_safe(websocket, {"step": "pricing", "message": "Finalizing...", "progress": 90})
        
        # Increment usage for free tier
        increment_usage(websocket)
        
        try:
            engine = PricingEngine()
            pricing = engine.calculate(tender_data, rates, debate_result)
            # Update global tender database for intelligence
            update_tender_database(tender_data, pricing)
        except Exception as e:
            print(f"Pricing Error: {e}")
            base = debate_result.get("final_price", 50000)
            duration = tender_data.get("duration_months", 12)
            pricing = {
                "total_monthly": base,
                "total_contract_value": base * duration,
                "labour_cost": base * 0.7,
                "equipment_cost": base * 0.1,
                "materials_cost": base * 0.1,
                "overheads": base * 0.15,
                "profit": base * 0.15,
                "vat": base * 0.15
            }
        
        # --- ADD WIN SCORE V2 INTELLIGENCE ---
        await send_safe(websocket, {"step": "intelligence", "message": "Calculating Win Score V2...", "progress": 92})
        try:
            ws_v2 = WinScoreV2(str(INSIGHTS_JSON))
            win_score_data = ws_v2.calculate(
                price=pricing.get("total_contract_value", 0),
                sector=tender_data.get("sector", "general"),
                province=tender_data.get("location", "Unknown"),
                duration=tender_data.get("duration_months", 12),
                workforce=tender_data.get("workforce", {}).get("total_workers", 1)
            )
        except Exception as e:
            print(f"Win Score V2 Error: {e}")
            win_score_data = {"win_probability": "N/A", "risk_level": "Unknown", "issues": [], "suggestions": []}
        
        await send_safe(websocket, {"step": "generating", "message": "Creating documents...", "progress": 95})
        
        try:
            doc_gen = DocumentGenerator()
            safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in tender_data.get("reference", "unknown"))[:50] or "tender"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            word_filename = f"tender_{safe_ref}_{timestamp}.docx"
            excel_filename = f"pricing_{safe_ref}_{timestamp}.xlsx"
            
            word_path = OUTPUTS / word_filename
            excel_path = OUTPUTS / excel_filename
            
            await doc_gen.generate_word(tender_data, pricing, str(word_path))
            await doc_gen.generate_excel(tender_data, pricing, str(excel_path))
            
            # Save to history with full data for analytics
            hist = {
                "date": datetime.now().isoformat(),
                "timestamp": datetime.now().isoformat(),
                "reference": tender_data.get("reference", "unknown"),
                "type": tender_data.get("tender_type", "Unknown"),
                "tender_type": tender_data.get("tender_type", "Unknown"),
                "sector": tender_data.get("sector", tender_data.get("tender_type", "Unknown")),
                "total_value": pricing.get("total_contract_value", 0),
                "duration_months": tender_data.get("duration_months", 12),
                "confidence": debate_result.get("confidence", 0),
                "win_score": win_score_data,
                "tender_data": tender_data,
                "pricing": pricing,
                "debate_result": debate_result,
                "documents": {"word": word_filename, "excel": excel_filename}
            }
            
            with open(HISTORY / f"{timestamp}_{safe_ref}.json", "w") as f:
                json.dump(hist, f, indent=2, default=str)
            
            await send_safe(websocket, {
                "step": "complete",
                "progress": 100,
                "tender_data": tender_data,
                "pricing": pricing,
                "debate_result": debate_result,
                "win_score": win_score_data,
                "documents": {"word": word_filename, "excel": excel_filename}
            })
            
        except Exception as e:
            print(f"Doc generation error: {e}")
            traceback.print_exc()
            await send_safe(websocket, {"step": "error", "message": "Something went wrong. Please refresh the page and try again.", "progress": 95})
            
    except Exception as e:
        print(f"Critical Error: {e}")
        traceback.print_exc()
        await send_safe(websocket, {"step": "error", "message": "Something went wrong. Please refresh the page and try again.", "progress": 0})

@app.post("/api/reprice")
async def reprice_tender(payload: dict = Body(...)):
    pricing = payload.get("pricing")
    mode = payload.get("mode")
    
    if not pricing or not mode:
        raise HTTPException(400, "Missing pricing or mode")
    
    try:
        engine = PricingEngine()
        new_pricing = engine.reprice(pricing, mode)
        return new_pricing
    except Exception as e:
        print(f"Reprice error: {e}")
        raise HTTPException(500, f"Error recalculating price: {str(e)}")

@app.post("/api/edit-draft")
async def edit_draft(payload: dict = Body(...)):
    tender_data = payload.get("tender_data")
    pricing = payload.get("pricing")
    regenerate = payload.get("regenerate", False)
    
    if not tender_data or not pricing:
        raise HTTPException(400, "Missing tender_data or pricing")
    
    # Update files if regeneration requested
    word_filename = None
    excel_filename = None
    
    if regenerate:
        try:
            doc_gen = DocumentGenerator()
            safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in tender_data.get("reference", "unknown"))[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            word_filename = f"tender_{safe_ref}_{timestamp}.docx"
            excel_filename = f"pricing_{safe_ref}_{timestamp}.xlsx"
            
            word_path = OUTPUTS / word_filename
            excel_path = OUTPUTS / excel_filename
            
            await doc_gen.generate_word(tender_data, pricing, str(word_path))
            await doc_gen.generate_excel(tender_data, pricing, str(excel_path))
        except Exception as e:
            print(f"Regeneration error: {e}")
            # Continue even if regeneration fails, but log it
    
    # Save to history
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in tender_data.get("reference", "unknown"))[:50]
        
        hist = {
            "date": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat(),
            "reference": tender_data.get("reference", "unknown"),
            "type": tender_data.get("tender_type", "Unknown"),
            "tender_type": tender_data.get("tender_type", "Unknown"),
            "sector": tender_data.get("sector", tender_data.get("tender_type", "Unknown")),
            "total_value": pricing.get("total_contract_value", 0),
            "duration_months": tender_data.get("duration_months", 12),
            "confidence": payload.get("debate_result", {}).get("confidence", 0.8),
            "tender_data": tender_data,
            "pricing": pricing,
            "debate_result": payload.get("debate_result", {}),
            "documents": {
                "word": word_filename or payload.get("documents", {}).get("word"),
                "excel": excel_filename or payload.get("documents", {}).get("excel")
            }
        }
        
        with open(HISTORY / f"{timestamp}_{safe_ref}.json", "w") as f:
            json.dump(hist, f, indent=2, default=str)
            
        return {
            "success": True, 
            "message": "Draft saved successfully", 
            "documents": hist["documents"]
        }
    except Exception as e:
        print(f"Save draft error: {e}")
        raise HTTPException(500, f"Error saving draft: {str(e)}")

@app.get("/api/history")
async def get_history(
    search: str = Query(None),
    tender_type: str = Query(None),
    sort_by: str = Query("date"),
    sort_order: str = Query("desc")
):
    entries = []
    for file in sorted(HISTORY.glob("*.json"), reverse=True):
        try:
            with open(file) as f:
                data = json.load(f)
            data['id'] = file.stem
            data['filename'] = file.name
            entries.append(data)
        except:
            continue
    
    if search:
        search_lower = search.lower()
        filtered = []
        for entry in entries:
            tender_data = entry.get('tender_data', entry)
            ref = tender_data.get('reference', '').lower()
            sector = tender_data.get('sector', tender_data.get('tender_type', '')).lower()
            location = tender_data.get('location', '').lower()
            if search_lower in ref or search_lower in sector or search_lower in location:
                filtered.append(entry)
        entries = filtered
    
    if tender_type:
        filtered = []
        for entry in entries:
            tender_data = entry.get('tender_data', entry)
            t_type = tender_data.get('tender_type', tender_data.get('sector', '')).lower()
            if tender_type.lower() in t_type:
                filtered.append(entry)
        entries = filtered
    
    reverse_sort = sort_order.lower() == "desc"
    if sort_by == "date":
        entries.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')), reverse=reverse_sort)
    elif sort_by == "value":
        entries.sort(key=lambda x: x.get('pricing', {}).get('total_contract_value', x.get('total_value', 0)), reverse=reverse_sort)
    elif sort_by == "reference":
        entries.sort(key=lambda x: x.get('tender_data', {}).get('reference', '').lower(), reverse=reverse_sort)
    
    return entries

@app.get("/api/tender/{tender_id}")
async def get_tender(tender_id: str):
    tender_path = HISTORY / f"{tender_id}.json"
    if tender_path.exists():
        with open(tender_path) as f:
            return json.load(f)
    
    matches = list(HISTORY.glob(f"*{tender_id}*.json"))
    if matches:
        with open(matches[0]) as f:
            return json.load(f)
    
    raise HTTPException(404, "Tender not found")

@app.post("/api/duplicate")
async def duplicate_tender(
    tender_id: str = Body(...),
    new_reference: str = Body(None)
):
    tender_path = HISTORY / f"{tender_id}.json"
    source_data = None
    
    if tender_path.exists():
        with open(tender_path) as f:
            source_data = json.load(f)
    else:
        matches = list(HISTORY.glob(f"*{tender_id}*.json"))
        if matches:
            with open(matches[0]) as f:
                source_data = json.load(f)
    
    if not source_data:
        raise HTTPException(404, "Tender not found")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_ref = new_reference or f"COPY_{source_data.get('tender_data', {}).get('reference', 'tender')}"
    safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in new_ref)[:50]
    filename = f"{timestamp}_{safe_ref}.json"
    
    source_data['timestamp'] = datetime.now().isoformat()
    source_data['original_id'] = tender_id
    if 'tender_data' in source_data:
        source_data['tender_data']['reference'] = new_ref
    
    new_path = HISTORY / filename
    with open(new_path, 'w') as f:
        json.dump(source_data, f, indent=2, default=str)
    
    return {"success": True, "new_id": filename.replace('.json', ''), "reference": new_ref}

@app.get("/api/analytics")
async def get_analytics():
    entries = []
    for file in HISTORY.glob("*.json"):
        try:
            with open(file) as f:
                entries.append(json.load(f))
        except:
            continue
    
    total_tenders = len(entries)
    contract_values = []
    sector_counts = {}
    
    for entry in entries:
        pricing = entry.get('pricing', {})
        value = pricing.get('total_contract_value', entry.get('total_value', 0))
        if value > 0:
            contract_values.append(value)
        
        tender_data = entry.get('tender_data', entry)
        # Check multiple possible keys for sector/type
        sector = (
            tender_data.get('sector') or 
            tender_data.get('tender_type') or 
            entry.get('type') or 
            entry.get('tender_type') or
            'Unknown'
        )
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    avg_contract = sum(contract_values) / len(contract_values) if contract_values else 0
    most_common_sector = max(sector_counts, key=sector_counts.get) if sector_counts else "N/A"
    
    return {
        "total_tenders_processed": total_tenders,
        "avg_contract_value": round(avg_contract, 2),
        "most_common_sector": most_common_sector,
        "sector_breakdown": sector_counts,
        "total_value_processed": sum(contract_values)
    }

@app.get("/api/download/word/{filename}")
async def download_word(filename: str):
    try:
        decoded_filename = urllib.parse.unquote(filename)
        file_path = OUTPUTS / decoded_filename
        
        if not file_path.exists():
            files = sorted(OUTPUTS.glob("tender_*.docx"), key=lambda x: x.stat().st_mtime, reverse=True)
            if files:
                file_path = files[0]
            else:
                raise HTTPException(404, "File not found")
        
        return FileResponse(file_path, filename=file_path.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        raise HTTPException(500, f"Download error: {str(e)}")

@app.get("/api/download/excel/{filename}")
async def download_excel(filename: str):
    try:
        decoded_filename = urllib.parse.unquote(filename)
        file_path = OUTPUTS / decoded_filename
        
        if not file_path.exists():
            files = sorted(OUTPUTS.glob("pricing_*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)
            if files:
                file_path = files[0]
            else:
                raise HTTPException(404, "File not found")
        
        return FileResponse(file_path, filename=file_path.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        raise HTTPException(500, f"Download error: {str(e)}")

@app.get("/api/download/zip")
async def download_zip(word: str, excel: str):
    import io
    import zipfile
    from fastapi.responses import StreamingResponse
    try:
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
            word_path = OUTPUTS / urllib.parse.unquote(word)
            excel_path = OUTPUTS / urllib.parse.unquote(excel)
            if word_path.exists():
                temp_zip.write(word_path, arcname=word_path.name)
            if excel_path.exists():
                temp_zip.write(excel_path, arcname=excel_path.name)
                
        zip_io.seek(0)
        return StreamingResponse(
            iter([zip_io.getvalue()]), 
            media_type="application/x-zip-compressed", 
            headers={"Content-Disposition": f"attachment; filename=tender_package.zip"}
        )
    except Exception as e:
        raise HTTPException(500, f"Zip error: {str(e)}")

@app.get("/api/files/list")
async def list_generated_files():
    files = []
    for f in OUTPUTS.iterdir():
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
    return {"files": files}

@app.post("/api/edit-draft")
async def edit_draft(
    tender_data: dict = Body(...),
    pricing: dict = Body(...),
    executive_summary: str = Body(None),
    scope_description: str = Body(None),
    pricing_notes: str = Body(None)
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in tender_data.get("reference", "draft"))[:50] or "draft"
    filename = f"{timestamp}_{safe_ref}_edited.json"
    file_path = HISTORY / filename

    edited_data = {
        "date": datetime.now().isoformat(),
        "edited": True,
        "original_reference": tender_data.get("reference"),
        "tender_data": tender_data,
        "pricing": pricing,
        "edits": {
            "executive_summary": executive_summary,
            "scope_description": scope_description,
            "pricing_notes": pricing_notes
        },
        "branding": {
            "company_name": BRANDING_CONFIG.get("company_name"),
            "logo_path": BRANDING_CONFIG.get("logo_path")
        }
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(edited_data, f, indent=2, default=str)

    return {
        "success": True,
        "filename": filename,
        "path": str(file_path),
        "message": "Draft saved successfully"
    }

@app.post("/api/regenerate")
async def regenerate_documents(
    tender_data: dict = Body(...),
    pricing: dict = Body(...),
    executive_summary: str = Body(None),
    scope_description: str = Body(None),
    pricing_notes: str = Body(None)
):
    try:
        if executive_summary:
            tender_data["executive_summary"] = executive_summary
        if scope_description:
            tender_data["scope_description"] = scope_description
        if pricing_notes:
            pricing["notes"] = pricing_notes

        doc_gen = DocumentGenerator()
        doc_gen.set_branding(
            company_name=BRANDING_CONFIG.get("company_name"),
            logo_path=BRANDING_CONFIG.get("logo_path")
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_ref = "".join(c if c.isalnum() or c in "-_" else "_" for c in tender_data.get("reference", "tender"))[:50] or "tender"
        
        word_filename = f"tender_response_{safe_ref}_{timestamp}.docx"
        excel_filename = f"pricing_breakdown_{safe_ref}_{timestamp}.xlsx"
        
        word_path = OUTPUTS / word_filename
        excel_path = OUTPUTS / excel_filename
        
        await doc_gen.generate_word(tender_data, pricing, str(word_path))
        # Assuming pricing engine or similar has a method for excel, or DocumentGenerator handles it
        if hasattr(doc_gen, 'generate_excel'):
            await doc_gen.generate_excel(tender_data, pricing, str(excel_path))
        
        return {
            "success": True,
            "documents": {
                "word": word_filename,
                "excel": excel_filename if hasattr(doc_gen, 'generate_excel') else None
            },
            "message": "Documents regenerated successfully"
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"Regeneration error: {str(e)}")

@app.get("/api/win-score")
async def get_win_score(
    tender_type: str = Query(...),
    price: float = Query(...),
    duration_months: int = Query(...),
    workers: int = Query(...),
    area_sqm: int = Query(0),
    historical_avg: float = Query(None)
):
    issues = []
    suggestions = []
    score = 70

    if historical_avg and historical_avg > 0:
        price_ratio = price / historical_avg
        if price_ratio > 1.3:
            issues.append(f"Price is {((price_ratio - 1) * 100):.0f}% above historical average – may reduce competitiveness")
            score -= 25
            suggestions.append("Consider reducing margin or optimizing workforce costs")
        elif price_ratio < 0.7:
            issues.append(f"Price is {((1 - price_ratio) * 100):.0f}% below historical average – may be underpriced")
            score -= 15
            suggestions.append("Review costs to ensure sustainability")
        else:
            score += 10

    workers_per_sqm = workers / max(area_sqm, 1) if area_sqm > 0 else 0
    if tender_type == "cleaning":
        if workers_per_sqm > 0.015:
            issues.append("High workforce density may appear unrealistic to evaluators")
            score -= 10
            suggestions.append("Review worker-to-area ratio for cleaning tenders")
        elif workers_per_sqm < 0.003:
            issues.append("Low workforce density may raise quality concerns")
            score -= 5
    elif tender_type in ["construction", "security"]:
        if workers < 3:
            issues.append("Small workforce may not match contract scope")
            score -= 10
            suggestions.append("Ensure workforce matches project requirements")

    if duration_months > 36:
        issues.append("Contract duration exceeds 3 years – may face renewal challenges")
        score -= 10
        suggestions.append("Consider break clauses for long-term contracts")
    elif duration_months < 1:
        issues.append("Very short duration may not allow proper service delivery")
        score -= 5

    required_fields = {
        "reference": "reference",
        "tender_type": "tender_type",
        "duration_months": "duration_months",
        "workers": "workers",
        "scope": "area_sqm"
    }
    missing = []
    if not tender_type or tender_type == "Unknown": missing.append("tender_type")
    if not duration_months: missing.append("duration_months")
    if not workers: missing.append("workers")
    if not area_sqm and tender_type == "cleaning": missing.append("area_sqm")

    if missing:
        issues.append(f"Incomplete data: {', '.join(missing)}")
        score -= 15
        suggestions.append("Ensure all tender requirement fields are correctly extracted for better evaluation")

    score = max(0, min(100, score))

    if score >= 75:
        risk_level = "Low"
    elif score >= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    if not issues:
        issues.append("No major issues detected")

    return {
        "win_probability": score,
        "risk_level": risk_level,
        "issues": issues,
        "suggestions": suggestions
    }

@app.get("/api/compliance-checklist")
async def get_compliance_checklist(tender_type: str = Query(...)):
    checklists = {
        "cleaning": {
            "required_documents": [
                "Tax clearance certificate",
                "CSD registration (Central Supplier Database)",
                "B-BBEE affidavit or certificate",
                "Company profile",
                "Relevant experience letters",
                "Health and safety policy",
                "Environmental policy"
            ],
            "notes": [
                "B-BBEE level 1-4 preferred for government tenders",
                "Tax clearance must be valid (within 12 months)",
                "CSD registration is mandatory for all government suppliers"
            ]
        },
        "security": {
            "required_documents": [
                "PSIRA registration (Private Security Industry Regulatory Authority)",
                "Tax clearance certificate",
                "CSD registration",
                "B-BBEE certificate",
                "Company profile with experience",
                "Arms import/export permits (if applicable)",
                "Training certifications for personnel"
            ],
            "notes": [
                "PSIRA registration is legally required for security services",
                "Security cleared personnel may be required",
                "B-BBEE scoring can significantly impact selection"
            ]
        },
        "construction": {
            "required_documents": [
                "CIDB registration",
                "Tax clearance certificate",
                "CSD registration",
                "B-BBEE certificate",
                "Company profile",
                "Project portfolio",
                "Health and safety plan",
                "Environmental impact assessment"
            ],
            "notes": [
                "CIDB grading must match contract value",
                "Letter of good standing from Workmen's Compensation",
                "Public liability insurance required"
            ]
        }
    }

    base_docs = [
        "Tax clearance certificate",
        "CSD registration",
        "B-BBEE certificate",
        "Company profile",
        "Bank rating letter"
    ]

    checklist = checklists.get(tender_type.lower(), {})
    required = checklist.get("required_documents", base_docs)
    notes = checklist.get("notes", ["Ensure all documents are current and valid"])

    history_files = list(HISTORY.glob("*.json"))
    submitted_docs = set()
    for hist_file in history_files[-10:]:
        try:
            with open(hist_file) as f:
                data = json.load(f)
                if data.get("type") == tender_type:
                    submitted_docs.add("Previous tender submission reference")
                    break
        except:
            continue

    missing = [doc for doc in required if doc not in submitted_docs]

    return {
        "tender_type": tender_type,
        "required_documents": required,
        "missing": missing,
        "notes": notes
    }

@app.post("/api/demo")
async def generate_demo_tender(tender_type: str = Query("cleaning")):
    demo_texts = {
        "cleaning": """
TENDER REFERENCE: CLEAN-2026-DEMO
TITLE: Provision of Cleaning Services for 12 Months
LOCATION: Pretoria Main Office
SCOPE OF WORK:
- Provide daily cleaning services for 1000 sqm office space.
- Require 5 unskilled cleaners and 1 supervisor.
- Provide all cleaning equipment and materials.
- Duration of contract: 12 months.
""",
        "security": """
TENDER REFERENCE: SEC-2026-DEMO
TITLE: Provision of Security Services for 12 Months
LOCATION: Johannesburg CBD Office Park
SCOPE OF WORK:
- Provide 24/7 security services for office complex.
- Require 8 security officers and 2 supervisors.
- CCTV monitoring and access control responsibilities.
- Duration of contract: 12 months.
""",
        "construction": """
TENDER REFERENCE: CON-2026-DEMO
TITLE: Office Renovation and Refurbishment
LOCATION: Cape Town Industrial Area
SCOPE OF WORK:
- Renovate 500 sqm office space including partitioning.
- Electrical rewiring and lighting installation.
- Plumbing upgrades and bathroom refurbishment.
- Duration of contract: 3 months.
"""
    }

    demo_text = demo_texts.get(tender_type.lower(), demo_texts["cleaning"])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_demo_{tender_type}.txt"
    file_path = UPLOADS / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(demo_text)

    return {
        "filename": filename,
        "path": str(file_path),
        "original_files": [str(file_path)],
        "count": 1,
        "type": "single",
        "tender_type": tender_type
    }

@app.post("/api/reprice")
async def reprice_quote(
    pricing: dict = Body(...),
    mode: str = Body(...)
):
    valid_modes = ["optimize_win", "maximize_profit", "reduce_margin"]
    if mode not in valid_modes:
        raise HTTPException(400, f"Invalid mode. Must be one of: {', '.join(valid_modes)}")

    engine = PricingEngine()
    repriced = engine.reprice(pricing, mode)

    return {
        "success": True,
        "original": {
            "total_monthly": pricing.get("total_monthly"),
            "total_contract_value": pricing.get("total_contract_value"),
            "profit": pricing.get("profit"),
            "overheads": pricing.get("overheads")
        },
        "repriced": {
            "total_monthly": repriced.get("total_monthly"),
            "total_contract_value": repriced.get("total_contract_value"),
            "profit": repriced.get("profit"),
            "overheads": repriced.get("overheads")
        },
        "savings": {
            "monthly": round(pricing.get("total_monthly", 0) - repriced.get("total_monthly", 0), 2),
            "contract": round(pricing.get("total_contract_value", 0) - repriced.get("total_contract_value", 0), 2)
        },
        "mode_description": repriced.get("reprice_description")
    }

@app.post("/api/clauses")
async def extract_clauses(payload: dict = Body(...)):
    raw_text = payload.get("raw_text", "")
    penalties = []
    deadlines = []
    compliance = []

    penalty_patterns = [
        r'penalty\s*(?:of|shall\s+be)?\s*([\d.,\s]+%?|R\s*[\d,]+)',
        r' liquidated\s*(?:and\s*)?damages?\s*(?:of|equal\s+to)?\s*([\d.,\s]+%?|R\s*[\d,]+)',
        r'non[- ]?performance\s*(?:penalty|damages?)?\s*(?:of|shall\s+be)?\s*([\d.,\s]+%?|R\s*[\d,]+)',
        r'breach\s*(?:of\s*contract)?\s*(?:penalty|damages?)?\s*(?:of)?\s*([\d.,\s]+%?|R\s*[\d,]+)',
        r'default\s*(?:penalty)?\s*(?:of)?\s*([\d.,\s]+%?|R\s*[\d,]+)'
    ]
    for pattern in penalty_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        for match in matches:
            penalty_text = match.strip() if isinstance(match, str) else ' '.join(match).strip()
            if penalty_text and penalty_text not in penalties:
                penalties.append(penalty_text)

    deadline_patterns = [
        r'(?:within|within\s+a\s*period\s*of|not\s+later\s+than)\s*(\d+)\s*(?:days?|business\s+days?|calendar\s+days?|weeks?|months?)',
        r'deadline\s*(?:of|is)?\s*(\d+)\s*(?:days?|business\s+days?|calendar\s+days?|weeks?|months?)',
        r'delivery\s*(?:within|time\s*frame|period)?\s*(\d+)\s*(?:days?|business\s+days?|calendar\s+days?|weeks?|months?)',
        r'(?:submit|submission)\s*(?:by|no\s+later\s+than)?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'commencement\s*date[^\d]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    ]
    for pattern in deadline_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        for match in matches:
            deadline_text = match.strip() if isinstance(match, str) else ' '.join(match).strip()
            if deadline_text and deadline_text not in deadlines:
                deadlines.append(deadline_text)

    compliance_keywords = [
        'cidb registration', 'tax clearance', 'csd registration', 'b-bbee',
        'bbbee', 'good standing', 'occupational health', 'safety', 'ema',
        'environmental', 'labour law', 'employment equity', 'skills development',
        'preferential procurement', 'local content', 'sector specific',
        'grade required', 'classification', 'rating', 'experience required',
        'insurance required', 'public liability', 'workmen compensation',
        'indemnity', 'indemnify', 'hold harmless', 'force majeure',
        'termination', 'cancellation', 'subcontracting', 'assignment'
    ]
    compliance_sections = []
    lines = raw_text.lower().split('\n')
    for i, line in enumerate(lines):
        for keyword in compliance_keywords:
            if keyword in line and line.strip() not in compliance_sections:
                compliance_sections.append(line.strip())

    return {
        "penalties": penalties if penalties else ["No explicit penalty clauses detected"],
        "deadlines": deadlines if deadlines else ["No explicit deadline clauses detected"],
        "compliance_clauses": compliance_sections[:10] if compliance_sections else ["Review tender document for compliance requirements"]
    }

@app.get("/api/timeline")
async def generate_timeline(
    duration_months: int = Query(...),
    workers: int = Query(...),
    tender_type: str = Query("general")
):
    milestones = []
    total_days = duration_months * 30

    if tender_type.lower() == 'construction':
        phase_days = [
            ("Mobilization & Site Setup", 0.08, ["Site establishment", "Equipment delivery", "Initial assessments"]),
            ("Foundation & Structural Work", 0.08, ["Groundworks", "Foundations", "Structural elements"]),
            ("Main Construction Phase", 0.35, ["Building construction", "Installation work", "Quality checks"]),
            ("Finishing & Fixtures", 0.25, ["Interior finishing", "Fixtures installation", "Painting"]),
            ("Testing & Commissioning", 0.12, ["Systems testing", "Compliance verification", "Commissioning"]),
            ("Handover & Closeout", 0.12, ["Final inspection", "Documentation", "Defect resolution"])
        ]
    elif tender_type.lower() == 'cleaning':
        phase_days = [
            ("Mobilization", 0.10, ["Staff recruitment", "Training", "Equipment procurement"]),
            ("Initial Deep Clean", 0.15, ["Premises assessment", "Deep cleaning", "Equipment setup"]),
            ("Service Commencement", 0.40, ["Regular cleaning services", "Quality monitoring", "Staff supervision"]),
            ("Mid-Contract Review", 0.10, ["Performance review", "Client feedback", "Service adjustments"]),
            ("Continued Services", 0.15, ["Ongoing service delivery", "Staff management", "Supply management"]),
            ("Contract Closeout", 0.10, ["Final inspection", "Documentation", "Transition support"])
        ]
    elif tender_type.lower() == 'security':
        phase_days = [
            ("Mobilization", 0.12, ["Guard recruitment", "Clearance verification", "Equipment setup"]),
            ("Site Assessment", 0.08, ["Risk assessment", "Patrol routes", "System configuration"]),
            ("Service Commencement", 0.45, ["24/7 security operations", "Incident response", "Reporting"]),
            ("Quarterly Review", 0.15, ["Performance metrics", "Client meetings", "Service optimization"]),
            ("Continued Operations", 0.12, ["Ongoing security services", "Training updates", "System maintenance"]),
            ("Contract Closeout", 0.08, ["Knowledge transfer", "Documentation", "Final reporting"])
        ]
    elif tender_type.lower() == 'it_services':
        phase_days = [
            ("Discovery & Planning", 0.15, ["Requirements gathering", "Architecture design", "Timeline planning"]),
            ("Development Phase", 0.35, ["Core development", "Integration", "Testing"]),
            ("Implementation", 0.25, ["Deployment", "User training", "Go-live support"]),
            ("Stabilization", 0.15, ["Bug fixes", "Performance optimization", "Documentation"]),
            ("Project Closeout", 0.10, ["Final handover", "Training completion", "Support transition"])
        ]
    else:
        phase_days = [
            ("Mobilization", 0.12, ["Team assembly", "Resource planning", "Initial setup"]),
            ("Planning & Preparation", 0.10, ["Detailed planning", "Risk assessment", "Schedule creation"]),
            ("Main Service Delivery", 0.45, ["Service delivery", "Quality monitoring", "Client liaison"]),
            ("Midpoint Review", 0.10, ["Progress review", "Adjustments", "Client feedback"]),
            ("Continued Delivery", 0.13, ["Ongoing services", "Performance optimization", "Reporting"]),
            ("Contract Closeout", 0.10, ["Final deliverables", "Documentation", "Transition support"])
        ]

    current_day = 0
    for phase_name, phase_ratio, tasks in phase_days:
        phase_days_count = int(total_days * phase_ratio)
        end_day = min(current_day + phase_days_count, total_days)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=end_day)

        milestones.append({
            "phase": phase_name,
            "start_day": current_day,
            "end_day": end_day,
            "duration_days": phase_days_count,
            "tasks": tasks,
            "workforce_allocation": max(1, int(workers * phase_ratio * 2)) if phase_ratio > 0.1 else max(1, workers)
        })
        current_day = end_day
        if current_day >= total_days:
            break

    return {
        "tender_type": tender_type,
        "total_duration_months": duration_months,
        "total_duration_days": total_days,
        "workforce": workers,
        "milestones": milestones,
        "estimated_completion": (datetime.now() + timedelta(days=total_days)).strftime("%Y-%m-%d")
    }

BRANDING_CONFIG = {"company_name": "Contractor Name", "logo_path": None}

@app.post("/api/branding")
async def set_branding(
    company_name: str = Body(...),
    logo: UploadFile = File(None)
):
    global BRANDING_CONFIG

    BRANDING_CONFIG["company_name"] = company_name

    if logo:
        allowed_ext = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}
        file_ext = Path(logo.filename).suffix.lower()
        if file_ext not in allowed_ext:
            raise HTTPException(400, f"Invalid logo format. Allowed: {', '.join(allowed_ext)}")

        logo_filename = f"brand_logo{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
        logo_path = UPLOADS / logo_filename

        content = await logo.read()
        with open(logo_path, 'wb') as f:
            f.write(content)

        BRANDING_CONFIG["logo_path"] = str(logo_path)

    return {
        "success": True,
        "company_name": BRANDING_CONFIG["company_name"],
        "logo_url": f"/static/uploads/{Path(BRANDING_CONFIG['logo_path']).name}" if BRANDING_CONFIG["logo_path"] else None
    }

@app.get("/api/branding")
async def get_branding():
    return {
        "company_name": BRANDING_CONFIG["company_name"],
        "logo_url": f"/static/uploads/{Path(BRANDING_CONFIG['logo_path']).name}" if BRANDING_CONFIG["logo_path"] else None
    }

@app.post("/api/email-pack")
async def generate_email_pack(
    tender_id: str = Body(None),
    tender_data: dict = Body(None),
    pricing: dict = Body(None)
):
    if tender_id:
        tender_path = HISTORY / f"{tender_id}.json"
        if not tender_path.exists():
            matches = list(HISTORY.glob(f"*{tender_id}*.json"))
            if matches:
                tender_path = matches[0]

        if tender_path.exists():
            with open(tender_path) as f:
                full_data = json.load(f)
                tender_data = tender_data or full_data.get("tender_data", full_data)
                pricing = pricing or full_data.get("pricing", {})

    if not tender_data:
        raise HTTPException(400, "Either tender_id or tender_data must be provided")

    ref = tender_data.get("reference", "TENDER")
    sector = tender_data.get("sector", tender_data.get("tender_type", "Services"))
    location = tender_data.get("location", "N/A")
    duration = tender_data.get("duration_months", tender_data.get("duration", {}).get("months", 12))
    client = tender_data.get("client", {}).get("name", "Client")

    total_value = 0
    if pricing and isinstance(pricing, dict):
        total_value = pricing.get("total_contract_value", 0)

    subject = f"Tender Submission: {ref} - {sector.title()} Services for {location}"

    body = f"""Dear {client},

Thank you for the opportunity to submit our tender for the provision of {sector} services.

TENDER REFERENCE: {ref}
LOCATION: {location}
DURATION: {duration} months
TOTAL CONTRACT VALUE: R {total_value:,.2f}

Please find attached our comprehensive tender submission including:
- Technical Proposal (Word document)
- Pricing Schedule (Excel spreadsheet)
- All required compliance documentation

Our submission demonstrates our capability to deliver high-quality {sector} services tailored to your specific requirements. We have the necessary resources, experience, and commitment to ensure successful contract delivery.

We look forward to the opportunity to work with you.

Best regards,

{BRANDING_CONFIG['company_name']}
"""

    attachments = []
    if OUTPUTS.exists():
        docx_files = sorted(OUTPUTS.glob("tender_*.docx"), key=lambda x: x.stat().st_mtime, reverse=True)
        if docx_files:
            attachments.append({"filename": docx_files[0].name, "type": "document"})

        xlsx_files = sorted(OUTPUTS.glob("pricing_*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)
        if xlsx_files:
            attachments.append({"filename": xlsx_files[0].name, "type": "pricing"})

    return {
        "subject": subject,
        "body": body,
        "attachments": attachments,
        "metadata": {
            "reference": ref,
            "sector": sector,
            "location": location,
            "duration_months": duration,
            "total_value": total_value,
            "company": BRANDING_CONFIG["company_name"]
        }
    }

@app.get("/api/download/word/{filename}")
async def download_word(filename: str):
    file_path = OUTPUTS / filename
    if not file_path.exists():
        raise HTTPException(404, "Word document not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@app.get("/api/download/excel/{filename}")
async def download_excel(filename: str):
    file_path = OUTPUTS / filename
    if not file_path.exists():
        raise HTTPException(404, "Excel workbook not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.get("/api/download/zip")
async def download_zip(word: str = Query(...), excel: str = Query(...)):
    import zipfile
    import io
    
    zip_filename = f"tender_submission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    # Create zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        word_path = OUTPUTS / word
        if word_path.exists():
            zip_file.write(word_path, word)
            
        excel_path = OUTPUTS / excel
        if excel_path.exists():
            zip_file.write(excel_path, excel)
            
    zip_buffer.seek(0)
    return Response(
        zip_buffer.getvalue(),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment;filename={zip_filename}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=120)
