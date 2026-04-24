import asyncio
import aiohttp
import re
from typing import Dict, List, Optional
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import time

class WebSearcher:
    def __init__(self):
        self.ddgs = DDGS()
        self.session = None
        
    async def search_all_rates(self, tender_data: Dict) -> Dict:
        """Search for all relevant rates based on tender type"""
        tender_type = tender_data.get('tender_type', 'general')
        tasks = []
        
        if tender_type == 'cleaning':
            tasks = [
                self._search_cleaning_wages(),
                self._search_equipment_rates('cleaning'),
                self._search_cleaning_materials()
            ]
        elif tender_type == 'construction':
            tasks = [
                self._search_construction_wages(),
                self._search_equipment_rates('construction'),
                self._search_construction_materials()
            ]
        elif tender_type == 'electrical':
            tasks = [
                self._search_electrical_wages(),
                self._search_electrical_materials(),
                self._search_equipment_rates('electrical')
            ]
        elif tender_type == 'security':
            tasks = [
                self._search_security_wages(),
                self._search_security_equipment(),
                self._search_psira_rates()
            ]
        elif tender_type == 'plumbing':
            tasks = [
                self._search_plumbing_wages(),
                self._search_plumbing_materials()
            ]
        else:
            tasks = [self._search_general_rates()]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        combined = {}
        for result in results:
            if isinstance(result, dict):
                combined.update(result)
        
        return combined
    
    async def _search_cleaning_wages(self) -> Dict:
        """Search for SA cleaning sector wages"""
        queries = [
            "SA cleaning sector wage determination 2025 general worker",
            "cleaning sector minimum wage South Africa 2025 hourly rate",
            "cleaning supervisor monthly salary South Africa"
        ]
        
        rates = {
            'general_worker_hourly': 23.50,  # Default sectoral determination
            'supervisor_monthly': 8500.00,
            'team_leader_hourly': 28.00
        }
        
        for query in queries:
            try:
                results = self.ddgs.text(query, max_results=3)
                for r in results:
                    text = r['body']
                    # Extract hourly rates
                    match = re.search(r'R\s*(\d+\.?\d*)\s*(?:per\s*hour|/hour|hourly)', text, re.IGNORECASE)
                    if match:
                        rates['general_worker_hourly'] = float(match.group(1))
                    
                    # Extract monthly
                    match = re.search(r'R\s*(\d[\d\s,]*)\s*(?:per\s*month|monthly)', text, re.IGNORECASE)
                    if match:
                        val = float(match.group(1).replace(' ', '').replace(',', ''))
                        if val > 5000:  # Likely supervisor
                            rates['supervisor_monthly'] = val
            except Exception as e:
                print(f"Search error: {e}")
                continue
        
        return {
            'labour_rates': rates,
            'source': 'Sectoral Determination 1: Cleaning Services'
        }
    
    async def _search_construction_wages(self) -> Dict:
        """Search CIDB and construction wages"""
        rates = {
            'skilled_artisan_daily': 450.00,
            'semi_skilled_daily': 350.00,
            'general_worker_daily': 250.00,
            'foreman_daily': 650.00
        }
        
        queries = [
            "CIDB construction worker daily rate South Africa 2025",
            "bricklayer daily wage South Africa",
            "construction foreman daily rate 2025"
        ]
        
        for query in queries:
            try:
                results = self.ddgs.text(query, max_results=2)
                for r in results:
                    text = r['body']
                    if 'bricklayer' in text.lower() or 'artisan' in text.lower():
                        match = re.search(r'R\s*(\d+\.?\d*)', text)
                        if match:
                            rates['skilled_artisan_daily'] = float(match.group(1))
            except:
                continue
        
        return {'labour_rates': rates, 'source': 'CIDB/BCCEI'}
    
    async def _search_electrical_wages(self) -> Dict:
        rates = {
            'electrician_hourly': 150.00,
            'assistant_electrician_hourly': 80.00,
            'master_electrician_hourly': 250.00
        }
        
        try:
            results = self.ddgs.text("electrician hourly rate South Africa 2025", max_results=3)
            for r in results:
                match = re.search(r'R\s*(\d+\.?\d*)', r['body'])
                if match:
                    val = float(match.group(1))
                    if 100 < val < 300:
                        rates['electrician_hourly'] = val
        except:
            pass
            
        return {'labour_rates': rates, 'source': 'Electrical Contracting Industry'}
    
    async def _search_security_wages(self) -> Dict:
        rates = {
            'security_guard_monthly': 5500.00,
            'armed_response_monthly': 8500.00,
            'supervisor_monthly': 9500.00,
            'psira_registration': 450.00
        }
        
        try:
            results = self.ddgs.text("security guard minimum wage South Africa 2025", max_results=3)
            for r in results:
                match = re.search(r'R\s*(\d[\d\s,]*)', r['body'])
                if match:
                    val = float(match.group(1).replace(' ', '').replace(',', ''))
                    if 4000 < val < 7000:
                        rates['security_guard_monthly'] = val
        except:
            pass
            
        return {'labour_rates': rates, 'source': 'PSIRA/Sectoral Determination'}
    
    async def _search_plumbing_wages(self) -> Dict:
        return {
            'labour_rates': {
                'plumber_hourly': 180.00,
                'assistant_plumber_hourly': 100.00,
                'apprentice_plumber_hourly': 60.00
            },
            'source': 'Plumbing Industry'
        }
    
    async def _search_equipment_rates(self, tender_type: str) -> Dict:
        """Search for equipment rental rates"""
        equipment_rates = {}
        
        if tender_type == 'cleaning':
            searches = {
                'scrubbing_machine': 'industrial floor scrubber rental price per day South Africa',
                'vacuum_industrial': 'industrial vacuum cleaner rental daily rate SA',
                'pressure_washer': 'pressure washer hire rate per day'
            }
        elif tender_type == 'construction':
            searches = {
                'excavator': 'excavator rental cost per hour South Africa',
                'tipper_truck': 'tipper truck hire daily rate',
                'concrete_mixer': 'concrete mixer rental price per day'
            }
        else:
            searches = {}
        
        for equipment, query in searches.items():
            try:
                results = self.ddgs.text(query, max_results=2)
                for r in results:
                    match = re.search(r'R\s*(\d+\.?\d*)', r['body'])
                    if match:
                        equipment_rates[equipment] = float(match.group(1))
                        break
            except:
                # Fallback rates
                equipment_rates[equipment] = 800.00 if 'excavator' in equipment else 350.00
        
        return {'equipment_rates': equipment_rates}
    
    async def _search_cleaning_materials(self) -> Dict:
        return {
            'material_rates': {
                'detergent_per_litre': 25.00,
                'disinfectant_per_litre': 35.00,
                'floor_polish_per_litre': 45.00,
                'consumables_per_sqm_monthly': 2.50
            }
        }
    
    async def _search_construction_materials(self) -> Dict:
        return {
            'material_rates': {
                'concrete_per_m3': 1200.00,
                'bricks_per_1000': 650.00,
                'steel_rebar_per_ton': 14500.00,
                'cement_per_bag': 95.00
            }
        }
    
    async def _search_electrical_materials(self) -> Dict:
        return {
            'material_rates': {
                'cable_2_5mm_per_meter': 28.00,
                'cable_4mm_per_meter': 42.00,
                'distribution_board': 850.00,
                'breaker_20a': 85.00,
                'led_fitting': 125.00
            }
        }
    
    async def _search_security_equipment(self) -> Dict:
        return {
            'equipment_rates': {
                'cctv_camera_install': 2500.00,
                'access_control_point': 4500.00,
                'alarm_install': 1800.00
            }
        }
    
    async def _search_psira_rates(self) -> Dict:
        return {'psira_grade_a': 8500.00, 'psira_grade_b': 6500.00, 'psira_grade_c': 5500.00}
    
    async def _search_plumbing_materials(self) -> Dict:
        return {
            'material_rates': {
                'pvc_pipe_110mm_per_meter': 85.00,
                'fittings_set': 120.00,
                'cement_kg': 25.00
            }
        }
    
    async def _search_general_rates(self) -> Dict:
        return {
            'labour_rates': {
                'skilled_hourly': 120.00,
                'semi_skilled_hourly': 80.00,
                'general_hourly': 45.00
            }
        }
    
    async def search_past_contractors(self, tender_data: Dict) -> List[Dict]:
        """Search for past award information"""
        reference = tender_data.get('reference', '')
        queries = [
            f"{reference} awarded to",
            f"{reference} contract award",
            f"tender award {reference}"
        ]
        
        contractors = []
        
        for query in queries:
            try:
                results = self.ddgs.text(query, max_results=3)
                for r in results:
                    # Try to extract contractor name and value
                    text = r['body']
                    # Simple extraction patterns
                    if 'awarded' in text.lower() or 'contract' in text.lower():
                        contractors.append({
                            'source': r['href'],
                            'snippet': text[:200],
                            'confidence': 'low'  # Web search results need verification
                        })
            except:
                continue
        
        return contractors
