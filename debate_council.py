import asyncio
import json
import re
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import aiohttp

from env_loader import load_env_file

load_env_file(Path(__file__).resolve().parent / ".env")

@dataclass
class DebateRound:
    model: str
    role: str
    price: float
    reasoning: str

class DebateCouncil:
    """
    3-Cloud-Model Debate Council - Using CURRENT VALID Groq models
    Valid models: llama-3.3-70b-versatile, llama-3.1-8b-instant
    """
    
    def __init__(self, model_configs=None, websocket=None):
        self.websocket = websocket
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"
        self.api_available = bool(self.api_key) and self.api_key.startswith("gsk_")
        
        # UPDATED: Only use models that EXIST on Groq free tier
        self.models = {
            "cost_accountant": {
                "id": "llama-3.3-70b-versatile",  # Works ✓
                "role": "Cost Accountant",
                "temp": 0.3
            },
            "market_analyst": {
                "id": "llama-3.1-8b-instant",  # Works ✓ (replaces mixtral)
                "role": "Market Analyst",
                "temp": 0.7
            },
            "risk_assessor": {
                "id": "llama-3.1-8b-instant",  # Works ✓ (replaces gemma)
                "role": "Risk Assessor",
                "temp": 0.5
            }
        }
        
        if not self.api_available:
            print("⚠️ WARNING: No valid GROQ_API_KEY. Using local calculation.")
    
    async def _send(self, message: dict):
        if not self.websocket:
            return False
        try:
            await self.websocket.send_json(message)
            return True
        except:
            return False
    
    async def _call_groq(self, model_id: str, prompt: str, temperature: float = 0.7) -> str:
        if not self.api_available:
            return "Error: No API key"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 500
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 401:
                        return "Error: Invalid API key"
                    elif resp.status == 400:
                        text = await resp.text()
                        return f"Error: Model unavailable ({text[:100]})"
                    elif resp.status != 200:
                        return f"Error HTTP {resp.status}"
                    
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _extract_price(self, text: str) -> float:
        if not text or text.startswith("Error"):
            return 0.0
        
        matches = re.findall(r'R\s*([\d\s,]+)', text)
        for m in matches:
            try:
                return float(m.replace(' ', '').replace(',', ''))
            except:
                continue
        
        matches = re.findall(r'\b[\d,]+\b', text)
        for m in matches:
            try:
                val = float(m.replace(',', ''))
                if 10000 < val < 10000000:
                    return val
            except:
                continue
        return 0.0
    
    def _calculate_fallback(self, tender_data: Dict, rates: Dict) -> Dict:
        tender_type = tender_data.get('tender_type', 'general')
        req = tender_data.get('requirements', {})
        duration = tender_data.get('duration_months', 12)
        
        workers = req.get('workers', 0)
        if workers == 0:
            area = req.get('area_sqm', 1000)
            workers = max(2, area // 400)
        
        if tender_type == 'cleaning':
            hourly_rate = 25.00
            hours = req.get('hours_per_day', 8)
            days = 22
            monthly_labour = workers * hourly_rate * hours * days * 1.35
            equipment = 3000 * req.get('shifts', 1)
            materials = req.get('area_sqm', workers * 400) * 2.50
        else:
            monthly_labour = workers * 450 * 22 * 1.35
            equipment = 5000
            materials = 2000
        
        transport = 2000
        subtotal = monthly_labour + equipment + materials + transport
        overheads = subtotal * 0.15
        profit = subtotal * 0.15
        vat = (subtotal + overheads + profit) * 0.15
        total = subtotal + overheads + profit + vat
        
        return {
            "final_price": total,
            "confidence": 65.0,
            "proposals": [
                {"model": "Local-Cost", "role": "Cost Accountant", "price": total * 0.95},
                {"model": "Local-Market", "role": "Market Analyst", "price": total},
                {"model": "Local-Risk", "role": "Risk Assessor", "price": total * 1.05}
            ],
            "consensus_reasoning": f"Local calculation: {workers} workers, R{total:,.2f}/month",
            "price_range": f"R {total*0.95:,.0f} - R {total*1.05:,.0f}",
            "fallback": True,
            "monthly_labour": monthly_labour,
            "equipment": equipment,
            "materials": materials,
            "subtotal": subtotal,
            "overheads": overheads,
            "profit": profit,
            "vat": vat,
            "total_monthly": total
        }
    
    async def deliberate(self, tender_data: Dict, rates: Dict, past_contractors: List) -> Dict:
        context = json.dumps({
            "type": tender_data.get('tender_type', 'Unknown'),
            "ref": tender_data.get('reference', 'TBC'),
            "duration": tender_data.get('duration_months', 12),
            "location": tender_data.get('location', 'SA'),
            "workers": tender_data.get('requirements', {}).get('workers', 0),
            "area": tender_data.get('requirements', {}).get('area_sqm', 0)
        })[:1500]
        
        await self._send({"step": "debate_start", "message": "Starting pricing analysis...", "progress": 55})
        
        if not self.api_available:
            await self._send({"step": "warning", "message": "Using local calculation...", "progress": 60})
            result = self._calculate_fallback(tender_data, rates)
            return result
        
        proposals = []
        api_failed = 0
        
        for key, config in self.models.items():
            await self._send({"step": "thinking", "message": f"Querying {config['role']}...", "progress": 60})
            
            prompt = f"You are {config['role']} for SA tenders.\nContext: {context}\nPropose monthly price ZAR.\nFormat: PRICE: R [amount]"
            
            response = await self._call_groq(config["id"], prompt, config["temp"])
            
            if response.startswith("Error"):
                print(f"API Error: {response}")
                api_failed += 1
                fallback = self._calculate_fallback(tender_data, rates)
                proposals.append(DebateRound(config["id"], config["role"], fallback["final_price"], response))
            else:
                price = self._extract_price(response)
                proposals.append(DebateRound(config["id"], config["role"], price, response[:200]))
                await self._send({"step": "proposal", "message": f"{config['role']}: R {price:,.2f}", "data": {"price": price}})
            
            await asyncio.sleep(0.5)
        
        if api_failed == 3:
            await self._send({"step": "warning", "message": "All API failed, using local calc...", "progress": 70})
            return self._calculate_fallback(tender_data, rates)
        
        prices = [p.price for p in proposals if p.price > 0]
        if len(prices) >= 2:
            avg = sum(prices) / len(prices)
            confidence = 85.0 if api_failed == 0 else 70.0
        else:
            fallback = self._calculate_fallback(tender_data, rates)
            return fallback
        
        await self._send({"step": "complete", "message": f"Consensus: R {avg:,.2f}", "progress": 85})
        
        return {
            "final_price": avg,
            "confidence": confidence,
            "proposals": [{"model": p.model, "role": p.role, "price": p.price} for p in proposals],
            "consensus_reasoning": "Cloud debate complete",
            "price_range": f"R {min(prices):,.0f} - R {max(prices):,.0f}",
            "fallback": api_failed > 0
        }

@dataclass
class ModelConfig:
    name: str
    role: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class MemoryEfficientDebateCouncil(DebateCouncil):
    pass
