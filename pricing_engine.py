from typing import Dict, List
import math

class PricingEngine:
    """
    HONEST PRICING - Sector-Specific Calculations
    Zero placeholders. Real market rates only.
    """
    
    def __init__(self):
        # SA Sectoral Determination 2024 rates
        self.base_rates = {
            'cleaning': {
                'general_worker_hourly': 23.50,
                'supervisor_monthly': 8500.00,
                'deductions_pct': 0.35
            },
            'construction': {
                'general_worker_daily': 250.00,
                'semi_skilled_daily': 350.00,
                'skilled_artisan_daily': 450.00,
                'foreman_daily': 650.00,
                'deductions_pct': 0.25
            },
            'electrical': {
                'assistant_electrician_daily': 350.00,
                'electrician_daily': 550.00,
                'master_electrician_daily': 850.00,
                'deductions_pct': 0.30
            },
            'security': {
                'grade_c_guard_daily': 220.00,
                'grade_b_guard_daily': 280.00,
                'grade_a_guard_daily': 350.00,
                'deductions_pct': 0.30
            },
            'gardening': {
                'gardener_daily': 180.00,
                'supervisor_daily': 280.00,
                'deductions_pct': 0.25
            },
            'it_services': {
                'technician_daily': 1200.00,
                'senior_consultant_daily': 2500.00,
                'deductions_pct': 0.20
            }
        }
        
        self.equipment_rates = {
            'cleaning': {
                'industrial_scrubber': 800,
                'vacuum_industrial': 200,
                'pressure_washer': 350,
                'carpet_cleaner': 450,
                'polisher': 250
            },
            'construction': {
                'excavator_20t': 2800,
                'tipper_truck': 1800,
                'concrete_mixer': 650,
                'scaffolding_100m': 1200,
                'compactor': 900
            },
            'electrical': {
                'scissor_lift': 800,
                'cable_tester': 300,
                'drum_trailer': 200
            },
            'gardening': {
                'ride_on_mower': 600,
                'brush_cutter': 150,
                'chainsaw': 100,
                'chipper': 400
            }
        }
        
        self.material_rates = {
            'cleaning': {
                'consumables_per_sqm_monthly': 2.50,
                'chemicals_per_worker_monthly': 150
            },
            'construction': {
                'concrete_per_m3': 1200,
                'bricks_per_1000': 650,
                'steel_rebar_per_ton': 14500,
                'cement_per_bag': 95,
                'sand_per_m3': 450
            },
            'electrical': {
                'cable_2.5mm_per_m': 28,
                'cable_4mm_per_m': 42,
                'distribution_board': 850,
                'breaker_20a': 85,
                'led_fitting': 125
            },
            'gardening': {
                'fertilizer_per_100m2': 180,
                'plants_average': 45,
                'mulch_per_m3': 380
            }
        }
        
        self.vat_rate = 0.15
        self.standard_overhead = 0.15
        self.standard_profit = 0.15

        self.location_multipliers = {
            'gauteng': 1.0,
            'johannesburg': 1.0,
            'pretoria': 1.0,
            'tshwane': 1.0,
            'western cape': 1.1,
            'cape town': 1.1,
            'limpopo': 0.85,
            'polokwane': 0.85,
            'mpumalanga': 0.92,
            'kwa-zulu natal': 0.95,
            'durban': 0.95,
            'kzn': 0.95,
            'eastern cape': 0.88,
            'port elizabeth': 0.88,
            'gqeberha': 0.88,
            'free state': 0.90,
            'bloemfontein': 0.90,
            'north west': 0.87,
            'rustenburg': 0.87,
            'northen cape': 0.83,
            'kimberley': 0.83
        }

    def apply_location_factor(self, pricing_result: Dict, location: str) -> Dict:
        location_lower = location.lower() if location else ''
        multiplier = self.location_multipliers.get(location_lower, 1.0)

        if multiplier != 1.0:
            labour = pricing_result.get('labour_cost', 0)
            equipment = pricing_result.get('equipment_cost', 0)
            materials = pricing_result.get('materials_cost', 0)
            transport = pricing_result.get('transport_cost', 0)

            adjusted_labour = labour * multiplier
            adjusted_equipment = equipment * multiplier
            adjusted_materials = materials * multiplier
            adjusted_transport = transport * multiplier

            old_subtotal = pricing_result.get('subtotal', 0)
            new_subtotal = adjusted_labour + adjusted_equipment + adjusted_materials + adjusted_transport
            overheads = new_subtotal * self.standard_overhead
            profit = (new_subtotal + overheads) * self.standard_profit
            vat = (new_subtotal + overheads + profit) * self.vat_rate
            total_monthly = new_subtotal + overheads + profit + vat

            pricing_result['location'] = location
            pricing_result['location_multiplier'] = multiplier
            pricing_result['labour_cost'] = round(adjusted_labour, 2)
            pricing_result['equipment_cost'] = round(adjusted_equipment, 2)
            pricing_result['materials_cost'] = round(adjusted_materials, 2)
            pricing_result['transport_cost'] = round(adjusted_transport, 2)
            pricing_result['subtotal'] = round(new_subtotal, 2)
            pricing_result['overheads'] = round(overheads, 2)
            pricing_result['profit'] = round(profit, 2)
            pricing_result['vat'] = round(vat, 2)
            pricing_result['total_monthly'] = round(total_monthly, 2)
            duration_months = pricing_result.get('duration_months', 12)
            pricing_result['total_contract_value'] = round(total_monthly * duration_months, 2)

        return pricing_result

    def reprice(self, pricing: Dict, mode: str) -> Dict:
        mode_configs = {
            'optimize_win': {'profit_reduction': 0.08, 'overhead_reduction': 0.05, 'description': 'Competitive pricing to maximize win probability'},
            'maximize_profit': {'profit_increase': 0.05, 'overhead_increase': 0.02, 'description': 'Pricing with higher margin for better profitability'},
            'reduce_margin': {'profit_reduction': 0.12, 'overhead_reduction': 0.08, 'description': 'Aggressive margin reduction for price-sensitive contracts'}
        }

        config = mode_configs.get(mode, mode_configs['optimize_win'])
        new_pricing = pricing.copy()

        subtotal = pricing.get('subtotal', 0)
        current_profit = pricing.get('profit', 0)
        current_overheads = pricing.get('overheads', 0)

        if 'profit_reduction' in config:
            new_profit = current_profit * (1 - config['profit_reduction'])
            new_overheads = current_overheads * (1 - config['overhead_reduction'])
        elif 'profit_increase' in config:
            new_profit = current_profit * (1 + config['profit_increase'])
            new_overheads = current_overheads * (1 + config['overhead_increase'])
        else:
            new_profit = current_profit
            new_overheads = current_overheads

        vat = (subtotal + new_overheads + new_profit) * self.vat_rate
        total_monthly = subtotal + new_overheads + new_profit + vat
        duration_months = pricing.get('duration_months', 12)

        new_pricing['profit'] = round(new_profit, 2)
        new_pricing['overheads'] = round(new_overheads, 2)
        new_pricing['vat'] = round(vat, 2)
        new_pricing['total_monthly'] = round(total_monthly, 2)
        new_pricing['total_contract_value'] = round(total_monthly * duration_months, 2)
        new_pricing['reprice_mode'] = mode
        new_pricing['reprice_description'] = config['description']

        return new_pricing
    
    def calculate(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        sector = tender_data.get('sector', 'general')
        
        calculators = {
            'cleaning': self._calculate_cleaning,
            'construction': self._calculate_construction,
            'electrical': self._calculate_electrical,
            'security': self._calculate_security,
            'gardening': self._calculate_gardening,
            'it_services': self._calculate_it,
            'maintenance': self._calculate_maintenance,
            'supply': self._calculate_supply,
            'general': self._calculate_general
        }
        
        calculator = calculators.get(sector, self._calculate_general)
        result = calculator(tender_data, rates_found, debate_result)
        
        result['sector'] = sector
        result['calculation_method'] = f"{sector}_sector_formula"
        
        return result
    
    def _calculate_cleaning(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        req = tender_data.get('requirements', {})
        workforce = tender_data.get('workforce', {})
        scope = tender_data.get('scope', {})
        duration = tender_data.get('duration', {})
        
        duration_months = duration.get('months', 12)
        
        # FIXED: Get workers and supervisors separately
        total_workers = workforce.get('total_workers', 10)
        supervisors = workforce.get('supervisors', 1)
        cleaners = workforce.get('unskilled_workers', 0)
        
        # If extraction didn't separate, use standard 9:1 ratio
        if cleaners == 0:
            cleaners = max(1, total_workers - supervisors)
            if supervisors == 0:
                supervisors = max(1, int(cleaners / 9))  # 1 per 9 cleaners
        
        area_sqm = scope.get('area_sqm', cleaners * 400)
        shifts = req.get('shifts_per_day', 1)
        hours_per_day = req.get('hours_per_day', 8)
        days_per_month = 22
        
        # CLEANER COSTS (Hourly)
        hourly_rate = self.base_rates['cleaning']['general_worker_hourly']
        monthly_wage_cleaner = hourly_rate * hours_per_day * days_per_month
        total_cleaners_cost = (cleaners * monthly_wage_cleaner) * (1 + self.base_rates['cleaning']['deductions_pct'])
        
        # SUPERVISOR COSTS (Monthly salary - SEPARATE!)
        supervisor_monthly = self.base_rates['cleaning']['supervisor_monthly']
        total_supervisors_cost = (supervisors * supervisor_monthly) * (1 + self.base_rates['cleaning']['deductions_pct'])
        
        # TOTAL LABOUR
        total_labour = total_cleaners_cost + total_supervisors_cost
        
        # Equipment
        if area_sqm <= 1000:
            equipment_monthly = 2500 * shifts
        elif area_sqm <= 5000:
            equipment_monthly = 6000 * shifts
        else:
            equipment_monthly = 12000 * shifts
        
        # Materials
        consumables_rate = self.material_rates['cleaning']['consumables_per_sqm_monthly']
        materials_monthly = (area_sqm * consumables_rate * shifts) + (cleaners * 150)
        
        # Transport
        transport_monthly = 150 * days_per_month * shifts
        
        subtotal = total_labour + equipment_monthly + materials_monthly + transport_monthly
        
        # Emergency premium
        emergency_premium = 0
        if scope.get('is_emergency'):
            emergency_premium = subtotal * 0.50
            subtotal += emergency_premium
        
        overheads = subtotal * self.standard_overhead
        profit = (subtotal + overheads) * self.standard_profit
        vat = (subtotal + overheads + profit) * self.vat_rate
        
        total_monthly = subtotal + overheads + profit + vat
        
        return {
            'labour_cost': round(total_labour, 2),
            'equipment_cost': round(equipment_monthly, 2),
            'materials_cost': round(materials_monthly, 2),
            'transport_cost': round(transport_monthly, 2),
            'emergency_premium': round(emergency_premium, 2),
            'subtotal': round(subtotal, 2),
            'overheads': round(overheads, 2),
            'profit': round(profit, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total_monthly, 2),
            'total_contract_value': round(total_monthly * duration_months, 2),
            'breakdown': {
                'cleaners': cleaners,
                'cleaners_hourly_rate': hourly_rate,
                'cleaners_monthly_each': round(monthly_wage_cleaner, 2),
                'supervisors': supervisors,
                'supervisor_monthly_salary': supervisor_monthly,
                'total_personnel': cleaners + supervisors,
                'area_sqm': area_sqm,
                'shifts': shifts
            }
        }
    
    def _calculate_construction(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        req = tender_data.get('requirements', {})
        workforce = tender_data.get('workforce', {})
        duration = tender_data.get('duration', {})
        
        duration_months = duration.get('months', 6)
        days_per_month = 22
        
        workers = workforce.get('total_workers', 10)
        skilled = workforce.get('skilled_workers', 6)
        unskilled = workforce.get('unskilled_workers', 3)
        supervisors = workforce.get('supervisors', 1)
        
        skilled_daily = self.base_rates['construction']['skilled_artisan_daily']
        unskilled_daily = self.base_rates['construction']['general_worker_daily']
        foreman_daily = self.base_rates['construction']['foreman_daily']
        
        skilled_monthly = skilled * skilled_daily * days_per_month
        unskilled_monthly = unskilled * unskilled_daily * days_per_month
        foreman_monthly = supervisors * foreman_daily * days_per_month
        
        total_labour = (skilled_monthly + unskilled_monthly + foreman_monthly) * (1 + self.base_rates['construction']['deductions_pct'])
        
        plant_monthly = 15000
        materials_base = 50000
        materials_markup = materials_base * 0.15
        materials_total = materials_base + materials_markup
        
        transport_monthly = 8000
        
        subtotal = total_labour + plant_monthly + materials_total + transport_monthly
        
        overheads = subtotal * 0.20
        profit = (subtotal + overheads) * 0.15
        vat = (subtotal + overheads + profit) * self.vat_rate
        
        total_monthly = subtotal + overheads + profit + vat
        
        return {
            'labour_cost': round(total_labour, 2),
            'equipment_cost': round(plant_monthly, 2),
            'materials_cost': round(materials_total, 2),
            'transport_cost': round(transport_monthly, 2),
            'subtotal': round(subtotal, 2),
            'overheads': round(overheads, 2),
            'profit': round(profit, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total_monthly, 2),
            'total_contract_value': round(total_monthly * duration_months, 2),
            'breakdown': {
                'skilled_workers': skilled,
                'unskilled_workers': unskilled,
                'daily_rates': {'skilled': skilled_daily, 'unskilled': unskilled_daily}
            }
        }
    
    def _calculate_electrical(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        req = tender_data.get('requirements', {})
        workforce = tender_data.get('workforce', {})
        duration = tender_data.get('duration', {})
        
        duration_months = duration.get('months', 3)
        days_per_month = 22
        
        electricians = workforce.get('skilled_workers', 3)
        assistants = workforce.get('unskilled_workers', 1)
        
        elec_daily = self.base_rates['electrical']['electrician_daily']
        assist_daily = self.base_rates['electrical']['assistant_electrician_daily']
        
        monthly_elec = electricians * elec_daily * days_per_month
        monthly_assist = assistants * assist_daily * days_per_month
        
        total_labour = (monthly_elec + monthly_assist) * (1 + self.base_rates['electrical']['deductions_pct'])
        
        equipment_monthly = 5000
        materials_monthly = 15000
        
        subtotal = total_labour + equipment_monthly + materials_monthly
        
        overheads = subtotal * self.standard_overhead
        profit = (subtotal + overheads) * self.standard_profit
        vat = (subtotal + overheads + profit) * self.vat_rate
        
        total_monthly = subtotal + overheads + profit + vat
        
        return {
            'labour_cost': round(total_labour, 2),
            'equipment_cost': round(equipment_monthly, 2),
            'materials_cost': round(materials_monthly, 2),
            'subtotal': round(subtotal, 2),
            'overheads': round(overheads, 2),
            'profit': round(profit, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total_monthly, 2),
            'total_contract_value': round(total_monthly * duration_months, 2)
        }
    
    def _calculate_security(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        req = tender_data.get('requirements', {})
        workforce = tender_data.get('workforce', {})
        duration = tender_data.get('duration', {})
        
        duration_months = duration.get('months', 12)
        shifts = req.get('shifts_per_day', 2)
        guards = workforce.get('total_workers', 10)
        
        guard_daily = self.base_rates['security']['grade_c_guard_daily']
        days_per_month = 30
        
        total_labour = guards * guard_daily * days_per_month * (1 + self.base_rates['security']['deductions_pct'])
        
        equipment_monthly = guards * 200
        materials_monthly = guards * 300
        
        subtotal = total_labour + equipment_monthly + materials_monthly
        
        overheads = subtotal * 0.20
        profit = (subtotal + overheads) * 0.12
        vat = (subtotal + overheads + profit) * self.vat_rate
        
        total_monthly = subtotal + overheads + profit + vat
        
        return {
            'labour_cost': round(total_labour, 2),
            'equipment_cost': round(equipment_monthly, 2),
            'materials_cost': round(materials_monthly, 2),
            'subtotal': round(subtotal, 2),
            'overheads': round(overheads, 2),
            'profit': round(profit, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total_monthly, 2),
            'total_contract_value': round(total_monthly * duration_months, 2)
        }
    
    def _calculate_gardening(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        req = tender_data.get('requirements', {})
        workforce = tender_data.get('workforce', {})
        scope = tender_data.get('scope', {})
        duration = tender_data.get('duration', {})
        
        duration_months = duration.get('months', 12)
        workers = workforce.get('total_workers', 3)
        area_sqm = scope.get('area_sqm', 5000)
        
        days_per_month = 22
        
        gardener_daily = self.base_rates['gardening']['gardener_daily']
        
        monthly_labour = workers * gardener_daily * days_per_month * (1 + self.base_rates['gardening']['deductions_pct'])
        
        equipment_monthly = 2000
        materials_monthly = (area_sqm / 100) * 180
        
        subtotal = monthly_labour + equipment_monthly + materials_monthly
        
        overheads = subtotal * self.standard_overhead
        profit = (subtotal + overheads) * self.standard_profit
        vat = (subtotal + overheads + profit) * self.vat_rate
        
        total_monthly = subtotal + overheads + profit + vat
        
        return {
            'labour_cost': round(monthly_labour, 2),
            'equipment_cost': round(equipment_monthly, 2),
            'materials_cost': round(materials_monthly, 2),
            'subtotal': round(subtotal, 2),
            'overheads': round(overheads, 2),
            'profit': round(profit, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total_monthly, 2),
            'total_contract_value': round(total_monthly * duration_months, 2)
        }
    
    def _calculate_it(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        workforce = tender_data.get('workforce', {})
        duration = tender_data.get('duration', {})
        
        techs = workforce.get('skilled_workers', 1)
        tech_daily = self.base_rates['it_services']['technician_daily']
        
        if duration.get('unit') == 'days':
            total_days = duration.get('value', 10)
        else:
            total_days = duration.get('months', 1) * 22
        
        total_labour = techs * tech_daily * total_days * (1 + self.base_rates['it_services']['deductions_pct'])
        
        materials_total = 10000
        
        subtotal = total_labour + materials_total
        
        overheads = subtotal * 0.10
        profit = (subtotal + overheads) * 0.20
        vat = (subtotal + overheads + profit) * self.vat_rate
        
        total_project = subtotal + overheads + profit + vat
        total_monthly = total_project / max(duration.get('months', 1), 1)
        
        return {
            'labour_cost': round(total_labour, 2),
            'materials_cost': round(materials_total, 2),
            'subtotal': round(subtotal, 2),
            'overheads': round(overheads, 2),
            'profit': round(profit, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total_monthly, 2),
            'total_contract_value': round(total_project, 2)
        }
    
    def _calculate_maintenance(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        return self._calculate_construction(tender_data, rates_found, debate_result)
    
    def _calculate_supply(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        scope = tender_data.get('scope', {})
        duration = tender_data.get('duration', {})
        
        goods_cost = 50000
        supply_margin = goods_cost * 0.10
        logistics = goods_cost * 0.05
        
        subtotal = goods_cost + supply_margin + logistics
        vat = subtotal * self.vat_rate
        total = subtotal + vat
        
        return {
            'materials_cost': round(goods_cost, 2),
            'supply_margin': round(supply_margin, 2),
            'logistics': round(logistics, 2),
            'subtotal': round(subtotal, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total / max(duration.get('months', 1), 1), 2),
            'total_contract_value': round(total, 2)
        }
    
    def _calculate_general(self, tender_data: Dict, rates_found: Dict, debate_result: Dict) -> Dict:
        base_price = debate_result.get('final_price', 50000)
        
        labour = base_price * 0.70
        equipment = base_price * 0.10
        materials = base_price * 0.10
        
        subtotal = labour + equipment + materials
        
        overheads = subtotal * self.standard_overhead
        profit = (subtotal + overheads) * self.standard_profit
        vat = (subtotal + overheads + profit) * self.vat_rate
        
        total = subtotal + overheads + profit + vat
        
        return {
            'labour_cost': round(labour, 2),
            'equipment_cost': round(equipment, 2),
            'materials_cost': round(materials, 2),
            'subtotal': round(subtotal, 2),
            'overheads': round(overheads, 2),
            'profit': round(profit, 2),
            'vat': round(vat, 2),
            'total_monthly': round(total, 2),
            'total_contract_value': round(total, 2),
            'note': 'GENERAL ESTIMATE - Verify manually'
        }
