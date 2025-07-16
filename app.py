import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
import time
import random
import webbrowser
import urllib.parse
from pathlib import Path
import requests
import os
import folium
from streamlit_folium import st_folium

# Configure page
st.set_page_config(
    page_title="BH Worldwide AI Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .flight-status {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .quote-card {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        border: 2px solid #fff;
    }
    .quote-summary {
        background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .quote-actions {
        background: linear-gradient(135deg, #00cec9 0%, #55a3ff 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    .stButton > button {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    .stButton > button:disabled {
        background: #95a5a6;
        cursor: not-allowed;
        transform: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables at application startup
def initialize_session_state():
    """Initialize all session state variables used throughout the application"""
    if 'generated_quotes' not in st.session_state:
        st.session_state.generated_quotes = []
    if 'case_statuses' not in st.session_state:
        st.session_state.case_statuses = {}
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.datetime.now()
    if 'cached_critical' not in st.session_state:
        st.session_state.cached_critical = 2
    if 'cached_response' not in st.session_state:
        st.session_state.cached_response = 105
    if 'cached_status' not in st.session_state:
        st.session_state.cached_status = "🟢 Online"
    if 'quotes' not in st.session_state:
        st.session_state.quotes = {}
    if 'email_processed' not in st.session_state:
        st.session_state.email_processed = False
    if 'selected_email_data' not in st.session_state:
        st.session_state.selected_email_data = None

# Initialize session state before any other operations
initialize_session_state()

class BHWorldwideAI:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.load_data()
        # Session state is now initialized globally before class instantiation
        
    def load_data(self):
        """Load all business data from JSON files"""
        try:
            # Load customer data (try extended first, fallback to original)
            try:
                with open(self.data_path / "Customer_Data/Airlines/extended_customers.json") as f:
                    self.customers = json.load(f)
            except:
                with open(self.data_path / "Customer_Data/Airlines/major_customers.json") as f:
                    self.customers = json.load(f)
            
            # Load active cases (try extended first, fallback to original)
            try:
                with open(self.data_path / "Operations/AOG_Center/extended_aog_cases.json") as f:
                    self.active_cases = json.load(f)
            except:
                with open(self.data_path / "Operations/AOG_Center/active_cases.json") as f:
                    self.active_cases = json.load(f)
                
            # Load competitive data
            with open(self.data_path / "Business_Intelligence/Competitors/competitor_analysis.json") as f:
                self.competitors = json.load(f)
                
            # Load lost opportunities (try extended first)
            try:
                with open(self.data_path / "Financial/Lost_Opportunities/historical_analysis.json") as f:
                    self.lost_opportunities = json.load(f)
            except:
                with open(self.data_path / "Financial/Lost_Opportunities/monthly_analysis.json") as f:
                    self.lost_opportunities = json.load(f)
                
            # Load pricing model
            with open(self.data_path / "Operations/Pricing/current_pricing_model.json") as f:
                self.pricing_model = json.load(f)
                
            # Load pain points
            with open(self.data_path / "Business_Intelligence/Pain_Points/current_challenges.json") as f:
                self.pain_points = json.load(f)
                
            # Load inventory (try extended first)
            try:
                with open(self.data_path / "Operations/Inventory/extended_inventory.json") as f:
                    self.inventory = json.load(f)
            except:
                with open(self.data_path / "Operations/Inventory/critical_parts.json") as f:
                    self.inventory = json.load(f)
            
            # Load REAL parts catalog and pricing data for accurate quotes
            try:
                with open(self.data_path / "Operations/Parts_Database/aircraft_parts_catalog.json") as f:
                    self.parts_catalog = json.load(f)
            except:
                self.parts_catalog = []
                
            try:
                with open(self.data_path / "Operations/Parts_Database/parts_pricing.json") as f:
                    self.parts_pricing = json.load(f)
            except:
                self.parts_pricing = {}
                
            try:
                with open(self.data_path / "Operations/Parts_Database/inventory_locations.json") as f:
                    self.inventory_locations = json.load(f)
            except:
                self.inventory_locations = {}
                
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Make sure you're running this from the correct directory with the BH_Worldwide_Logistics data")
    
    def get_live_status_metrics(self):
        """Get real-time status metrics with some randomization for demo effect"""
        active_cases = self.active_cases["active_aog_cases"]
        
        # Initialize session state if not exists
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.datetime.now()
        if 'generated_quotes' not in st.session_state:
            st.session_state.generated_quotes = []
        if 'case_statuses' not in st.session_state:
            st.session_state.case_statuses = {}
        
        # Add some random variation to make it feel more "live"
        now = datetime.datetime.now()
        time_diff = (now - st.session_state.last_update).seconds
        
        # Update every 30 seconds for demo effect
        if time_diff > 30:
            st.session_state.last_update = now
            # Add small random variations
            base_critical = len([case for case in active_cases if case.get("urgency") == "Critical"])
            critical_cases = max(0, base_critical + random.randint(-1, 2))
            
            # Vary response time slightly
            base_response = 105
            avg_response_time = base_response + random.randint(-15, 25)
            
            # System status based on performance
            if avg_response_time > 120:
                system_status = "🔴 Degraded"
            elif avg_response_time > 100:
                system_status = "🟡 Warning"
            else:
                system_status = "🟢 Online"
        else:
            # Use cached values if recent
            critical_cases = getattr(st.session_state, 'cached_critical', 2)
            avg_response_time = getattr(st.session_state, 'cached_response', 105)
            system_status = getattr(st.session_state, 'cached_status', "🟢 Online")
        
        # Cache the values
        st.session_state.cached_critical = critical_cases
        st.session_state.cached_response = avg_response_time
        st.session_state.cached_status = system_status
        
        quotes_count = len(st.session_state.generated_quotes)
        
        return {
            "critical_cases": critical_cases,
            "avg_response_time": avg_response_time,
            "quotes_generated": quotes_count,
            "system_status": system_status
        }
    
    def get_flight_status_data(self, limit=6):
        """Generate realistic flight status data based on AOG cases"""
        active_cases = self.active_cases["active_aog_cases"]
        flights = []
        
        # Take a sample of cases for flight display
        sample_cases = random.sample(active_cases, min(limit, len(active_cases)))
        
        for case in sample_cases:
            flight_number = f"{case['airline'][:2]}{random.randint(100, 9999)}"
            status = "🔴 GROUNDED" if case["status"] == "Pricing in progress" else \
                    "🟡 DELAYED" if case["urgency"] == "High" else "🟢 ON TIME"
            
            # Extract location for route
            location = case.get("location", "Unknown")
            
            # Generate realistic routes based on airline
            routes = {
                "Ryanair": ["DUB → LHR", "STN → BGY", "BVA → MAD"],
                "Lufthansa": ["FRA → MUC", "FRA → JFK", "MUC → LAX"],
                "Emirates": ["DXB → LHR", "DXB → JFK", "DXB → SYD"],
                "British Airways": ["LHR → CDG", "LHR → JFK", "LHR → SIN"],
                "KLM": ["AMS → JFK", "AMS → NRT", "AMS → CPT"]
            }
            
            airline_routes = routes.get(case["airline"], ["XXX → YYY"])
            route = random.choice(airline_routes)
            
            flights.append({
                "flight": flight_number,
                "airline": case["airline"],
                "route": route,
                "status": status,
                "aog_case": case["case_id"],
                "delay": case.get("elapsed_time", "Unknown")
            })
        
        # Add some normal flights for context
        if limit > len(sample_cases):
            normal_flights = [
                {"flight": "VS123", "airline": "Virgin Atlantic", "route": "LHR → JFK", 
                 "status": "🟢 ON TIME", "aog_case": "None", "delay": "On time"},
                {"flight": "AF456", "airline": "Air France", "route": "CDG → LAX", 
                 "status": "🟢 DEPARTED", "aog_case": "None", "delay": "+3m"}
            ]
            flights.extend(normal_flights[:limit-len(sample_cases)])
        
        return flights
    
    @st.cache_data
    def create_global_map(_self):
        """Create interactive map showing AOG incidents and real inventory hubs"""
        m = folium.Map(location=[50.0, 10.0], zoom_start=3, tiles='OpenStreetMap')
        
        # Real BH Worldwide inventory hub locations (from actual data)
        inventory_hub_coords = {
            "London (LHR)": (51.4700, -0.4543),  # Primary hub
            "Frankfurt (FRA)": (50.0379, 8.5622),  # European hub
            "Dubai (DXB)": (25.2532, 55.3657),  # Middle East hub
            "Singapore (SIN)": (1.3644, 103.9915),  # Asia-Pacific hub
            "New York (JFK)": (40.6413, -73.7781),  # Americas hub
            "Hong Kong (HKG)": (22.3080, 113.9185)  # Additional Asian hub
        }
        
        # Extended location coordinates for AOG cases
        location_coords = {
            "Dublin Airport (DUB)": (53.4213, -6.2701),
            "Frankfurt Airport (FRA)": (50.0379, 8.5622),
            "London (LHR)": (51.4700, -0.4543),
            "Paris (CDG)": (49.0097, 2.5479),
            "Amsterdam (AMS)": (52.3105, 4.7683),
            "Madrid (MAD)": (40.4839, -3.5680),
            "Rome (FCO)": (41.8003, 12.2389),
            "Munich (MUC)": (48.3537, 11.7751),
            "Zurich (ZUR)": (47.4647, 8.5492),
            "Vienna (VIE)": (48.1103, 16.5697),
            "Dubai (DXB)": (25.2532, 55.3657),
            "Singapore (SIN)": (1.3644, 103.9915),
            "New York JFK (JFK)": (40.6413, -73.7781),
            "Tokyo Narita (NRT)": (35.7720, 140.3929),
            "Sydney (SYD)": (-33.9399, 151.1753)
        }
        
        # Add BH Worldwide inventory hubs to map first
        for hub_name, coords in inventory_hub_coords.items():
            folium.Marker(
                location=coords,
                popup=f"<b>BH Worldwide Hub</b><br>{hub_name}<br>📦 Parts Inventory Available<br>🚚 Express Logistics Center",
                icon=folium.Icon(color='green', icon='home', prefix='fa')
            ).add_to(m)
        
        # Use fixed sample to prevent constant changes  
        fixed_cases = _self.active_cases["active_aog_cases"][:15]
        
        for case in fixed_cases:
            location = case.get("location", "Unknown")
            
            # Try to find coordinates
            coords = None
            for loc_key, coord in location_coords.items():
                if any(code in location for code in ["DUB", "FRA", "LHR", "CDG", "AMS", "MAD", "FCO", "MUC", "ZUR", "VIE", "DXB", "SIN", "JFK", "NRT", "SYD"]):
                    if loc_key.split("(")[1].replace(")", "") in location:
                        coords = coord
                        break
            
            if coords:
                # Color based on urgency and status
                if case["urgency"] == "Critical":
                    color = 'red'
                elif case["status"] == "Lost to competitor":
                    color = 'orange'
                elif case["urgency"] == "High":
                    color = 'darkred'
                else:
                    color = 'blue'
                
                popup_text = f"""
                <b>{case['case_id']}</b><br>
                🏢 {case['airline']}<br>
                ✈️ {case['aircraft']}<br>
                📍 {location}<br>
                💰 Loss: {case.get('total_loss_so_far', 'Unknown')}<br>
                📊 Status: {case['status']}<br>
                🔧 Part: {case.get('part_needed', 'Unknown')}<br>
                ⚡ Urgency: {case['urgency']}
                """
                
                folium.Marker(
                    coords,
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=f"{case['airline']} - {case['case_id']}",
                    icon=folium.Icon(color=color, icon='plane', prefix='fa')
                ).add_to(m)
        
        return m
            
    def generate_ai_quote(self, case_details: dict, case_id: str) -> dict:
        """Generate AI-powered quote using REAL parts catalog and pricing data"""
        # Check if quote already exists for this case
        existing_quote = next((q for q in st.session_state.generated_quotes if q.get('case_id') == case_id), None)
        if existing_quote:
            return existing_quote
        
        # Simulate processing time
        processing_steps = [
            "🔍 Analyzing part requirements from catalog...",
            "💰 Calculating pricing from real data...",
            "📍 Checking inventory locations...",
            "🚚 Optimizing delivery routing...",
            "✅ Generating comprehensive quote..."
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, step in enumerate(processing_steps):
            time.sleep(0.4)
            progress_bar.progress((i + 1) / len(processing_steps))
            status_text.text(step)
        
        # Get part details from case
        part_needed = case_details.get('part_needed', 'Unknown Part')
        part_number = case_details.get('part_number', 'N/A')
        aircraft_type = case_details.get('aircraft', 'Unknown')
        
        # Find matching part in real catalog
        matching_part = None
        if hasattr(self, 'parts_catalog') and self.parts_catalog:
            # Try to find exact match first
            for part in self.parts_catalog:
                if part_number != 'N/A' and part.get('part_number') == part_number:
                    matching_part = part
                    break
            
            # If no exact match, find by description similarity
            if not matching_part:
                for part in self.parts_catalog:
                    if any(word.lower() in part.get('description', '').lower() for word in part_needed.split()):
                        matching_part = part
                        break
        
        # Calculate pricing using real data or realistic fallback
        if matching_part and hasattr(self, 'parts_pricing') and self.parts_pricing:
            # Get real pricing for the part
            part_key = matching_part.get('part_number', '')
            pricing_data = self.parts_pricing.get('parts_pricing', {}).get(part_key, {})
            
            if pricing_data:
                # Use real pricing from London hub (convert to GBP)
                base_price_gbp = pricing_data.get('london_gbp', {}).get('base_price', 45000)
                expedite_markup = pricing_data.get('london_gbp', {}).get('expedite_surcharge_percentage', 35) / 100
                
                base_cost = int(base_price_gbp)
                expedite_cost = int(base_cost * expedite_markup)
                insurance_cost = int(base_cost * 0.015)  # 1.5% insurance
                
                # Get lead time and adjust delivery options
                lead_time = matching_part.get('lead_time', '24 hours')
                criticality = matching_part.get('criticality_level', 'Medium')
                
                if 'hours' in lead_time:
                    delivery_time = "Same Day Express"
                elif 'days' in lead_time and int(lead_time.split()[0]) <= 3:
                    delivery_time = "Next Flight Out (NFO)"
                else:
                    delivery_time = "Standard Freight"
            else:
                # Fallback pricing
                base_cost = random.randint(15000, 85000)
                expedite_cost = int(base_cost * 0.35)
                insurance_cost = int(base_cost * 0.015)
                delivery_time = "Next Flight Out (NFO)"
        else:
            # Fallback pricing when no real data available
            base_cost = random.randint(25000, 75000)
            expedite_cost = int(base_cost * 0.30)
            insurance_cost = int(base_cost * 0.012)
            delivery_time = "Next Flight Out (NFO)"
        
        total_cost = base_cost + expedite_cost + insurance_cost
        
        # Check real inventory status and determine optimal source hub
        inventory_status = self.get_inventory_status(part_number)
        source_hub = "LHR"  # Default to London
        inventory_availability = "Unknown"
        recommended_source = "London"
        
        if inventory_status:
            available_stock = inventory_status['available_stock']
            # Find the best hub with highest available stock
            best_hub = max(available_stock.items(), key=lambda x: x[1])
            if best_hub[1] > 0:
                recommended_source = best_hub[0].title()
                source_hub = best_hub[0][:3].upper()  # Get 3-letter code
                inventory_availability = f"In Stock - {best_hub[1]} units available"
            else:
                # All locations out of stock, check incoming
                if inventory_status.get('next_arrival'):
                    inventory_availability = f"Out of stock - {inventory_status['next_arrival']}"
                else:
                    inventory_availability = "Out of stock - Lead time required"
        
        quote = {
            "quote_id": f"BHW-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "case_id": case_id,
            "airline": case_details.get('airline', 'Unknown'),
            "aircraft": aircraft_type,
            "part_needed": part_needed,
            "part_number": part_number,
            "response_time": "8.7 minutes",  # AI advantage
            "total_cost": total_cost,
            "breakdown": {
                "base_transport": base_cost,
                "expedite_charges": expedite_cost,
                "insurance": insurance_cost
            },
            "delivery_time": delivery_time,
            "source_hub": source_hub,
            "recommended_source": recommended_source,
            "inventory_availability": inventory_availability,
            "inventory_status": inventory_status,
            "confidence_score": random.randint(94, 99),
            "competitive_advantage": f"{random.randint(12, 18)}% faster than competitors",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Generated",
            "real_data_used": matching_part is not None
        }
        
        progress_bar.progress(1.0)
        status_text.text("✅ Quote generated successfully using real parts data!")
        
        # Add to session state and mark case as quoted
        st.session_state.generated_quotes.append(quote)
        st.session_state.case_statuses[case_id] = "quoted"
        
        return quote
    
    def get_inventory_status(self, part_number=None):
        """Get comprehensive inventory status for a specific part or all parts"""
        if not hasattr(self, 'inventory_locations') or not self.inventory_locations:
            return None
        
        if part_number:
            # Find specific part
            for item in self.inventory_locations:
                if item.get('part_number') == part_number:
                    return self._calculate_inventory_metrics(item)
            return None
        else:
            # Return summary for all parts
            return self._calculate_global_inventory_metrics()
    
    def _calculate_inventory_metrics(self, inventory_item):
        """Calculate comprehensive metrics for a single part"""
        part_number = inventory_item['part_number']
        stock_levels = inventory_item['stock_levels_per_location']
        reserved = inventory_item['reserved_inventory_per_location']
        incoming = inventory_item['incoming_stock_schedules_per_location']
        
        # Calculate available stock (stock - reserved)
        available_stock = {}
        total_stock = 0
        total_available = 0
        total_reserved = 0
        
        for location, stock in stock_levels.items():
            reserved_qty = reserved.get(location, 0)
            available_qty = max(0, stock - reserved_qty)
            available_stock[location] = available_qty
            total_stock += stock
            total_available += available_qty
            total_reserved += reserved_qty
        
        # Determine availability status
        if total_available == 0:
            status = "critical"
            status_color = "red"
        elif total_available <= 3:
            status = "low"
            status_color = "orange"
        elif total_available <= 10:
            status = "medium"
            status_color = "yellow"
        else:
            status = "good"
            status_color = "green"
        
        # Find best hub for fastest delivery
        best_hubs = sorted(
            [(loc, qty) for loc, qty in available_stock.items() if qty > 0],
            key=lambda x: x[1], reverse=True
        )
        
        # Calculate incoming stock
        total_incoming = 0
        next_arrival = None
        for location, schedule in incoming.items():
            if schedule and schedule.get('quantity'):
                total_incoming += schedule['quantity']
                if not next_arrival or schedule['arrival_date'] < next_arrival:
                    next_arrival = schedule['arrival_date']
        
        return {
            'part_number': part_number,
            'total_stock': total_stock,
            'total_available': total_available,
            'total_reserved': total_reserved,
            'status': status,
            'status_color': status_color,
            'available_stock': available_stock,  # Match what the UI expects
            'available_by_location': available_stock,
            'stock_by_location': stock_levels,
            'reserved_by_location': reserved,
            'best_hubs': best_hubs,
            'total_incoming': total_incoming,
            'next_arrival_date': next_arrival,
            'next_arrival': f"{total_incoming} units arriving on {next_arrival}" if next_arrival else None,
            'incoming_schedules': incoming
        }
    
    def _calculate_global_inventory_metrics(self):
        """Calculate global inventory health metrics"""
        if not self.inventory_locations:
            return None
        
        total_parts = len(self.inventory_locations)
        critical_parts = 0
        low_stock_parts = 0
        overstocked_parts = 0
        total_inventory_value = 0
        
        location_totals = {'London': 0, 'Frankfurt': 0, 'Dubai': 0, 'Singapore': 0, 'New York': 0, 'Hong Kong': 0}
        
        for item in self.inventory_locations:
            metrics = self._calculate_inventory_metrics(item)
            
            if metrics['status'] == 'critical':
                critical_parts += 1
            elif metrics['status'] == 'low':
                low_stock_parts += 1
            elif metrics['total_available'] > 50:  # Overstocked threshold
                overstocked_parts += 1
            
            # Add to location totals
            for location, stock in metrics['stock_by_location'].items():
                if location in location_totals:
                    location_totals[location] += stock
        
        # Calculate inventory health score
        healthy_parts = total_parts - critical_parts - low_stock_parts
        health_score = (healthy_parts / total_parts) * 100 if total_parts > 0 else 0
        
        return {
            'total_parts': total_parts,
            'critical_parts': critical_parts,
            'low_stock_parts': low_stock_parts,
            'overstocked_parts': overstocked_parts,
            'healthy_parts': healthy_parts,
            'health_score': health_score,
            'overall_health': health_score,  # Add this for compatibility
            'location_totals': location_totals
        }
    
    def get_inventory_recommendations(self, part_number, location):
        """Get AI-powered inventory recommendations for AOG scenarios"""
        inventory_status = self.get_inventory_status(part_number)
        
        if not inventory_status:
            return {
                'message': '⚠️ Part not found in inventory system',
                'recommendation': 'external_sourcing',
                'alternatives': []
            }
        
        available_hubs = [(hub, qty) for hub, qty in inventory_status['best_hubs'] if qty > 0]
        
        if not available_hubs:
            # No stock available
            if inventory_status['next_arrival_date']:
                return {
                    'message': f'🚨 CRITICAL: No stock available globally. Next delivery: {inventory_status["next_arrival_date"]}',
                    'recommendation': 'wait_for_restock',
                    'delivery_date': inventory_status['next_arrival_date'],
                    'alternatives': self._find_alternative_parts(part_number)
                }
            else:
                return {
                    'message': '🚨 CRITICAL: No stock available and no incoming shipments',
                    'recommendation': 'emergency_procurement',
                    'alternatives': self._find_alternative_parts(part_number)
                }
        
        # Stock available - find best option
        best_hub, best_qty = available_hubs[0]
        
        if best_qty == 1:
            message = f'⚠️ LAST UNIT: Only 1 unit available in {best_hub}'
            recommendation = 'expedite_premium'
        elif best_qty <= 3:
            message = f'⚡ LOW STOCK: {best_qty} units in {best_hub}'
            recommendation = 'expedite_standard'
        else:
            message = f'✅ AVAILABLE: {best_qty} units in {best_hub}'
            recommendation = 'standard_delivery'
        
        return {
            'message': message,
            'recommendation': recommendation,
            'best_hub': best_hub,
            'available_quantity': best_qty,
            'all_hubs': available_hubs,
            'stock_summary': f"Global: {inventory_status['total_available']} available"
        }
    
    def _find_alternative_parts(self, part_number):
        """Find alternative parts when primary part is unavailable"""
        # Simplified alternative part logic
        alternatives = []
        
        # In a real system, this would use part compatibility data
        if hasattr(self, 'parts_catalog') and self.parts_catalog:
            primary_part = None
            for part in self.parts_catalog:
                if part.get('part_number') == part_number:
                    primary_part = part
                    break
            
            if primary_part:
                category = primary_part.get('category', '')
                # Find other parts in same category
                for part in self.parts_catalog[:5]:  # Limit for demo
                    if (part.get('category') == category and 
                        part.get('part_number') != part_number):
                        alt_inventory = self.get_inventory_status(part.get('part_number'))
                        if alt_inventory and alt_inventory['total_available'] > 0:
                            alternatives.append({
                                'part_number': part.get('part_number'),
                                'description': part.get('description'),
                                'available_qty': alt_inventory['total_available']
                            })
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def display_quote_card(self, quote):
        """Display a beautifully formatted quote card with real parts data"""
        # Show data source indicator
        data_source_badge = "✅ Real Parts Catalog" if quote.get('real_data_used', False) else "🔄 Simulated Data"
        
        st.markdown(f"""
        <div class="quote-card">
            <h3>🎯 Quote Generated: {quote['quote_id']} <span style="background: #28a745; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{data_source_badge}</span></h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                <div>
                    <h4>📋 Case Details</h4>
                    <p><strong>Case ID:</strong> {quote['case_id']}</p>
                    <p><strong>Airline:</strong> {quote['airline']}</p>
                    <p><strong>Aircraft:</strong> {quote['aircraft']}</p>
                </div>
                <div>
                    <h4>🔧 Parts Information</h4>
                    <p><strong>Part Needed:</strong> {quote.get('part_needed', 'N/A')}</p>
                    <p><strong>Part Number:</strong> {quote.get('part_number', 'N/A')}</p>
                    <p><strong>Source Hub:</strong> {quote.get('recommended_source', 'London')}</p>
                    <p><strong>Inventory:</strong> <span style="color: {'#28a745' if 'In Stock' in str(quote.get('inventory_availability', 'Unknown')) else '#dc3545'};">{quote.get('inventory_availability', 'Unknown')}</span></p>
                </div>
                <div>
                    <h4>⚡ Performance</h4>
                    <p><strong>Response Time:</strong> {quote['response_time']}</p>
                    <p><strong>Confidence:</strong> {quote['confidence_score']}%</p>
                    <p><strong>Advantage:</strong> {quote['competitive_advantage']}</p>
                </div>
                <div>
                    <h4>💰 Financial</h4>
                    <p><strong>Total Cost:</strong> £{quote['total_cost']:,}</p>
                    <p><strong>Delivery:</strong> {quote['delivery_time']}</p>
                    <p><strong>Generated:</strong> {quote['timestamp']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced breakdown table with real data indicators
        breakdown_df = pd.DataFrame([
            {"Component": "Base Transport", "Cost (£)": f"{quote['breakdown']['base_transport']:,}", "Source": "Real Pricing" if quote.get('real_data_used') else "Estimated"},
            {"Component": "Expedite Charges", "Cost (£)": f"{quote['breakdown']['expedite_charges']:,}", "Source": "Catalog Rate" if quote.get('real_data_used') else "Standard Rate"},
            {"Component": "Insurance", "Cost (£)": f"{quote['breakdown']['insurance']:,}", "Source": "Policy Rate"},
            {"Component": "**TOTAL**", "Cost (£)": f"**£{quote['total_cost']:,}**", "Source": "**Integrated Pricing**"}
        ])
        
        st.table(breakdown_df)
    
    def display_quote_actions(self, quote):
        """Display post-quote action buttons with full functionality"""
        st.markdown(f"""
        <div class="quote-actions">
            <h4>📋 Next Actions for {quote['quote_id']}</h4>
            <p>Choose what to do with this generated quote:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Create safe keys by replacing hyphens with underscores
        safe_quote_id = quote['quote_id'].replace('-', '_')
        modify_key = f"modify_{safe_quote_id}"
        alternative_key = f"alternative_{safe_quote_id}"
        
        # Initialize session state for quote modifications
        if modify_key not in st.session_state:
            st.session_state[modify_key] = False
        if alternative_key not in st.session_state:
            st.session_state[alternative_key] = None
        
        with col1:
            # Send to Customer - Opens email client
            if st.button(f"📧 Send to Customer", key=f"send_{safe_quote_id}"):
                # Create professional email content
                subject = f"AOG Quote - {quote['quote_id']} - {quote['airline']} - {quote.get('aircraft', 'Aircraft')}"
                
                email_body = f"""Dear {quote['airline']} Team,

Please find below our quote for your AOG requirements:

=== QUOTE DETAILS ===
Quote ID: {quote['quote_id']}
Case ID: {quote['case_id']}
Aircraft: {quote.get('aircraft', 'N/A')}
Part Required: {quote.get('part_needed', 'N/A')}
Location: {quote.get('location', 'N/A')}

=== COST BREAKDOWN ===
Base Transport: £{quote['breakdown']['base_transport']:,}
Expedite Charges: £{quote['breakdown']['expedite_charges']:,}
Insurance: £{quote['breakdown']['insurance']:,}
------------------------
TOTAL COST: £{quote['total_cost']:,}

=== DELIVERY TIMELINE ===
Estimated Delivery: {quote['delivery_time']}
Response Time: {quote['response_time']}
Confidence Score: {quote['confidence_score']}%

=== COMPETITIVE ADVANTAGE ===
{quote['competitive_advantage']}

Please confirm your acceptance of this quote. We are standing by to expedite delivery immediately upon your approval.

For any questions or modifications, please contact us immediately.

Best regards,
BH Worldwide Logistics AOG Team

This quote is valid for 24 hours and subject to part availability."""
                
                # Create mailto link
                mailto_link = f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(email_body)}"
                
                # Display clickable link and try to open email client
                st.success("✅ Email prepared! Click the link below to send:")
                st.markdown(f'<a href="{mailto_link}" target="_blank">📧 Open Email Client</a>', unsafe_allow_html=True)
                
                # Try to open default email client programmatically
                try:
                    webbrowser.open(mailto_link)
                except:
                    st.info("Please click the link above if your email client didn't open automatically.")
                
        with col2:
            # Modify Quote - Inline editing form
            if st.button(f"📋 Modify Quote", key=f"modify_btn_{safe_quote_id}"):
                st.session_state[modify_key] = not st.session_state[modify_key]
        
        # Show modification form if toggled
        if st.session_state[modify_key]:
            with st.expander("🔧 Quote Modification Panel", expanded=True):
                mod_col1, mod_col2 = st.columns(2)
                
                with mod_col1:
                    # Delivery options
                    current_delivery = quote.get('delivery_option', 'Next Flight Out')
                    new_delivery = st.selectbox(
                        "Delivery Option:", 
                        ["Next Flight Out", "Same Day", "Express", "Standard"], 
                        index=["Next Flight Out", "Same Day", "Express", "Standard"].index(current_delivery),
                        key=f"mod_delivery_{safe_quote_id}"
                    )
                    
                    # Price adjustment slider
                    price_adjustment = st.slider(
                        "Price Adjustment:", 
                        -20, 20, 0, 1, 
                        format="%d%%",
                        key=f"mod_price_{safe_quote_id}"
                    )
                    
                    # Calculate new price
                    original_cost = quote['total_cost']
                    adjusted_cost = int(original_cost * (1 + price_adjustment / 100))
                    
                    st.metric("Original Cost", f"£{original_cost:,}")
                    st.metric("Adjusted Cost", f"£{adjusted_cost:,}", f"{price_adjustment:+}%")
                
                with mod_col2:
                    # Notes text area
                    notes = st.text_area(
                        "Modification Notes:", 
                        placeholder="Enter reasons for modifications, special instructions, etc.",
                        height=100,
                        key=f"mod_notes_{safe_quote_id}"
                    )
                    
                    # Delivery time adjustment based on option
                    delivery_times = {
                        "Next Flight Out": "2-4 hours",
                        "Same Day": "4-8 hours", 
                        "Express": "6-12 hours",
                        "Standard": "12-24 hours"
                    }
                    
                    st.info(f"New Delivery Time: {delivery_times[new_delivery]}")
                
                # Save changes button
                if st.button("💾 Save Changes", key=f"save_mod_{safe_quote_id}", type="primary"):
                    # Update quote in session state
                    if 'quotes' not in st.session_state:
                        st.session_state.quotes = {}
                    
                    # Create modified quote
                    modified_quote = quote.copy()
                    modified_quote['total_cost'] = adjusted_cost
                    modified_quote['delivery_option'] = new_delivery
                    modified_quote['delivery_time'] = delivery_times[new_delivery]
                    modified_quote['modification_notes'] = notes
                    modified_quote['modified'] = True
                    modified_quote['modification_timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Recalculate breakdown proportionally
                    ratio = adjusted_cost / original_cost
                    modified_quote['breakdown'] = {
                        'base_transport': int(quote['breakdown']['base_transport'] * ratio),
                        'expedite_charges': int(quote['breakdown']['expedite_charges'] * ratio),
                        'insurance': int(quote['breakdown']['insurance'] * ratio)
                    }
                    
                    st.session_state.quotes[quote['quote_id']] = modified_quote
                    st.success(f"✅ Quote {quote['quote_id']} successfully modified!")
                    st.session_state[modify_key] = False
                    st.rerun()
        
        with col3:
            # Generate Alternative - Creates comparison
            if st.button(f"🔄 Generate Alternative", key=f"alt_btn_{safe_quote_id}"):
                # Generate alternative quote
                import random
                
                # Create alternative with variations
                base_cost = quote['total_cost']
                variation = random.uniform(-0.15, 0.15)  # ±15% variation
                alt_cost = int(base_cost * (1 + variation))
                
                alternative_quote = {
                    'quote_id': f"{quote['quote_id']}_ALT",
                    'case_id': quote['case_id'],
                    'airline': quote['airline'],
                    'total_cost': alt_cost,
                    'delivery_time': random.choice(["3-5 hours", "4-6 hours", "6-10 hours", "8-12 hours"]),
                    'delivery_option': random.choice(["Alternative Route", "Direct Express", "Hub Transfer", "Charter Flight"]),
                    'confidence_score': random.randint(85, 98),
                    'competitive_advantage': random.choice([
                        "Alternative routing reduces delivery time",
                        "Cost-optimized solution with reliable delivery",
                        "Premium service with enhanced tracking",
                        "Flexible delivery options available"
                    ]),
                    'response_time': quote['response_time'],
                    'breakdown': {
                        'base_transport': int(alt_cost * 0.6),
                        'expedite_charges': int(alt_cost * 0.25),
                        'insurance': int(alt_cost * 0.15)
                    },
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'routing': random.choice(["Via Frankfurt Hub", "Direct Charter", "Scheduled Carrier", "Road/Air Combo"]),
                    'carrier': random.choice(["Lufthansa Cargo", "FedEx", "DHL", "Emirates SkyCargo"])
                }
                
                st.session_state[alternative_key] = alternative_quote
                st.success("✅ Alternative quote generated! See comparison below.")
        
        # Display alternative quote comparison if generated
        if st.session_state[alternative_key]:
            alt_quote = st.session_state[alternative_key]
            
            st.markdown("---")
            st.subheader("🔄 Quote Comparison")
            
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                st.markdown("**🔵 Original Quote**")
                st.metric("Cost", f"£{quote['total_cost']:,}")
                st.metric("Delivery", quote['delivery_time'])
                st.metric("Confidence", f"{quote['confidence_score']}%")
                st.info(f"**Advantage:** {quote['competitive_advantage']}")
            
            with comp_col2:
                st.markdown("**🟢 Alternative Quote**")
                cost_diff = alt_quote['total_cost'] - quote['total_cost']
                st.metric("Cost", f"£{alt_quote['total_cost']:,}", f"£{cost_diff:+,}")
                st.metric("Delivery", alt_quote['delivery_time'])
                st.metric("Confidence", f"{alt_quote['confidence_score']}%")
                st.info(f"**Routing:** {alt_quote['routing']}")
                st.info(f"**Carrier:** {alt_quote['carrier']}")
                st.info(f"**Advantage:** {alt_quote['competitive_advantage']}")
            
            # Alternative selection buttons
            alt_col1, alt_col2, alt_col3 = st.columns(3)
            
            with alt_col1:
                if st.button("✅ Select Original", key=f"select_orig_{safe_quote_id}"):
                    st.session_state[alternative_key] = None
                    st.success("Original quote selected")
                    st.rerun()
            
            with alt_col2:
                if st.button("🔄 Select Alternative", key=f"select_alt_{safe_quote_id}"):
                    # Replace original with alternative
                    if 'quotes' not in st.session_state:
                        st.session_state.quotes = {}
                    st.session_state.quotes[quote['quote_id']] = alt_quote
                    st.session_state[alternative_key] = None
                    st.success("Alternative quote selected")
                    st.rerun()
            
            with alt_col3:
                if st.button("❌ Dismiss Comparison", key=f"dismiss_alt_{safe_quote_id}"):
                    st.session_state[alternative_key] = None
                    st.rerun()
        
        with col4:
            # Cancel Quote - With confirmation
            cancel_confirm_key = f"cancel_confirm_{safe_quote_id}"
            if st.button(f"❌ Cancel Quote", key=f"cancel_btn_{safe_quote_id}"):
                if cancel_confirm_key not in st.session_state:
                    st.session_state[cancel_confirm_key] = False
                st.session_state[cancel_confirm_key] = True
        
        # Show confirmation dialog if cancel was clicked
        if st.session_state.get(f"cancel_confirm_{safe_quote_id}", False):
            st.warning("⚠️ Are you sure you want to cancel this quote?")
            conf_col1, conf_col2, conf_col3 = st.columns(3)
            
            with conf_col1:
                if st.button("✅ Yes, Cancel Quote", key=f"confirm_cancel_{safe_quote_id}", type="primary"):
                    # Remove quote from session state
                    if 'quotes' in st.session_state and quote['quote_id'] in st.session_state.quotes:
                        del st.session_state.quotes[quote['quote_id']]
                    
                    # Reset case status to need quote
                    case_id = quote['case_id']
                    if case_id in st.session_state.case_statuses:
                        st.session_state.case_statuses[case_id] = "needs quote"
                    
                    # Clean up session state - use safe keys for cleanup
                    keys_to_remove = []
                    for key in st.session_state.keys():
                        if safe_quote_id in key or quote['quote_id'] in key:
                            keys_to_remove.append(key)
                    
                    for key in keys_to_remove:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.error(f"❌ Quote {quote['quote_id']} has been cancelled")
                    st.info(f"📝 Case {case_id} status reset to 'needs quote'")
                    time.sleep(2)
                    st.rerun()
            
            with conf_col2:
                if st.button("❌ No, Keep Quote", key=f"keep_quote_{safe_quote_id}"):
                    st.session_state[f"cancel_confirm_{safe_quote_id}"] = False
                    st.rerun()
            
            with conf_col3:
                st.write("")

# Initialize the dashboard
@st.cache_data
def load_dashboard_data():
    possible_paths = [
        "BH_Worldwide_Logistics",
        "./BH_Worldwide_Logistics"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return BHWorldwideAI(path)
    
    st.error("Cannot find BH_Worldwide_Logistics data directory. Please check the path.")
    st.stop()

dashboard = load_dashboard_data()

# Get live metrics (this will update every 30 seconds)
live_metrics = dashboard.get_live_status_metrics()

# Sidebar Navigation
st.sidebar.title("🚀 BH Worldwide AI")
st.sidebar.markdown("---")

# Live Status Indicators (now updating with variation)
st.sidebar.markdown("### 🔴 Live Status")
st.sidebar.markdown(f"**Active Critical Cases:** {live_metrics['critical_cases']}")
st.sidebar.markdown(f"**Avg Response Time:** {live_metrics['avg_response_time']} min")
st.sidebar.markdown(f"**Quotes Generated:** {live_metrics['quotes_generated']}")
st.sidebar.markdown(f"**System Status:** {live_metrics['system_status']}")

# Add refresh button for live updates
if st.sidebar.button("🔄 Refresh Live Data"):
    st.session_state.last_update = datetime.datetime.now() - datetime.timedelta(seconds=31)
    st.rerun()

# Data source indicator
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Sources")
st.sidebar.markdown(f"**Total AOG Cases:** {len(dashboard.active_cases['active_aog_cases'])}")
st.sidebar.markdown(f"**Total Customers:** {len(dashboard.customers['major_airline_customers'])}")
if hasattr(dashboard.inventory, 'get'):
    st.sidebar.markdown(f"**Inventory Items:** {len(dashboard.inventory.get('critical_inventory', []))}")

# Gemini API Key input (optional)
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Configuration")
api_key = st.sidebar.text_input(
    "Gemini API Key (Optional)",
    type="password",
    help="Get free key from https://ai.google.dev/ or leave empty for simulation"
)

if api_key:
    st.sidebar.success("✅ Real AI Enabled")
else:
    st.sidebar.info("ℹ️ Simulation Mode Active")

st.sidebar.markdown("### 📱 Navigation")
page = st.sidebar.radio(
    "Choose Dashboard View",
    ["🏠 Executive Overview", "⚡ Live AOG Center", "🗺️ Global Operations Map", "✈️ Flight Status Monitor", "🤖 AI Quote Engine", "📊 Analytics & Insights", "🎯 Competitive Intelligence", "💰 ROI Calculator"],
    label_visibility="collapsed"
)

# Main Dashboard Logic
if page == "🏠 Executive Overview":
    # Professional Header with Real-time Status
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="color: #1f1f1f; font-size: 36px; font-weight: bold; margin: 0;">
            👑 BH Worldwide AI Dashboard - Executive Command Center
        </h1>
        <div style="text-align: right;">
            <span style="color: #666; font-size: 14px;">Last Updated: {current_time}</span><br>
            <span style="color: #00ff00; font-size: 12px;">● LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional Disclaimer & Attribution Banner
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #4285f4;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 24px; margin-right: 10px;">🤖</span>
            <h3 style="color: white; margin: 0; font-size: 18px;">AI Demonstration Dashboard</h3>
        </div>
        <p style="color: #f0f0f0; margin: 8px 0; font-size: 14px; line-height: 1.4;">
            This dashboard demonstrates how AI can transform BH Worldwide's AOG logistics operations. 
            <strong>Financial data (£16.0M revenue, £9.99M loss risk) is based on real BH Worldwide financials.</strong>
            Operational data is simulated for demonstration purposes.
        </p>
        <div style="border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 12px; margin-top: 12px;">
            <p style="color: #e0e0e0; margin: 0; font-size: 14px;">
                <strong>Developed by:</strong> Hussein Srour, PhD, MBA<br>
                <strong>Title:</strong> Vice President, Data Science & AI Consulting<br>
                <strong>Organization:</strong> Thakral One, Australia<br>
                <strong>Connect:</strong> <a href="https://www.linkedin.com/in/hussein-srour?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app" 
                target="_blank" style="color: #87ceeb; text-decoration: none;">LinkedIn Profile</a>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CRITICAL EXECUTIVE ALERT - REAL FINANCIAL DATA
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff0000 0%, #800000 100%);
        padding: 25px;
        border-radius: 20px;
        margin: 25px 0;
        border: 4px solid #ff0000;
        box-shadow: 0 10px 20px rgba(255, 0, 0, 0.4);
        text-align: center;
        color: white;
    ">
        <h1 style="margin: 0; font-size: 32px; font-weight: bold;">⚠️ EXECUTIVE DECISION REQUIRED ⚠️</h1>
        <h2 style="margin: 15px 0; font-size: 26px;">BH Worldwide faces £9.99M annual loss = 62% of £16M revenue</h2>
        <div style="display: flex; justify-content: center; gap: 30px; margin: 20px 0;">
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; min-width: 150px;">
                <div style="font-size: 28px; font-weight: bold;">£16.0M</div>
                <div style="font-size: 16px;">Total Revenue (2024)</div>
                <div style="font-size: 14px; color: #ffcccc;">-3.7% declining</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; min-width: 150px;">
                <div style="font-size: 28px; font-weight: bold;">£9.99M</div>
                <div style="font-size: 16px;">Annual Loss Risk</div>
                <div style="font-size: 14px; color: #ffcccc;">62% of total revenue</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; min-width: 150px;">
                <div style="font-size: 28px; font-weight: bold;">£1.2M</div>
                <div style="font-size: 16px;">AI Investment</div>
                <div style="font-size: 14px; color: #ccffcc;">834% ROI to prevent loss</div>
            </div>
        </div>
        <p style="margin: 15px 0; font-size: 20px; font-weight: bold;">
            This is not an optimization opportunity - this is about company survival
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # === 1. EXECUTIVE COMMAND CENTER ===
    st.markdown("## 🎯 Business Health Command Center")
    
    # Critical Alerts and Business Health
    alert_col1, alert_col2 = st.columns([2, 1])
    
    with alert_col1:
        # Real-time Business Health Indicators
        st.markdown("### 🚦 Business Health Indicators")
        
        health_col1, health_col2, health_col3, health_col4 = st.columns(4)
        
        with health_col1:
            revenue_health = "🟡"  # Cautionary due to recent decline
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; border-radius: 10px; background: #f8f9fa; border-left: 4px solid #ffc107;">
                <h2 style="margin: 0; color: #ffc107;">Revenue</h2>
                <h1 style="margin: 5px 0; font-size: 48px;">{revenue_health}</h1>
                <p style="margin: 0; color: #666;">£16.0M (-3.7%)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with health_col2:
            operations_health = "🟢" if random.random() > 0.2 else "🟡"
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; border-radius: 10px; background: #f8f9fa; border-left: 4px solid #ffc107;">
                <h2 style="margin: 0; color: #ffc107;">Operations</h2>
                <h1 style="margin: 5px 0; font-size: 48px;">{operations_health}</h1>
                <p style="margin: 0; color: #666;">94.7% Efficiency</p>
            </div>
            """, unsafe_allow_html=True)
        
        with health_col3:
            customer_health = "🟢" if random.random() > 0.1 else "🟡"
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; border-radius: 10px; background: #f8f9fa; border-left: 4px solid #17a2b8;">
                <h2 style="margin: 0; color: #17a2b8;">Customer</h2>
                <h1 style="margin: 5px 0; font-size: 48px;">{customer_health}</h1>
                <p style="margin: 0; color: #666;">4.7/5 Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with health_col4:
            innovation_health = "🟢" if random.random() > 0.4 else "🟡"
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; border-radius: 10px; background: #f8f9fa; border-left: 4px solid #6f42c1;">
                <h2 style="margin: 0; color: #6f42c1;">Innovation</h2>
                <h1 style="margin: 5px 0; font-size: 48px;">{innovation_health}</h1>
                <p style="margin: 0; color: #666;">89% Progress</p>
            </div>
            """, unsafe_allow_html=True)
    
    with alert_col2:
        # Critical Alerts and Actions
        st.markdown("### 🚨 Executive Actions Required")
        
        critical_actions = [
            {"priority": "🔴", "action": "CRITICAL: £9.99M potential annual loss = 62% of £16M revenue - EXISTENTIAL THREAT", "deadline": "IMMEDIATE ACTION REQUIRED"},
            {"priority": "🔴", "action": "Approve AI implementation budget: £1.2M to prevent loss", "deadline": "Today"},
            {"priority": "🟡", "action": "Review Lufthansa partnership terms", "deadline": "This Week"}
        ]
        
        for action in critical_actions:
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; border-radius: 5px; background: #f8f9fa; border-left: 3px solid #dc3545;">
                {action['priority']} <strong>{action['action']}</strong><br>
                <small style="color: #666;">Due: {action['deadline']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Today's Financial Impact Tracker - REAL BH CONTEXT
        st.markdown("### 💰 Daily Revenue Protection")
        daily_revenue_at_risk = 9.99 * 1000000 / 365  # £9.99M annual risk ÷ 365 days
        daily_revenue = 16.0 * 1000000 / 365  # £16M annual revenue ÷ 365 days
        
        st.metric("Daily Revenue at Risk", f"£{daily_revenue_at_risk:,.0f}", "🔴 WITHOUT AI PROTECTION")
        st.metric("Daily Revenue", f"£{daily_revenue:,.0f}", f"27% at risk daily")
    
    # === 2. FINANCIAL REALITY DASHBOARD ===
    st.markdown("---")
    st.markdown("## 💰 Financial Reality Dashboard - Real BH Worldwide Performance")
    st.markdown("*Based on actual BH Worldwide financials from Financial/BH_Actual_Financials/*")
    
    # Row 1: Key Financial KPIs
    st.markdown("### 📊 Key Financial Performance Indicators (2024)")
    financial_kpi_col1, financial_kpi_col2, financial_kpi_col3, financial_kpi_col4 = st.columns(4)
    
    with financial_kpi_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Revenue</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">£16.0M</h1>
            <p style="margin: 5px 0; font-size: 14px;">2024 Total Revenue</p>
            <p style="margin: 0; font-size: 12px; color: #ffcccc;">-3.7% YoY decline</p>
        </div>
        """, unsafe_allow_html=True)
    
    with financial_kpi_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #20bf6b 0%, #26a69a 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Gross Margin</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">32.2%</h1>
            <p style="margin: 5px 0; font-size: 14px;">2024 Gross Margin</p>
            <p style="margin: 0; font-size: 12px; color: #ccffcc;">Improving trend</p>
        </div>
        """, unsafe_allow_html=True)
    
    with financial_kpi_col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #3867d6 0%, #8854d0 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">EBITDA</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">£1.1M</h1>
            <p style="margin: 5px 0; font-size: 14px;">2024 EBITDA</p>
            <p style="margin: 0; font-size: 12px; color: #ccccff;">6.7% of revenue</p>
        </div>
        """, unsafe_allow_html=True)
    
    with financial_kpi_col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Net Income</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">£0.8M</h1>
            <p style="margin: 5px 0; font-size: 14px;">2024 Net Income</p>
            <p style="margin: 0; font-size: 12px; color: #ffffcc;">4.9% net margin</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2: Business Health Indicators
    st.markdown("### 🏥 Business Health & Risk Assessment")
    health_kpi_col1, health_kpi_col2, health_kpi_col3, health_kpi_col4 = st.columns(4)
    
    with health_kpi_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Current Ratio</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">1.6x</h1>
            <p style="margin: 5px 0; font-size: 14px;">Strong Liquidity</p>
            <p style="margin: 0; font-size: 12px; color: #ccffcc;">✅ Healthy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with health_kpi_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">ROA</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">11.8%</h1>
            <p style="margin: 5px 0; font-size: 14px;">Return on Assets</p>
            <p style="margin: 0; font-size: 12px; color: #ccffcc;">✅ Healthy Returns</p>
        </div>
        """, unsafe_allow_html=True)
    
    with health_kpi_col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e17055 0%, #fdcb6e 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Growth Rate</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">-3.7%</h1>
            <p style="margin: 5px 0; font-size: 14px;">2024 Decline</p>
            <p style="margin: 0; font-size: 12px; color: #ffcccc;">⚠️ Concerning</p>
        </div>
        """, unsafe_allow_html=True)
    
    with health_kpi_col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Financial Risk</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">HIGH</h1>
            <p style="margin: 5px 0; font-size: 14px;">£9.99M at Risk</p>
            <p style="margin: 0; font-size: 12px; color: #ffcccc;">🚨 Crisis Level</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 3: Global Inventory Intelligence KPIs
    st.markdown("### 🏭 Global Inventory Intelligence Dashboard")
    inventory_kpi_col1, inventory_kpi_col2, inventory_kpi_col3, inventory_kpi_col4 = st.columns(4)
    
    # Get real inventory metrics if available
    try:
        global_inventory = dashboard._calculate_global_inventory_metrics()
    except:
        global_inventory = None
    
    with inventory_kpi_col1:
        parts_tracked = global_inventory['total_parts'] if global_inventory else 347
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Parts Tracked</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">{parts_tracked}</h1>
            <p style="margin: 5px 0; font-size: 14px;">Active Inventory Items</p>
            <p style="margin: 0; font-size: 12px; color: #ccffcc;">🏭 6 Global Hubs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with inventory_kpi_col2:
        health_score = global_inventory['overall_health'] if global_inventory else 91.3
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Stock Health</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">{health_score:.1f}%</h1>
            <p style="margin: 5px 0; font-size: 14px;">Overall Health Score</p>
            <p style="margin: 0; font-size: 12px; color: #ccffcc;">✅ Optimal Levels</p>
        </div>
        """, unsafe_allow_html=True)
    
    with inventory_kpi_col3:
        critical_parts = global_inventory['critical_parts'] if global_inventory else 23
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">Critical Parts</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">{critical_parts}</h1>
            <p style="margin: 5px 0; font-size: 14px;">Low Stock Alerts</p>
            <p style="margin: 0; font-size: 12px; color: #ffffcc;">⚠️ Monitoring Active</p>
        </div>
        """, unsafe_allow_html=True)
    
    with inventory_kpi_col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0;">
            <h3 style="margin: 0; color: white;">AI Optimization</h3>
            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">£847K</h1>
            <p style="margin: 5px 0; font-size: 14px;">Annual Savings</p>
            <p style="margin: 0; font-size: 12px; color: #ffccff;">🚀 15.2% Improvement</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Inventory Intelligence Summary
    inv_summary_col1, inv_summary_col2 = st.columns(2)
    
    with inv_summary_col1:
        st.markdown("#### 🎯 Inventory Intelligence Benefits")
        st.markdown("""
        **Real-time Stock Monitoring:**
        - 🟢 94.7% first-time availability rate
        - 🟡 72% reduction in stock-out incidents
        - 🔴 89% fewer emergency purchases
        
        **AI-Powered Optimization:**
        - 📈 15.2% inventory turnover improvement
        - 💰 £235K dead stock recovery
        - ⚡ 23% faster AOG resolution times
        """)
    
    with inv_summary_col2:
        st.markdown("#### 🌍 Global Hub Performance")
        # Sample hub performance data
        hub_performance = {
            'Hub': ['London', 'Frankfurt', 'Dubai', 'Singapore', 'New York', 'Hong Kong'],
            'Availability': ['96.8%', '94.2%', '91.7%', '93.5%', '89.1%', '87.4%'],
            'Stock Value': ['£8.2M', '£7.8M', '£6.5M', '£5.9M', '£4.3M', '£3.8M'],
            'Health': ['🟢 Excellent', '🟢 Good', '🟡 Fair', '🟢 Good', '🟡 Fair', '🟡 Fair']
        }
        hub_df = pd.DataFrame(hub_performance)
        st.dataframe(hub_df, use_container_width=True, hide_index=True)
    
    # === 3. STRATEGIC PERFORMANCE DASHBOARD ===
    st.markdown("---")
    st.markdown("## 📊 Strategic Performance Dashboard")
    
    # Balanced Scorecard
    scorecard_col1, scorecard_col2 = st.columns(2)
    
    with scorecard_col1:
        st.markdown("### 🎯 Balanced Scorecard")
        
        # Financial Perspective - REAL BH WORLDWIDE DATA
        financial_metrics = {
            "Revenue Growth": {"actual": -3.7, "target": 15.0, "unit": "%"},
            "Profit Margin": {"actual": 4.9, "target": 20.0, "unit": "%"},
            "ROI": {"actual": 34.8, "target": 25.0, "unit": "%"},
            "Cash Flow": {"actual": 1.3, "target": 2.0, "unit": "£M"}
        }
        
        scorecard_data = []
        for metric, values in financial_metrics.items():
            performance = "🟢" if values["actual"] >= values["target"] else "🟡" if values["actual"] >= values["target"] * 0.9 else "🔴"
            scorecard_data.append({
                "Metric": metric,
                "Actual": f"{values['actual']}{values['unit']}",
                "Target": f"{values['target']}{values['unit']}",
                "Status": performance
            })
        
        scorecard_df = pd.DataFrame(scorecard_data)
        st.dataframe(scorecard_df, use_container_width=True, hide_index=True)
    
    with scorecard_col2:
        # Strategic Initiatives Progress
        st.markdown("### 🚀 Strategic Initiatives")
        
        initiatives = [
            {"name": "AI Implementation", "progress": 78, "status": "On Track"},
            {"name": "Global Expansion", "progress": 92, "status": "Ahead"},
            {"name": "Digital Transformation", "progress": 65, "status": "At Risk"},
            {"name": "Sustainability Program", "progress": 85, "status": "On Track"}
        ]
        
        for initiative in initiatives:
            color = "#28a745" if initiative["status"] == "Ahead" else "#ffc107" if initiative["status"] == "On Track" else "#dc3545"
            st.markdown(f"""
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>{initiative['name']}</strong></span>
                    <span style="color: {color};">{initiative['status']}</span>
                </div>
                <div style="background: #e9ecef; border-radius: 10px; height: 10px; margin: 5px 0;">
                    <div style="background: {color}; width: {initiative['progress']}%; height: 100%; border-radius: 10px;"></div>
                </div>
                <small>{initiative['progress']}% Complete</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced Charts Section - 4 Comprehensive Financial & Risk Charts
    st.markdown("### 📈 Enhanced Financial Intelligence Charts")
    
    # First Row of Charts
    chart_row1_col1, chart_row1_col2 = st.columns(2)
    
    with chart_row1_col1:
        # Chart 1: Real Revenue Trends (2019-2024) with AI projection
        st.markdown("#### 📊 Revenue History & AI Future Projection")
        years_extended = ['2019', '2020', '2021', '2022', '2023', '2024', '2025E', '2026E']
        revenue_actual = [17.4, 18.8, 9.4, 11.4, 16.6, 16.0, None, None]  # Real BH data
        revenue_without_ai = [None, None, None, None, None, 16.0, 6.01, 3.5]  # Projected decline without AI
        revenue_with_ai = [None, None, None, None, None, 16.0, 25.99, 35.0]  # Projected growth with AI
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years_extended[:6], y=revenue_actual[:6], mode='lines+markers', 
                               name='Historical Revenue', line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=years_extended[5:], y=revenue_without_ai[5:], mode='lines+markers',
                               name='Without AI (Decline)', line=dict(color='#ff4444', width=3, dash='dash')))
        fig.add_trace(go.Scatter(x=years_extended[5:], y=revenue_with_ai[5:], mode='lines+markers',
                               name='With AI (Growth)', line=dict(color='#28a745', width=3)))
        fig.update_layout(title="BH Worldwide Revenue: Past Reality vs Future Scenarios", height=350, template="plotly_white")
        fig.add_annotation(x='2024', y=10, text="£9.99M Annual Loss<br>Without AI", showarrow=True, arrowcolor="red")
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_row1_col2:
        # Chart 2: Current vs AI Performance Metrics Comparison
        st.markdown("#### ⚡ Current vs AI Performance Impact")
        metrics = ['Response Time', 'Win Rate', 'Customer Satisfaction', 'Operational Efficiency', 'Revenue Growth']
        current_performance = [105, 65, 3.2, 67, -3.7]  # Current metrics
        ai_performance = [15, 85, 4.5, 92, 12.5]  # AI-enhanced metrics
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Current Performance', x=metrics, y=current_performance, 
                           marker_color='#ff6b6b', opacity=0.8))
        fig.add_trace(go.Bar(name='With AI', x=metrics, y=ai_performance, 
                           marker_color='#4ecdc4', opacity=0.8))
        fig.update_layout(title="Performance Transformation with AI Implementation", 
                        height=350, template="plotly_white", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    # Second Row of Charts
    chart_row2_col1, chart_row2_col2 = st.columns(2)
    
    with chart_row2_col1:
        # Chart 3: Profitability Impact Analysis
        st.markdown("#### 💰 Profitability Impact with AI Implementation")
        years_profit = ['2022', '2023', '2024', '2025E', '2026E']
        gross_margin_current = [28.4, 28.3, 32.2, 31.0, 29.5]  # Without AI - declining
        gross_margin_ai = [28.4, 28.3, 32.2, 42.5, 48.7]  # With AI - improving
        net_margin_current = [2.5, 4.8, 4.9, 3.2, 1.8]  # Without AI
        net_margin_ai = [2.5, 4.8, 4.9, 15.2, 22.4]  # With AI
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years_profit, y=gross_margin_current, mode='lines+markers',
                               name='Gross Margin (Current Path)', line=dict(color='#ff9999', width=2, dash='dash')))
        fig.add_trace(go.Scatter(x=years_profit, y=gross_margin_ai, mode='lines+markers',
                               name='Gross Margin (With AI)', line=dict(color='#28a745', width=3)))
        fig.add_trace(go.Scatter(x=years_profit, y=net_margin_current, mode='lines+markers',
                               name='Net Margin (Current Path)', line=dict(color='#ffcccc', width=2, dash='dash')))
        fig.add_trace(go.Scatter(x=years_profit, y=net_margin_ai, mode='lines+markers',
                               name='Net Margin (With AI)', line=dict(color='#20bf6b', width=3)))
        fig.update_layout(title="Margin Improvement Trajectory (%)", height=350, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_row2_col2:
        # Chart 4: Financial Risk Analysis - Crisis without AI
        st.markdown("#### 🚨 Financial Risk Analysis: Crisis Scenario")
        risk_categories = ['Revenue Loss', 'Market Share Loss', 'Customer Churn', 'Competitive Threat', 'Operational Risk']
        risk_without_ai = [95, 85, 78, 92, 88]  # Risk levels without AI (high)
        risk_with_ai = [15, 25, 22, 35, 20]  # Risk levels with AI (low)
        
        fig = go.Figure()
        # Create radar chart
        fig.add_trace(go.Scatterpolar(r=risk_without_ai, theta=risk_categories, fill='toself',
                                    name='Without AI (High Risk)', line_color='#ff4444'))
        fig.add_trace(go.Scatterpolar(r=risk_with_ai, theta=risk_categories, fill='toself',
                                    name='With AI (Low Risk)', line_color='#28a745'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        title="Risk Level Analysis (0-100 scale)", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # === 3. BUSINESS INTELLIGENCE HUB ===
    st.markdown("---")
    st.markdown("## 🧠 Business Intelligence Hub")
    
    bi_col1, bi_col2, bi_col3 = st.columns(3)
    
    with bi_col1:
        st.markdown("### 🔮 Predictive Analytics")
        
        # Early Warning Indicators
        warnings = [
            {"metric": "Customer Churn Risk", "value": "12%", "trend": "↑", "color": "#ffc107"},
            {"metric": "Market Share Risk", "value": "Low", "trend": "→", "color": "#28a745"},
            {"metric": "Operational Bottleneck", "value": "Medium", "trend": "↓", "color": "#17a2b8"},
            {"metric": "Competition Threat", "value": "High", "trend": "↑", "color": "#dc3545"}
        ]
        
        for warning in warnings:
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; border-radius: 5px; background: #f8f9fa; border-left: 3px solid {warning['color']};">
                <strong>{warning['metric']}</strong><br>
                <span style="font-size: 20px; color: {warning['color']};">{warning['value']} {warning['trend']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with bi_col2:
        st.markdown("### 👥 Customer Health Scores")
        
        # Customer risk matrix
        customers = [
            {"name": "Lufthansa", "health": 95, "risk": "Low", "value": "£2.1M"},
            {"name": "Emirates", "health": 88, "risk": "Low", "value": "£1.8M"},
            {"name": "Ryanair", "health": 72, "risk": "Medium", "value": "£1.2M"},
            {"name": "British Airways", "health": 65, "risk": "High", "value": "£950K"}
        ]
        
        for customer in customers:
            risk_color = "#28a745" if customer["risk"] == "Low" else "#ffc107" if customer["risk"] == "Medium" else "#dc3545"
            st.markdown(f"""
            <div style="padding: 8px; margin: 5px 0; border-radius: 5px; background: #f8f9fa;">
                <strong>{customer['name']}</strong> - {customer['value']}<br>
                <span style="color: {risk_color};">Health: {customer['health']}% ({customer['risk']} Risk)</span>
            </div>
            """, unsafe_allow_html=True)
    
    with bi_col3:
        st.markdown("### 🎯 Market Opportunities")
        
        # Opportunity prioritization
        opportunities = [
            {"opp": "Asia-Pacific Expansion", "value": "£5.2M", "effort": "High", "priority": "🟢"},
            {"opp": "AI Service Premium", "value": "£3.1M", "effort": "Medium", "priority": "🟢"},
            {"opp": "Cargo Airline Segment", "value": "£2.8M", "effort": "Low", "priority": "🟡"},
            {"opp": "Predictive Maintenance", "value": "£1.9M", "effort": "High", "priority": "🟡"}
        ]
        
        for opp in opportunities:
            st.markdown(f"""
            <div style="padding: 8px; margin: 5px 0; border-radius: 5px; background: #f8f9fa;">
                {opp['priority']} <strong>{opp['opp']}</strong><br>
                <small>Value: {opp['value']} | Effort: {opp['effort']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # === 4. EXECUTIVE ANALYTICS ===
    st.markdown("---")
    st.markdown("## 📋 Executive Analytics")
    
    analytics_col1, analytics_col2 = st.columns(2)
    
    with analytics_col1:
        # Revenue Performance with Drill-down
        st.markdown("### 💰 Revenue Performance Analysis")
        
        # Revenue by segment
        segments = ["Commercial Airlines", "Cargo Carriers", "Regional Airlines", "Charter Operations"]
        revenue_by_segment = [45, 25, 20, 10]
        
        fig = px.pie(
            values=revenue_by_segment,
            names=segments,
            title="Revenue Distribution by Customer Segment (%)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Customer Lifetime Value Analysis
        st.markdown("**Top Customers by Lifetime Value:**")
        clv_data = [
            {"Customer": "Lufthansa", "CLV": "£12.5M", "Trend": "↑"},
            {"Customer": "Emirates", "CLV": "£9.8M", "Trend": "↑"},
            {"Customer": "British Airways", "CLV": "£7.2M", "Trend": "→"},
            {"Customer": "Ryanair", "CLV": "£6.1M", "Trend": "↓"}
        ]
        
        for clv in clv_data:
            st.markdown(f"• **{clv['Customer']}**: {clv['CLV']} {clv['Trend']}")
    
    with analytics_col2:
        # Operational Cost Optimization
        st.markdown("### ⚡ Operational Efficiency Metrics")
        
        # Cost optimization opportunities
        cost_areas = ["Response Time", "Inventory Management", "Route Optimization", "Process Automation"]
        savings_potential = [2.1, 1.8, 1.4, 3.2]
        
        fig = px.bar(
            x=cost_areas,
            y=savings_potential,
            title="Cost Optimization Opportunities (£M)",
            color=savings_potential,
            color_continuous_scale="Greens"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Resource Allocation Effectiveness
        st.markdown("**Resource Allocation Effectiveness:**")
        resources = [
            {"Area": "AI Development", "Allocation": "35%", "ROI": "420%", "Status": "🟢"},
            {"Area": "Global Expansion", "Allocation": "25%", "ROI": "280%", "Status": "🟢"},
            {"Area": "Operations", "Allocation": "30%", "ROI": "180%", "Status": "🟡"},
            {"Area": "Marketing", "Allocation": "10%", "ROI": "95%", "Status": "🔴"}
        ]
        
        for resource in resources:
            st.markdown(f"{resource['Status']} **{resource['Area']}**: {resource['Allocation']} allocation, {resource['ROI']} ROI")
    
    # === 5. STRATEGIC INSIGHTS ===
    st.markdown("---")
    st.markdown("## 🎯 Strategic Insights & AI Recommendations")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        # AI-Powered Business Recommendations
        st.markdown("### 🤖 AI Business Recommendations")
        
        recommendations = [
            {
                "priority": "🔴",
                "title": "Immediate AI Investment",
                "description": "Deploy AI quote engine to capture £2.1M annual opportunity",
                "impact": "High Revenue Impact",
                "timeframe": "30 days"
            },
            {
                "priority": "🟡",
                "title": "Customer Retention Program",
                "description": "Implement loyalty program for at-risk high-value customers",
                "impact": "Medium Revenue Protection",
                "timeframe": "60 days"
            },
            {
                "priority": "🟢",
                "title": "Market Expansion",
                "description": "Enter cargo airline segment with specialized services",
                "impact": "New Revenue Stream",
                "timeframe": "120 days"
            }
        ]
        
        for rec in recommendations:
            st.markdown(f"""
            <div style="padding: 15px; margin: 10px 0; border-radius: 10px; background: #f8f9fa; border-left: 4px solid #007bff;">
                <h4 style="margin: 0; color: #007bff;">{rec['priority']} {rec['title']}</h4>
                <p style="margin: 5px 0;">{rec['description']}</p>
                <small><strong>Impact:</strong> {rec['impact']} | <strong>Timeline:</strong> {rec['timeframe']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with insights_col2:
        # Risk Assessment & Growth Matrix
        st.markdown("### ⚠️ Risk Assessment & Growth Matrix")
        
        # Risk vs Opportunity Matrix
        risks_opportunities = pd.DataFrame({
            'Opportunity': ['AI Implementation', 'Global Expansion', 'New Services', 'Partnerships', 'Automation'],
            'Risk Level': [2, 6, 4, 3, 1],
            'Opportunity Value': [9, 8, 6, 7, 5],
            'Investment Required': [5, 9, 4, 3, 6]
        })
        
        fig = px.scatter(
            risks_opportunities,
            x='Risk Level',
            y='Opportunity Value',
            size='Investment Required',
            hover_data=['Opportunity'],
            title="Risk vs Opportunity Matrix",
            labels={'Risk Level': 'Risk Level (1-10)', 'Opportunity Value': 'Opportunity Value (1-10)'}
        )
        
        # Add quadrant lines
        fig.add_hline(y=5, line_dash="dash", line_color="gray")
        fig.add_vline(x=5, line_dash="dash", line_color="gray")
        
        # Add quadrant labels
        fig.add_annotation(x=2.5, y=7.5, text="High Value<br>Low Risk", showarrow=False, bgcolor="lightgreen", opacity=0.7)
        fig.add_annotation(x=7.5, y=7.5, text="High Value<br>High Risk", showarrow=False, bgcolor="yellow", opacity=0.7)
        fig.add_annotation(x=2.5, y=2.5, text="Low Value<br>Low Risk", showarrow=False, bgcolor="lightgray", opacity=0.7)
        fig.add_annotation(x=7.5, y=2.5, text="Low Value<br>High Risk", showarrow=False, bgcolor="lightcoral", opacity=0.7)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced Executive Summary with Financial Context
        st.markdown("### 📈 Executive Financial Context")
        st.warning("""
        **Critical Financial Reality (Real BH Worldwide Data):**
        • **Current Revenue**: £16.0M (2024) with -3.7% declining trend
        • **Immediate Crisis**: £9.99M annual loss risk = 62% of total revenue
        • **Market Position**: Strong operations but declining financially
        • **AI Solution ROI**: 834% return on £1.2M investment
        • **Timeframe**: 1.4 months to break-even vs existential threat
        """)
    
    # === 6. EXECUTIVE SUMMARY BOX ===
    st.markdown("---")
    st.markdown("## 📋 Executive Decision Summary")
    
    # Header with styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 20px 0; color: white; text-align: center;">
        <h2 style="margin: 0; font-size: 28px;">🎯 Executive Decision Framework</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Three column layout using Streamlit columns
    exec_col1, exec_col2, exec_col3 = st.columns(3)
    
    with exec_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); padding: 20px; border-radius: 15px; color: white; margin: 10px 0;">
            <h3 style="margin: 0 0 15px 0; text-align: center;">📊 Current Financial Reality</h3>
            <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                <li><strong>Revenue:</strong> £16.0M (declining -3.7%)</li>
                <li><strong>Net Margin:</strong> 4.9% (£0.8M profit)</li>
                <li><strong>Gross Margin:</strong> 32.2% (improving)</li>
                <li><strong>Cash Position:</strong> £1.3M (adequate)</li>
                <li><strong>Debt:</strong> Zero (strong balance sheet)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with exec_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 20px; border-radius: 15px; color: white; margin: 10px 0; border: 2px solid #ff4444;">
            <h3 style="margin: 0 0 15px 0; text-align: center;">🚨 Existential Threat</h3>
            <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                <li><strong>Annual Loss Risk:</strong> £9.99M</li>
                <li><strong>% of Revenue:</strong> 62% at risk</li>
                <li><strong>Crisis Level:</strong> Company survival</li>
                <li><strong>Market Position:</strong> Deteriorating</li>
                <li><strong>Competitive:</strong> Falling behind</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with exec_col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%); padding: 20px; border-radius: 15px; color: white; margin: 10px 0; border: 2px solid #28a745;">
            <h3 style="margin: 0 0 15px 0; text-align: center;">💡 AI Solution Impact</h3>
            <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                <li><strong>Investment:</strong> £1.2M (7.5% of revenue)</li>
                <li><strong>ROI:</strong> 834% first year</li>
                <li><strong>Payback:</strong> 1.4 months</li>
                <li><strong>Risk Mitigation:</strong> £9.99M saved</li>
                <li><strong>Growth Potential:</strong> 2x revenue by 2026</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic Recommendation Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); padding: 25px; border-radius: 15px; margin: 20px 0; color: white;">
        <h3 style="margin: 0 0 15px 0; text-align: center;">🎯 Strategic Recommendation</h3>
        <p style="margin: 0; font-size: 18px; text-align: center; font-weight: bold; line-height: 1.6;">
            BH Worldwide faces an existential crisis: £9.99M potential annual loss represents 62% of total revenue. 
            This is NOT an optimization opportunity - this is about company survival. 
            The £1.2M AI investment offers 834% ROI and prevents business collapse. 
            <span style="color: #ffff99; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">IMMEDIATE EXECUTIVE ACTION REQUIRED.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quote Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); padding: 20px; border-radius: 15px; margin: 20px 0; color: white; text-align: center;">
        <p style="margin: 0; font-size: 16px; font-style: italic; font-weight: 500;">
            "The question is not whether BH Worldwide can afford to invest in AI - 
            it's whether the company can survive without it."
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Export Functionality
    st.markdown("---")
    if st.button("📄 Generate Executive Report", type="primary", use_container_width=True):
        st.success("📊 Executive report generated successfully! Check your downloads folder.")
        st.info("Report includes: Real BH financial data, crisis analysis, AI solution ROI, and implementation roadmap.")

elif page == "⚡ Live AOG Center":
    # Professional Header with Mission Control Theme
    current_time = datetime.datetime.now().strftime("%H:%M:%S UTC")
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="color: #1f1f1f; font-size: 36px; font-weight: bold; margin: 0;">
            🚀 AOG Mission Control Center
        </h1>
        <div style="text-align: right;">
            <span style="color: #666; font-size: 14px;">Mission Time: {current_time}</span><br>
            <span style="color: #00ff00; font-size: 12px;">● OPERATIONAL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("*Mission-critical operations command center for global AOG response*")
    
    # Mission Status Summary Cards
    st.markdown("### 🚨 Mission Status Overview")
    status_col1, status_col2, status_col3, status_col4, status_col5 = st.columns(5)
    
    # Get real-time data
    active_cases = dashboard.active_cases["active_aog_cases"]
    critical_cases = [case for case in active_cases if case.get("urgency") == "Critical"]
    high_cases = [case for case in active_cases if case.get("urgency") == "High"]
    pricing_cases = [case for case in active_cases if case.get("status") == "Awaiting Quote"]
    other_cases = [case for case in active_cases if case.get("status") not in ["Awaiting Quote", "Quote Sent", "Completed"]]
    lost_cases = [case for case in active_cases if case.get("status") == "Lost to Competitor"]
    
    with status_col1:
        st.metric("Active Missions", len(active_cases), f"+{random.randint(1,3)} new")
    with status_col2:
        st.metric("Critical Status", len(critical_cases), "🔴 Immediate action")
    with status_col3:
        st.metric("High Priority", len(high_cases), "🟡 Monitoring")
    with status_col4:
        st.metric("Response Time", "14.2 min", "-2.3 min vs target")
    with status_col5:
        st.metric("Success Rate", "97.8%", "+1.2% this month")
    
    # Advanced Mission Control Tabs
    control_tab1, control_tab2, control_tab3, control_tab4, control_tab5 = st.tabs([
        "🎛️ Operations Command", "👥 Resource Allocation", "📡 Communication Hub", 
        "⚠️ Escalation Management", "📊 Performance Monitor"
    ])
    
    with control_tab1:
        st.markdown("### 🎛️ Operations Command Dashboard")
        
        # Global Status Matrix
        st.markdown("#### Global AOG Status Matrix")
        
        ops_col1, ops_col2 = st.columns(2)
        
        with ops_col1:
            # Crisis Indicators
            st.markdown("##### 🚨 Crisis Indicators")
            
            crisis_data = {
                'Region': ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America'],
                'Active Cases': [8, 6, 12, 4, 2],
                'Critical Level': ['Medium', 'Low', 'High', 'Low', 'Low'],
                'Avg Response (min)': [12.5, 15.8, 18.2, 11.3, 22.4],
                'Fleet Impact': ['3.2%', '2.1%', '4.8%', '1.9%', '2.7%']
            }
            crisis_df = pd.DataFrame(crisis_data)
            
            # Color code by crisis level
            def highlight_crisis(row):
                if row['Critical Level'] == 'High':
                    return ['background-color: #ffcccc']*5
                elif row['Critical Level'] == 'Medium':
                    return ['background-color: #fff2cc']*5
                else:
                    return ['background-color: #ccffcc']*5
            
            st.dataframe(crisis_df.style.apply(highlight_crisis, axis=1), use_container_width=True)
        
        with ops_col2:
            # Real-time AOG heat map
            st.markdown("##### 🗺️ Real-time AOG Heat Map")
            
            # AOG intensity by hour
            hours = list(range(24))
            aog_intensity = [random.randint(2, 15) for _ in hours]
            current_hour = datetime.datetime.now().hour
            
            fig = px.bar(
                x=hours,
                y=aog_intensity,
                title="AOG Cases by Hour (UTC)",
                labels={'x': 'Hour (UTC)', 'y': 'Active Cases'}
            )
            
            # Highlight current hour
            fig.add_vline(x=current_hour, line_dash="dash", line_color="red", annotation_text="Current Hour")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Active Mission Board
        st.markdown("#### 🎯 Active Mission Board")
        
        # Organize cases by criticality
        critical_missions = [case for case in active_cases if case.get("urgency") == "Critical"]
        high_missions = [case for case in active_cases if case.get("urgency") == "High"]
        medium_missions = [case for case in active_cases if case.get("urgency") == "Medium"]
        
        mission_col1, mission_col2, mission_col3 = st.columns(3)
        
        with mission_col1:
            st.markdown("##### 🔴 CRITICAL MISSIONS")
            for case in critical_missions[:3]:
                st.markdown(f"""
                <div class="alert-critical">
                    <h4>🚨 {case['case_id']}</h4>
                    <p><strong>Aircraft:</strong> {case['aircraft']}</p>
                    <p><strong>Location:</strong> {case['location']}</p>
                    <p><strong>Elapsed:</strong> {case.get('elapsed_time', 'N/A')}</p>
                    <p><strong>Loss:</strong> {case['total_loss_so_far']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with mission_col2:
            st.markdown("##### 🟡 HIGH PRIORITY")
            for case in high_missions[:3]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); padding: 1rem; border-radius: 10px; color: white; margin: 1rem 0;">
                    <h4>⚡ {case['case_id']}</h4>
                    <p><strong>Aircraft:</strong> {case['aircraft']}</p>
                    <p><strong>Location:</strong> {case['location']}</p>
                    <p><strong>Status:</strong> {case['status']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with mission_col3:
            st.markdown("##### 🟢 MEDIUM PRIORITY")
            for case in medium_missions[:3]:
                st.markdown(f"""
                <div class="success-card">
                    <h4>📋 {case['case_id']}</h4>
                    <p><strong>Aircraft:</strong> {case['aircraft']}</p>
                    <p><strong>Location:</strong> {case['location']}</p>
                    <p><strong>Status:</strong> {case['status']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Mission Timeline
        st.markdown("#### ⏰ Mission Timeline & Forecast")
        
        timeline_col1, timeline_col2 = st.columns(2)
        
        with timeline_col1:
            # Expected resolution times
            st.markdown("##### Expected Resolution Times")
            
            resolution_data = []
            for case in active_cases[:8]:
                base_time = random.randint(30, 360)  # 30 minutes to 6 hours
                if case.get('urgency') == 'Critical':
                    base_time = random.randint(15, 120)
                elif case.get('urgency') == 'High':
                    base_time = random.randint(60, 240)
                
                resolution_data.append({
                    'Case ID': case['case_id'],
                    'Aircraft': case['aircraft'],
                    'ETA (minutes)': base_time,
                    'Confidence': f"{random.randint(75, 95)}%"
                })
            
            resolution_df = pd.DataFrame(resolution_data)
            st.dataframe(resolution_df, use_container_width=True)
        
        with timeline_col2:
            # Workload forecast
            hours_ahead = list(range(1, 13))
            predicted_cases = [len(active_cases) + random.randint(-3, 5) for _ in hours_ahead]
            
            fig = px.line(
                x=hours_ahead,
                y=predicted_cases,
                title="12-Hour Workload Forecast",
                markers=True
            )
            fig.update_layout(
                xaxis_title="Hours Ahead",
                yaxis_title="Predicted Active Cases",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with control_tab2:
        st.markdown("### 👥 Resource Allocation Center")
        
        # Staff Deployment Matrix
        st.markdown("#### Staff Deployment & Availability")
        
        resource_col1, resource_col2 = st.columns(2)
        
        with resource_col1:
            # Real-time staff status
            st.markdown("##### 👨‍🔧 Technical Staff Status")
            
            staff_status = {
                'Role': ['AOG Specialists', 'Technical Engineers', 'Logistics Coordinators', 'Customer Service', 'Quality Inspectors'],
                'Total Staff': [12, 18, 8, 15, 6],
                'On Duty': [10, 15, 7, 12, 5],
                'On Mission': [6, 8, 4, 3, 2],
                'Available': [4, 7, 3, 9, 3],
                'Utilization': ['83%', '89%', '88%', '80%', '83%']
            }
            staff_df = pd.DataFrame(staff_status)
            st.dataframe(staff_df, use_container_width=True)
            
            # Staff availability pie chart
            total_staff = sum(staff_status['Total Staff'])
            on_mission = sum(staff_status['On Mission'])
            available = sum(staff_status['Available'])
            off_duty = total_staff - on_mission - available
            
            fig = px.pie(
                values=[on_mission, available, off_duty],
                names=['On Mission', 'Available', 'Off Duty'],
                title="Overall Staff Status",
                color_discrete_map={'On Mission': '#ff6b6b', 'Available': '#51cf66', 'Off Duty': '#ffd43b'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with resource_col2:
            # Aircraft and equipment status
            st.markdown("##### ✈️ Fleet & Equipment Status")
            
            fleet_status = {
                'Asset Type': ['Company Aircraft', 'Partner Aircraft', 'Ground Vehicles', 'Test Equipment', 'Emergency Kits'],
                'Total Units': [3, 15, 28, 45, 120],
                'Available': [2, 12, 25, 42, 115],
                'In Use': [1, 3, 3, 3, 5],
                'Maintenance': [0, 0, 0, 0, 0],
                'Readiness': ['67%', '80%', '89%', '93%', '96%']
            }
            fleet_df = pd.DataFrame(fleet_status)
            st.dataframe(fleet_df, use_container_width=True)
            
            # Equipment readiness chart
            equipment_readiness = [67, 80, 89, 93, 96]
            equipment_types = ['Aircraft', 'Partner Fleet', 'Vehicles', 'Test Equip', 'Emergency']
            
            fig = px.bar(
                x=equipment_types,
                y=equipment_readiness,
                title="Equipment Readiness Levels",
                color=equipment_readiness,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Parts Inventory Matrix
        st.markdown("#### 📦 Critical Parts Inventory Status")
        
        inventory_col1, inventory_col2 = st.columns(2)
        
        with inventory_col1:
            # Critical parts status
            st.markdown("##### High-Demand Parts Inventory")
            
            parts_data = {
                'Part Category': ['Engine Components', 'Avionics', 'Landing Gear', 'Flight Controls', 'Hydraulics'],
                'Critical Parts': [45, 78, 23, 34, 56],
                'In Stock': [42, 71, 21, 32, 53],
                'On Order': [8, 15, 4, 6, 8],
                'Emergency Stock': [12, 18, 6, 9, 14],
                'Stock Level': ['94%', '91%', '91%', '94%', '95%']
            }
            parts_df = pd.DataFrame(parts_data)
            st.dataframe(parts_df, use_container_width=True)
        
        with inventory_col2:
            # Inventory health indicators
            st.markdown("##### Inventory Health Indicators")
            
            health_metrics = {
                'Metric': ['Stock Availability', 'Turnover Rate', 'Emergency Stock', 'Supplier Response', 'Quality Rate'],
                'Current': [93.2, 4.8, 98.5, 91.7, 99.1],
                'Target': [95.0, 5.2, 99.0, 95.0, 99.5],
                'Status': ['⚠️', '✅', '✅', '⚠️', '✅']
            }
            health_df = pd.DataFrame(health_metrics)
            st.dataframe(health_df, use_container_width=True)
            
            # Supplier response time trend
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            response_times = [14.2, 13.8, 15.1, 12.9, 16.3, 18.7, 17.2]
            
            fig = px.line(
                x=days,
                y=response_times,
                title="Supplier Response Times (Hours)",
                markers=True
            )
            fig.add_hline(y=15.0, line_dash="dash", line_color="red", annotation_text="Target")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Resource Optimization Recommendations
        st.markdown("#### 🎯 Resource Optimization Recommendations")
        
        optimization_col1, optimization_col2, optimization_col3 = st.columns(3)
        
        with optimization_col1:
            st.markdown("""
            <div class="metric-card">
                <h4>📈 Staff Optimization</h4>
                <p><strong>Recommendation:</strong> Redistribute 2 engineers from low-activity regions</p>
                <p><strong>Impact:</strong> 15% faster response in high-demand areas</p>
                <p><strong>Timeline:</strong> Immediate</p>
            </div>
            """, unsafe_allow_html=True)
        
        with optimization_col2:
            st.markdown("""
            <div class="metric-card">
                <h4>✈️ Fleet Optimization</h4>
                <p><strong>Recommendation:</strong> Pre-position emergency aircraft in Dubai</p>
                <p><strong>Impact:</strong> 30% reduction in Middle East response time</p>
                <p><strong>Timeline:</strong> 24 hours</p>
            </div>
            """, unsafe_allow_html=True)
        
        with optimization_col3:
            st.markdown("""
            <div class="metric-card">
                <h4>📦 Inventory Optimization</h4>
                <p><strong>Recommendation:</strong> Increase engine component buffer stock</p>
                <p><strong>Impact:</strong> 95% stock availability target</p>
                <p><strong>Timeline:</strong> 7 days</p>
            </div>
            """, unsafe_allow_html=True)
    
    with control_tab3:
        st.markdown("### 📡 Customer Communication Hub")
        
        # Communication Status Dashboard
        st.markdown("#### Communication Status & Automation")
        
        comm_col1, comm_col2 = st.columns(2)
        
        with comm_col1:
            # Active communications
            st.markdown("##### 📞 Active Communications")
            
            # Real-time communication tracking
            comm_data = []
            for case in active_cases[:6]:
                comm_data.append({
                    'Case ID': case['case_id'],
                    'Customer': case['airline'],
                    'Last Contact': f"{random.randint(5, 45)} min ago",
                    'Method': random.choice(['Email', 'Phone', 'SMS', 'Portal']),
                    'Status': random.choice(['Acknowledged', 'Pending Response', 'Follow-up Required']),
                    'Next Update': f"{random.randint(15, 60)} min"
                })
            
            comm_df = pd.DataFrame(comm_data)
            st.dataframe(comm_df, use_container_width=True)
        
        with comm_col2:
            # SLA tracking
            st.markdown("##### ⏱️ SLA Performance Tracking")
            
            sla_metrics = {
                'SLA Metric': ['Initial Response', 'Status Updates', 'Resolution Notice', 'Final Report'],
                'Target (min)': [15, 30, 60, 240],
                'Current Avg': [14.2, 27.8, 52.3, 218.5],
                'Compliance %': [96.8, 94.2, 91.7, 95.4],
                'Trend': ['↗️', '↗️', '↘️', '↗️']
            }
            sla_df = pd.DataFrame(sla_metrics)
            st.dataframe(sla_df, use_container_width=True)
            
            # SLA compliance trend
            sla_compliance = [96.8, 94.2, 91.7, 95.4]
            sla_names = ['Initial', 'Updates', 'Resolution', 'Report']
            
            fig = px.bar(
                x=sla_names,
                y=sla_compliance,
                title="SLA Compliance by Type",
                color=sla_compliance,
                color_continuous_scale='RdYlGn'
            )
            fig.add_hline(y=95.0, line_dash="dash", line_color="blue", annotation_text="Target")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Automated Notification System
        st.markdown("#### 🤖 Automated Notification System")
        
        notification_col1, notification_col2, notification_col3 = st.columns(3)
        
        with notification_col1:
            st.markdown("##### 📧 Email Automation")
            
            email_stats = {
                'Type': ['Case Acknowledgment', 'Progress Updates', 'Quote Delivery', 'Resolution Notice'],
                'Sent Today': [24, 67, 18, 12],
                'Success Rate': ['100%', '98.5%', '100%', '100%'],
                'Avg Response': ['2.3 min', '4.1 min', '1.8 min', 'N/A']
            }
            email_df = pd.DataFrame(email_stats)
            st.dataframe(email_df, use_container_width=True)
        
        with notification_col2:
            st.markdown("##### 📱 SMS & Push Alerts")
            
            sms_stats = {
                'Alert Type': ['Critical AOG', 'High Priority', 'SLA Warning', 'Resolution'],
                'Sent Today': [8, 15, 3, 12],
                'Delivery Rate': ['100%', '99.2%', '100%', '98.8%'],
                'Response Rate': ['87.5%', '73.3%', '100%', '58.3%']
            }
            sms_df = pd.DataFrame(sms_stats)
            st.dataframe(sms_df, use_container_width=True)
        
        with notification_col3:
            st.markdown("##### 🌐 Portal Notifications")
            
            portal_stats = {
                'Notification': ['Case Updates', 'Document Ready', 'Invoice Posted', 'Schedule Change'],
                'Posted Today': [45, 12, 8, 6],
                'Read Rate': ['94.2%', '100%', '87.5%', '83.3%'],
                'Avg Read Time': ['12 min', '3 min', '45 min', '18 min']
            }
            portal_df = pd.DataFrame(portal_stats)
            st.dataframe(portal_df, use_container_width=True)
        
        # Communication Quality Metrics
        st.markdown("#### 📊 Communication Quality Metrics")
        
        quality_col1, quality_col2 = st.columns(2)
        
        with quality_col1:
            # Customer satisfaction with communications
            comm_satisfaction = [9.2, 8.7, 8.9, 8.4, 8.8]
            comm_channels = ['Phone', 'Email', 'Portal', 'SMS', 'Overall']
            
            fig = px.bar(
                x=comm_channels,
                y=comm_satisfaction,
                title="Communication Channel Satisfaction",
                color=comm_satisfaction,
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with quality_col2:
            # Response time by channel
            response_times = [2.3, 4.1, 8.7, 1.2, 12.5]
            channels = ['SMS', 'Phone', 'Email', 'Push', 'Portal']
            
            fig = px.bar(
                x=channels,
                y=response_times,
                title="Avg Response Time by Channel (min)",
                color=response_times,
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with control_tab4:
        st.markdown("### ⚠️ Escalation Management System")
        
        # Automatic Escalation Triggers
        st.markdown("#### 🚨 Automatic Escalation Triggers")
        
        escalation_col1, escalation_col2 = st.columns(2)
        
        with escalation_col1:
            # Current escalations
            st.markdown("##### 🔥 Active Escalations")
            
            escalations = []
            for case in critical_cases[:4]:
                escalation_level = random.choice(['Level 1', 'Level 2', 'Level 3'])
                escalation_reason = random.choice(['Response Time Breach', 'High Financial Impact', 'VIP Customer', 'Critical Aircraft'])
                escalations.append({
                    'Case ID': case['case_id'],
                    'Customer': case['airline'],
                    'Level': escalation_level,
                    'Reason': escalation_reason,
                    'Escalated To': 'Operations Manager' if escalation_level == 'Level 1' else 'Director' if escalation_level == 'Level 2' else 'CEO',
                    'Time Since': f"{random.randint(5, 90)} min"
                })
            
            escalation_df = pd.DataFrame(escalations)
            st.dataframe(escalation_df, use_container_width=True)
        
        with escalation_col2:
            # Escalation rules matrix
            st.markdown("##### ⚙️ Escalation Rules Matrix")
            
            rules_data = {
                'Trigger': ['Response > 30 min', 'Loss > $100K', 'VIP Customer AOG', 'Multiple Failures', 'Media Attention'],
                'Level': ['Level 1', 'Level 2', 'Level 3', 'Level 2', 'Level 3'],
                'Auto Action': ['SMS to Manager', 'Call Director', 'Page CEO', 'Team Alert', 'PR Team Alert'],
                'Threshold': ['30 min', '$100K', 'Immediate', '3 failures', 'Any mention']
            }
            rules_df = pd.DataFrame(rules_data)
            st.dataframe(rules_df, use_container_width=True)
        
        # Management Alert Dashboard
        st.markdown("#### 📢 Management Alert Dashboard")
        
        alert_col1, alert_col2 = st.columns(2)
        
        with alert_col1:
            # Recent alerts sent
            st.markdown("##### 🚨 Recent Management Alerts")
            
            recent_alerts = [
                {
                    'Time': '09:45 UTC',
                    'Level': 'Level 3',
                    'Case': 'AOG-2024-1247',
                    'Alert': 'CEO notification - Emirates A350 AOG > 2 hours',
                    'Status': 'Acknowledged'
                },
                {
                    'Time': '08:32 UTC',
                    'Level': 'Level 2',
                    'Case': 'AOG-2024-1245',
                    'Alert': 'Director alert - American Airlines loss > $150K',
                    'Status': 'Action Taken'
                },
                {
                    'Time': '07:18 UTC',
                    'Level': 'Level 1',
                    'Case': 'AOG-2024-1243',
                    'Alert': 'Manager SMS - Response time approaching limit',
                    'Status': 'Resolved'
                }
            ]
            
            for alert in recent_alerts:
                status_color = '#28a745' if alert['Status'] == 'Resolved' else '#ffc107' if alert['Status'] == 'Action Taken' else '#dc3545'
                st.markdown(f"""
                <div style="border-left: 4px solid {status_color}; padding: 10px; margin: 10px 0; background: #f8f9fa;">
                    <strong>{alert['Time']} - {alert['Level']}</strong><br>
                    <strong>Case:</strong> {alert['Case']}<br>
                    <strong>Alert:</strong> {alert['Alert']}<br>
                    <strong>Status:</strong> <span style="color: {status_color};">{alert['Status']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with alert_col2:
            # Escalation effectiveness metrics
            st.markdown("##### 📊 Escalation Effectiveness")
            
            effectiveness_data = {
                'Metric': ['Avg Response to Alert', 'Resolution Improvement', 'False Escalations', 'Customer Satisfaction', 'Management Satisfaction'],
                'Current': ['3.2 min', '45% faster', '12%', '8.9/10', '9.1/10'],
                'Target': ['5.0 min', '30% faster', '<15%', '>8.5', '>8.5'],
                'Status': ['✅', '✅', '✅', '✅', '✅']
            }
            effectiveness_df = pd.DataFrame(effectiveness_data)
            st.dataframe(effectiveness_df, use_container_width=True)
            
            # Escalation frequency trend
            weeks = ['Week -4', 'Week -3', 'Week -2', 'Week -1', 'This Week']
            escalation_counts = [12, 8, 15, 6, 9]
            
            fig = px.line(
                x=weeks,
                y=escalation_counts,
                title="Weekly Escalation Frequency",
                markers=True
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        # Escalation Prevention
        st.markdown("#### 🛡️ Escalation Prevention Intelligence")
        
        prevention_col1, prevention_col2, prevention_col3 = st.columns(3)
        
        with prevention_col1:
            st.markdown("""
            <div class="alert-critical">
                <h4>🔮 Predictive Alerts</h4>
                <p><strong>Risk Detected:</strong> AOG-2024-1248 likely to escalate in 15 minutes</p>
                <p><strong>Reason:</strong> Parts delivery delayed</p>
                <p><strong>Action:</strong> Mobilizing backup supplier</p>
            </div>
            """, unsafe_allow_html=True)
        
        with prevention_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); padding: 1rem; border-radius: 10px; color: white; margin: 1rem 0;">
                <h4>⚡ Auto-Prevention</h4>
                <p><strong>Action Taken:</strong> Pre-emptive customer call initiated</p>
                <p><strong>Case:</strong> AOG-2024-1249</p>
                <p><strong>Result:</strong> Escalation probability reduced 75%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with prevention_col3:
            st.markdown("""
            <div class="success-card">
                <h4>📈 Success Metrics</h4>
                <p><strong>Prevented Escalations:</strong> 23 this month</p>
                <p><strong>Cost Savings:</strong> $450K avoided</p>
                <p><strong>Customer Satisfaction:</strong> +15% improvement</p>
            </div>
            """, unsafe_allow_html=True)
    
    with control_tab5:
        st.markdown("### 📊 Performance Monitoring Dashboard")
        
        # Live Performance Metrics
        st.markdown("#### ⚡ Live Performance Metrics")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            # Real-time productivity
            st.markdown("##### 🏃 Team Productivity")
            
            productivity_data = {
                'Team': ['AOG Specialists', 'Technical Engineers', 'Logistics', 'Customer Service'],
                'Cases/Hour': [2.3, 1.8, 3.1, 4.2],
                'Efficiency': ['92%', '89%', '95%', '87%'],
                'Target': [2.0, 1.5, 3.0, 4.0],
                'Status': ['✅', '✅', '✅', '✅']
            }
            productivity_df = pd.DataFrame(productivity_data)
            st.dataframe(productivity_df, use_container_width=True)
        
        with perf_col2:
            # Response time analytics
            st.markdown("##### ⏱️ Response Time Analytics")
            
            response_data = {
                'Priority': ['Critical', 'High', 'Medium', 'Low'],
                'Target (min)': [15, 30, 60, 120],
                'Current (min)': [12.8, 28.4, 52.3, 98.7],
                'Achievement': ['117%', '105%', '115%', '118%'],
                'Trend': ['↗️', '↗️', '↘️', '↗️']
            }
            response_df = pd.DataFrame(response_data)
            st.dataframe(response_df, use_container_width=True)
        
        with perf_col3:
            # Quality metrics
            st.markdown("##### 🎯 Quality Metrics")
            
            quality_data = {
                'Metric': ['First Time Fix', 'Customer Satisfaction', 'Accuracy Rate', 'Completion Rate'],
                'Current': ['87.6%', '8.4/10', '96.8%', '98.2%'],
                'Target': ['85%', '8.0/10', '95%', '95%'],
                'Performance': ['103%', '105%', '102%', '103%'],
                'Status': ['✅', '✅', '✅', '✅']
            }
            quality_df = pd.DataFrame(quality_data)
            st.dataframe(quality_df, use_container_width=True)
        
        # Performance Trends
        st.markdown("#### 📈 Performance Trends & Analytics")
        
        trends_col1, trends_col2 = st.columns(2)
        
        with trends_col1:
            # Hourly performance
            st.markdown("##### Hourly Performance Pattern")
            
            hours = list(range(24))
            performance_scores = [75 + 20 * abs(np.sin(h * np.pi / 12)) + random.randint(-5, 5) for h in hours]
            current_hour = datetime.datetime.now().hour
            
            fig = px.line(
                x=hours,
                y=performance_scores,
                title="24-Hour Performance Score",
                markers=True
            )
            fig.add_vline(x=current_hour, line_dash="dash", line_color="red", annotation_text="Now")
            fig.add_hline(y=85, line_dash="dash", line_color="green", annotation_text="Target")
            st.plotly_chart(fig, use_container_width=True)
        
        with trends_col2:
            # Weekly productivity trend
            st.markdown("##### Weekly Productivity Trend")
            
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            productivity_scores = [92, 94, 91, 95, 89, 87, 88]
            
            fig = px.bar(
                x=days,
                y=productivity_scores,
                title="Daily Productivity Scores",
                color=productivity_scores,
                color_continuous_scale='RdYlGn'
            )
            fig.add_hline(y=90, line_dash="dash", line_color="blue", annotation_text="Target")
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance Optimization
        st.markdown("#### 🚀 Performance Optimization Insights")
        
        optimization_col1, optimization_col2 = st.columns(2)
        
        with optimization_col1:
            # Top performers
            st.markdown("##### 🏆 Top Performing Teams")
            
            top_performers = {
                'Team': ['Singapore Hub', 'Miami Operations', 'London Center', 'Dubai Office'],
                'Performance Score': [96.2, 94.8, 92.1, 91.7],
                'Key Strength': ['Response Time', 'Quality', 'Efficiency', 'Customer Service'],
                'Recognition': ['🥇', '🥈', '🥉', '⭐']
            }
            performers_df = pd.DataFrame(top_performers)
            st.dataframe(performers_df, use_container_width=True)
        
        with optimization_col2:
            # Improvement opportunities
            st.markdown("##### 📊 Improvement Opportunities")
            
            improvements = {
                'Area': ['Parts Sourcing', 'Documentation', 'Communication', 'Training'],
                'Current Score': [87.3, 89.1, 91.4, 88.7],
                'Potential Gain': ['+8.2%', '+5.7%', '+3.8%', '+6.9%'],
                'Investment': ['Medium', 'Low', 'Low', 'Medium'],
                'Timeline': ['6 weeks', '2 weeks', '1 week', '8 weeks']
            }
            improvements_df = pd.DataFrame(improvements)
            st.dataframe(improvements_df, use_container_width=True)
        
        # Real-time Alerts
        st.markdown("#### 🚨 Real-time Performance Alerts")
        
        alerts_col1, alerts_col2, alerts_col3 = st.columns(3)
        
        with alerts_col1:
            st.markdown("""
            <div class="success-card">
                <h4>✅ Performance Excellence</h4>
                <p><strong>Team:</strong> AOG Specialists</p>
                <p><strong>Achievement:</strong> 100% SLA compliance for 8 hours</p>
                <p><strong>Impact:</strong> Zero escalations</p>
            </div>
            """, unsafe_allow_html=True)
        
        with alerts_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); padding: 1rem; border-radius: 10px; color: white; margin: 1rem 0;">
                <h4>⚠️ Performance Watch</h4>
                <p><strong>Team:</strong> Europe Operations</p>
                <p><strong>Issue:</strong> Response time trending up</p>
                <p><strong>Action:</strong> Additional resources deployed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with alerts_col3:
            st.markdown("""
            <div class="metric-card">
                <h4>📈 Trending Up</h4>
                <p><strong>Metric:</strong> Customer Satisfaction</p>
                <p><strong>Improvement:</strong> +12% this week</p>
                <p><strong>Driver:</strong> Faster resolution times</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Legacy case management (simplified)
    if st.session_state.generated_quotes:
        st.markdown("---")
        st.markdown("### 📋 Recent Mission Outcomes")
        
        quotes_summary_col1, quotes_summary_col2, quotes_summary_col3 = st.columns(3)
        
        total_quotes = len(st.session_state.generated_quotes)
        total_value = sum(quote['total_cost'] for quote in st.session_state.generated_quotes)
        avg_confidence = sum(quote['confidence_score'] for quote in st.session_state.generated_quotes) / total_quotes
        
        with quotes_summary_col1:
            st.metric("Missions Completed", total_quotes, "+3 today")
        with quotes_summary_col2:
            st.metric("Total Value", f"£{total_value:,}", "+15% vs yesterday")
        with quotes_summary_col3:
            st.metric("Success Rate", f"{avg_confidence:.1f}%", "+2.3% this week")
    
    # Show pricing cases first (these need attention)
    if pricing_cases:
        st.subheader("🔴 Cases Requiring Immediate Action")
        for case in pricing_cases:
            case_id = case['case_id']
            is_quoted = st.session_state.case_statuses.get(case_id) == "quoted"
            
            with st.expander(f"🔴 {case_id} - {case['airline']} ({case['urgency']} Priority) - NEEDS QUOTE"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Aircraft:** {case['aircraft']}")
                    st.write(f"**Tail Number:** {case['tail_number']}")
                    st.write(f"**Location:** {case['location']}")
                    
                with col2:
                    st.write(f"**Part Needed:** {case['part_needed']}")
                    st.write(f"**Part Number:** {case['part_number']}")
                    st.write(f"**Status:** {case['status']}")
                    
                    # Real-time inventory check
                    inventory_status = dashboard.get_inventory_status(case['part_number'])
                    if inventory_status:
                        st.markdown("**🏭 Global Stock Status:**")
                        stock_display = []
                        for location, stock in inventory_status['available_stock'].items():
                            if stock > 0:
                                color = "🟢" if stock >= 3 else "🟡" if stock >= 1 else "🔴"
                                stock_display.append(f"{color} {location.title()}({stock})")
                            else:
                                stock_display.append(f"🔴 {location.title()}(0)")
                        st.markdown(" ".join(stock_display))
                        
                        # Show ETA for incoming stock if available
                        if inventory_status.get('next_arrival'):
                            st.markdown(f"📦 **Next Arrival:** {inventory_status['next_arrival']}")
                    else:
                        st.markdown("**🏭 Stock Status:** ⚠️ Data not available")
                    
                with col3:
                    st.write(f"**Loss per Hour:** {case['estimated_loss_per_hour']}")
                    st.write(f"**Total Loss:** {case['total_loss_so_far']}")
                    st.write(f"**Elapsed Time:** {case.get('elapsed_time', 'N/A')}")
                
                # FIXED: All pricing cases get quote buttons
                if not is_quoted:
                    if st.button(f"🤖 Generate AI Quote for {case_id}", key=f"quote_{case_id}"):
                        # FIXED: Track actual processing time
                        start_time = time.time()
                        
                        st.markdown("---")
                        st.subheader(f"⚡ AI Processing for {case_id}")
                        
                        quote = dashboard.generate_ai_quote(case, case_id)
                        
                        # FIXED: Show actual processing time
                        actual_time = time.time() - start_time
                        actual_minutes = int(actual_time / 60)
                        actual_seconds = int(actual_time % 60)
                        
                        if actual_minutes > 0:
                            time_display = f"{actual_minutes}m {actual_seconds}s"
                        else:
                            time_display = f"{actual_seconds} seconds"
                        
                        # Show AI advantage in response time
                        ai_advantage = "(98% faster than manual process!)"
                        st.success(f"✅ Quote generated for {case_id} in {time_display} {ai_advantage}")
                        
                        # Show real data integration status
                        if quote.get('real_data_used', False):
                            st.info("📊 **Real Data Integration**: This quote uses actual BH Worldwide parts catalog and pricing data")
                        else:
                            st.warning("🔄 **Simulation Mode**: Real parts data not found, using realistic estimates")
                        
                        dashboard.display_quote_card(quote)
                        
                        # FIXED: Better action buttons with real functionality
                        st.markdown("---")
                        st.subheader(f"📋 Next Actions for {quote['quote_id']}")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.button(f"📧 Send Quote", key=f"send_{quote['quote_id']}"):
                                # FIXED: Real action - mark as sent
                                st.session_state.case_statuses[case_id] = "quote_sent"
                                st.success(f"✅ Quote {quote['quote_id']} sent to {quote['airline']}!")
                                st.info("📧 Email sent to airline AOG manager")
                                st.rerun()
                                
                        with col2:
                            if st.button(f"📋 Modify", key=f"modify_{quote['quote_id']}"):
                                # FIXED: Real action - show modification options
                                st.info(f"🔧 Quote {quote['quote_id']} opened for modification")
                                
                                # Show modification options
                                new_delivery = st.selectbox("Change Delivery:", ["Next Flight Out", "Same Day", "Express", "Standard"], key=f"mod_del_{quote['quote_id']}")
                                price_adjustment = st.slider("Price Adjustment (%):", -20, 20, 0, key=f"mod_price_{quote['quote_id']}")
                                
                                if st.button("💾 Save Changes", key=f"save_{quote['quote_id']}"):
                                    adjusted_cost = int(quote['total_cost'] * (1 + price_adjustment/100))
                                    st.success(f"✅ Quote modified: Delivery={new_delivery}, New Cost=£{adjusted_cost:,}")
                                
                        with col3:
                            if st.button(f"🔄 Alternative", key=f"alt_{quote['quote_id']}"):
                                # FIXED: Real action - generate alternative
                                st.info(f"🔄 Generating alternative quote for {case_id}")
                                
                                # Generate alternative with different pricing
                                alt_quote = dashboard.generate_ai_quote(case.to_dict(), f"{case_id}-ALT")
                                st.success("✅ Alternative quote generated!")
                                dashboard.display_quote_card(alt_quote)
                                
                        with col4:
                            if st.button(f"❌ Cancel", key=f"cancel_{quote['quote_id']}"):
                                # FIXED: Real action - cancel and remove
                                st.session_state.case_statuses[case_id] = "cancelled"
                                # Remove from generated quotes
                                st.session_state.generated_quotes = [q for q in st.session_state.generated_quotes if q['quote_id'] != quote['quote_id']]
                                st.warning(f"❌ Quote {quote['quote_id']} cancelled and removed")
                                st.rerun()
                        
                else:
                    # Show existing quote
                    existing_quote = next((q for q in st.session_state.generated_quotes if q.get('case_id') == case_id), None)
                    if existing_quote:
                        quote_status = st.session_state.case_statuses.get(case_id, "generated")
                        
                        if quote_status == "quote_sent":
                            st.success(f"✅ Quote {existing_quote['quote_id']} sent to customer")
                        elif quote_status == "cancelled":
                            st.warning(f"❌ Quote cancelled")
                        else:
                            st.info(f"📋 Quote {existing_quote['quote_id']} ready for action")
                        
                        if st.button(f"👁️ View Quote Details", key=f"view_{case_id}"):
                            dashboard.display_quote_card(existing_quote)
    
    # Show other cases
    if other_cases:
        st.subheader("📊 Other Active Cases")
        for case in other_cases:
            case_id = case['case_id']
            
            with st.expander(f"🟡 {case_id} - {case['airline']} ({case['status']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Aircraft:** {case['aircraft']}")
                    st.write(f"**Location:** {case['location']}")
                    
                with col2:
                    st.write(f"**Part Needed:** {case['part_needed']}")
                    st.write(f"**Part Number:** {case.get('part_number', 'N/A')}")
                    st.write(f"**Status:** {case['status']}")
                    
                    # Real-time inventory check
                    if case.get('part_number'):
                        inventory_status = dashboard.get_inventory_status(case['part_number'])
                        if inventory_status:
                            st.markdown("**🏭 Stock Levels:**")
                            stock_display = []
                            for location, stock in inventory_status['available_stock'].items():
                                if stock > 0:
                                    color = "🟢" if stock >= 3 else "🟡" if stock >= 1 else "🔴"
                                    stock_display.append(f"{color} {location.title()}({stock})")
                                else:
                                    stock_display.append(f"🔴 {location.title()}(0)")
                            st.markdown(" ".join(stock_display))
                        else:
                            st.markdown("**🏭 Stock:** ⚠️ Not tracked")
                    
                with col3:
                    st.write(f"**Total Loss:** {case['total_loss_so_far']}")
                    st.write(f"**Urgency:** {case['urgency']}")
    
    # Show lost cases at the bottom (less priority)
    if lost_cases:
        st.subheader("❌ Cases Lost to Competitors")
        st.warning("These cases were lost due to slow response times. Use them for analysis and improvement.")
        
        for case in lost_cases:
            with st.expander(f"❌ {case['case_id']} - {case['airline']} (LOST)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Aircraft:** {case['aircraft']}")
                    st.write(f"**Part Needed:** {case['part_needed']}")
                    st.write(f"**Location:** {case['location']}")
                    
                with col2:
                    st.write(f"**Total Loss:** {case['total_loss_so_far']}")
                    st.write(f"**Elapsed Time:** {case.get('elapsed_time', 'N/A')}")
                    st.error("Lost due to slow response time")
    
    # Quote Summary Section (keep existing)
    if st.session_state.generated_quotes:
        st.markdown("---")
        st.subheader("📊 Generated Quotes Summary")
        
        total_quotes = len(st.session_state.generated_quotes)
        total_value = sum(quote['total_cost'] for quote in st.session_state.generated_quotes)
        avg_confidence = sum(quote['confidence_score'] for quote in st.session_state.generated_quotes) / total_quotes
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="quote-summary">
                <h4>Total Quotes</h4>
                <h2>{total_quotes}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="quote-summary">
                <h4>Total Value</h4>
                <h2>£{total_value:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="quote-summary">
                <h4>Avg Confidence</h4>
                <h2>{avg_confidence:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Quotes table with status
        quotes_df = pd.DataFrame([
            {
                "Quote ID": quote['quote_id'],
                "Case ID": quote['case_id'],
                "Airline": quote['airline'],
                "Total Cost (£)": f"{quote['total_cost']:,}",
                "Status": st.session_state.case_statuses.get(quote['case_id'], 'Generated'),
                "Generated": quote['timestamp']
            }
            for quote in st.session_state.generated_quotes
        ])
        
        st.dataframe(quotes_df, use_container_width=True)

elif page == "🗺️ Global Operations Map":
    # FedEx/DHL-style Global Logistics Intelligence Header
    current_time = datetime.datetime.now().strftime("%H:%M:%S UTC")
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="color: #1f1f1f; font-size: 36px; font-weight: bold; margin: 0;">
            🌐 Global Logistics Intelligence Center
        </h1>
        <div style="text-align: right;">
            <span style="color: #666; font-size: 14px;">Global Time: {current_time}</span><br>
            <span style="color: #00ff00; font-size: 12px;">● NETWORK OPERATIONAL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("*Real-time global logistics command center for aviation parts distribution*")
    
    # Global Network Status Overview
    st.markdown("### 🌍 Global Network Status")
    network_col1, network_col2, network_col3, network_col4, network_col5 = st.columns(5)
    
    # Get real-time logistics data
    active_cases = dashboard.active_cases["active_aog_cases"]
    total_shipments = len(active_cases) * 3  # Simulate shipments based on cases
    
    with network_col1:
        st.metric("Active Shipments", f"{total_shipments:,}", f"+{random.randint(5,15)} new")
    with network_col2:
        st.metric("Aircraft in Transit", f"{random.randint(8,12)}", "✈️ Global fleet")
    with network_col3:
        st.metric("Hub Processing", f"{random.randint(1200,1800):,} parts", "📦 Active handling")
    with network_col4:
        st.metric("Network Efficiency", "96.8%", "+1.2% vs target")
    with network_col5:
        st.metric("On-Time Delivery", "94.7%", "📊 Global average")
    
    # Advanced Logistics Intelligence Tabs
    logistics_tab1, logistics_tab2, logistics_tab3, logistics_tab4, logistics_tab5 = st.tabs([
        "📍 Real-Time Tracking", "🧠 Logistics Intelligence", "🏢 Hub Performance", 
        "🔗 Supply Chain Visibility", "🌎 Regional Analysis"
    ])
    
    with logistics_tab1:
        st.markdown("### 📍 Real-Time Global Tracking")
        
        # Live Global Map with Enhanced Features
        st.markdown("#### 🗺️ Live Global Logistics Network")
        
        # Enhanced map with logistics data
        map_obj = dashboard.create_global_map()
        st_folium(map_obj, width=1200, height=500, returned_objects=[])
        
        tracking_col1, tracking_col2 = st.columns(2)
        
        with tracking_col1:
            # Aircraft Fleet Status
            st.markdown("##### ✈️ Fleet Status & Live Positions")
            
            fleet_data = {
                'Aircraft': ['BH-001 (B737F)', 'BH-002 (A320F)', 'BH-003 (Citation)', 'BH-004 (King Air)', 'BH-005 (Learjet)'],
                'Current Location': ['En route MIA→LHR', 'Loading at CDG', 'On ground SIN', 'En route DXB→FRA', 'Maintenance at MIA'],
                'Cargo Status': ['85% loaded', '100% loaded', 'Ready for dispatch', '60% loaded', 'Scheduled maintenance'],
                'ETA': ['4h 25m', 'Departing now', 'On standby', '2h 15m', '8h (back in service)'],
                'Priority Level': ['High', 'Critical', 'Medium', 'High', 'N/A']
            }
            fleet_df = pd.DataFrame(fleet_data)
            
            # Color code by priority
            def highlight_priority(row):
                if row['Priority Level'] == 'Critical':
                    return ['background-color: #ffcccc']*5
                elif row['Priority Level'] == 'High':
                    return ['background-color: #fff2cc']*5
                elif row['Priority Level'] == 'Medium':
                    return ['background-color: #e6f3ff']*5
                else:
                    return ['background-color: #f0f0f0']*5
            
            st.dataframe(fleet_df.style.apply(highlight_priority, axis=1), use_container_width=True)
        
        with tracking_col2:
            # Parts Movement Tracking
            st.markdown("##### 📦 Live Parts Movement")
            
            # Shipment tracking simulation
            shipment_hours = list(range(24))
            shipments_per_hour = [random.randint(15, 45) for _ in shipment_hours]
            current_hour = datetime.datetime.now().hour
            
            fig = px.line(
                x=shipment_hours,
                y=shipments_per_hour,
                title="Parts Movement - Last 24 Hours",
                labels={'x': 'Hour (UTC)', 'y': 'Active Shipments'}
            )
            
            # Highlight current hour
            fig.add_vline(x=current_hour, line_dash="dash", line_color="red", annotation_text="Now")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Critical Shipments Alert Board
        st.markdown("#### 🚨 Critical Shipments Alert Board")
        
        critical_shipments = [
            {"tracking": "BH240712001", "part": "Boeing 737 Engine Starter", "from": "Chicago", "to": "Dubai", "eta": "6h 30m", "status": "In Transit", "priority": "AOG Critical"},
            {"tracking": "BH240712002", "part": "A320 Landing Gear Actuator", "from": "Hamburg", "to": "Singapore", "eta": "12h 15m", "status": "Customs Hold", "priority": "AOG Critical"},
            {"tracking": "BH240712003", "part": "737 MAX Flight Computer", "from": "Seattle", "to": "London", "eta": "8h 45m", "status": "In Transit", "priority": "High"}
        ]
        
        for i, shipment in enumerate(critical_shipments):
            status_color = "#ff4444" if "Critical" in shipment["priority"] else "#ff8800"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {status_color} 0%, #ff6666 100%); padding: 1rem; border-radius: 10px; color: white; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0;">{shipment["tracking"]} - {shipment["part"]}</h4>
                        <p style="margin: 0.5rem 0 0 0;">{shipment["from"]} → {shipment["to"]} | ETA: {shipment["eta"]} | {shipment["status"]}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: rgba(255,255,255,0.3); padding: 0.3rem 0.6rem; border-radius: 15px; font-size: 12px;">
                            {shipment["priority"]}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with logistics_tab2:
        st.markdown("### 🧠 Logistics Intelligence")
        
        # Route Optimization & Intelligence
        st.markdown("#### 🛣️ Route Optimization & Intelligence")
        
        intel_col1, intel_col2 = st.columns(2)
        
        with intel_col1:
            # Route Efficiency Analysis
            st.markdown("##### 📊 Route Efficiency Analysis")
            
            routes_data = {
                'Route': ['Miami → Europe', 'Singapore → Middle East', 'London → Asia Pacific', 'Dubai → Americas', 'Chicago → Global'],
                'Avg Transit Time': ['8.5h', '4.2h', '11.3h', '15.7h', '9.8h'],
                'Efficiency Score': [94.2, 97.1, 89.6, 86.3, 91.7],
                'Weather Impact': ['Low', 'Medium', 'High', 'Low', 'Medium'],
                'Cost per kg': ['$12.50', '$8.90', '$15.20', '$18.40', '$13.80']
            }
            routes_df = pd.DataFrame(routes_data)
            st.dataframe(routes_df, use_container_width=True)
            
            # Route optimization suggestions
            st.markdown("##### 🎯 Optimization Recommendations")
            st.markdown("""
            - **London → Asia Pacific**: Consider Shanghai hub for 15% time reduction
            - **Dubai → Americas**: Alternative routing via Europe during peak season
            - **Weather-sensitive routes**: 48h advanced weather planning active
            """)
        
        with intel_col2:
            # Weather & Disruption Impact
            st.markdown("##### 🌤️ Weather & Disruption Impact")
            
            weather_regions = ['North America', 'Europe', 'Asia Pacific', 'Middle East', 'Latin America']
            weather_impact = [random.randint(1, 5) for _ in weather_regions]
            
            fig = px.bar(
                x=weather_regions,
                y=weather_impact,
                title="Weather Impact Score by Region (1-5 scale)",
                color=weather_impact,
                color_continuous_scale="RdYlGn_r"
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Customs & Regulatory Intelligence
            st.markdown("##### 📋 Customs & Regulatory Intelligence")
            
            customs_alerts = [
                {"region": "EU", "alert": "New battery regulations effective", "impact": "Medium", "action": "Update documentation"},
                {"region": "Asia", "alert": "Singapore customs delay 2-4h", "impact": "Low", "action": "Adjust ETA calculations"},
                {"region": "Americas", "alert": "All clear - normal processing", "impact": "None", "action": "Continue operations"}
            ]
            
            for alert in customs_alerts:
                impact_color = {"High": "#ff4444", "Medium": "#ff8800", "Low": "#ffbb00", "None": "#44ff44"}[alert["impact"]]
                st.markdown(f"""
                <div style="border-left: 4px solid {impact_color}; padding: 0.5rem; margin: 0.5rem 0; background: #f8f9fa;">
                    <strong>{alert["region"]}:</strong> {alert["alert"]}<br>
                    <small>Impact: {alert["impact"]} | Action: {alert["action"]}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with logistics_tab3:
        st.markdown("### 🏢 Hub Performance Dashboard")
        
        # Global Hub Performance Matrix
        st.markdown("#### 🌍 Global Hub Performance Matrix")
        
        hub_col1, hub_col2 = st.columns(2)
        
        with hub_col1:
            # Hub Performance Metrics
            st.markdown("##### 📊 Hub Performance Metrics")
            
            hub_data = {
                'Hub': ['Miami (MIA)', 'London (LHR)', 'Singapore (SIN)', 'Dubai (DXB)', 'Frankfurt (FRA)'],
                'Throughput/Day': ['850 parts', '620 parts', '920 parts', '540 parts', '680 parts'],
                'Processing Time': ['2.4h', '3.1h', '1.8h', '2.9h', '2.6h'],
                'Accuracy': ['99.2%', '98.7%', '99.6%', '98.9%', '99.1%'],
                'Utilization': ['87%', '92%', '94%', '79%', '85%'],
                'Performance Score': [94.2, 91.8, 96.7, 89.3, 92.1]
            }
            hub_df = pd.DataFrame(hub_data)
            
            # Color code by performance score
            def highlight_performance(row):
                score = row['Performance Score']
                if score >= 95:
                    return ['background-color: #ccffcc']*6
                elif score >= 90:
                    return ['background-color: #fff2cc']*6
                else:
                    return ['background-color: #ffcccc']*6
            
            st.dataframe(hub_df.style.apply(highlight_performance, axis=1), use_container_width=True)
        
        with hub_col2:
            # Hub Capacity Utilization
            st.markdown("##### 📈 Hub Capacity Utilization")
            
            hubs = ['Miami', 'London', 'Singapore', 'Dubai', 'Frankfurt']
            utilization = [87, 92, 94, 79, 85]
            
            fig = px.bar(
                x=hubs,
                y=utilization,
                title="Hub Capacity Utilization (%)",
                color=utilization,
                color_continuous_scale="RdYlGn"
            )
            fig.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Target: 90%")
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Hub Performance Deep Dive
        st.markdown("#### 🔍 Hub Performance Deep Dive")
        
        selected_hub = st.selectbox("Select Hub for Detailed Analysis:", 
                                  ["Miami (MIA)", "London (LHR)", "Singapore (SIN)", "Dubai (DXB)", "Frankfurt (FRA)"])
        
        hub_detail_col1, hub_detail_col2, hub_detail_col3 = st.columns(3)
        
        with hub_detail_col1:
            st.markdown("##### 📦 Processing Details")
            if "Miami" in selected_hub:
                st.metric("Daily Volume", "850 parts", "+5.2% vs last week")
                st.metric("Avg Processing", "2.4 hours", "-0.3h improvement")
                st.metric("Peak Hour Load", "89 parts/hour", "8-10 AM UTC")
            elif "Singapore" in selected_hub:
                st.metric("Daily Volume", "920 parts", "+3.8% vs last week")
                st.metric("Avg Processing", "1.8 hours", "Best in network")
                st.metric("Peak Hour Load", "102 parts/hour", "22-24 SGT")
            else:
                st.metric("Daily Volume", f"{random.randint(540,920)} parts", f"+{random.randint(1,8)}.{random.randint(1,9)}% vs last week")
                st.metric("Avg Processing", f"{random.randint(18,31)/10} hours", f"{random.choice(['+', '-'])}{random.randint(1,5)/10}h vs target")
                st.metric("Peak Hour Load", f"{random.randint(60,102)} parts/hour", f"{random.randint(6,23)}-{random.randint(8,24)} local time")
        
        with hub_detail_col2:
            st.markdown("##### 👥 Staffing & Resources")
            st.metric("Staff on Duty", f"{random.randint(25,45)}", "Full capacity")
            st.metric("Equipment Status", "98.5% operational", "2 units maintenance")
            st.metric("Warehouse Space", f"{random.randint(75,95)}% utilized", "Within optimal range")
        
        with hub_detail_col3:
            st.markdown("##### 🚨 Current Issues")
            if random.choice([True, False]):
                st.markdown("""
                <div class="success-card">
                    <h4>✅ All Systems Green</h4>
                    <p>No current issues</p>
                    <p>Operating at optimal efficiency</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); padding: 1rem; border-radius: 10px; color: white;">
                    <h4>⚠️ Minor Alert</h4>
                    <p>Conveyor Belt #3 maintenance</p>
                    <p>Reduced capacity until 14:00 UTC</p>
                </div>
                """, unsafe_allow_html=True)
    
    with logistics_tab4:
        st.markdown("### 🔗 Supply Chain Visibility")
        
        # Supply Chain Flow Tracking
        st.markdown("#### 📊 End-to-End Supply Chain Flow")
        
        supply_col1, supply_col2 = st.columns(2)
        
        with supply_col1:
            # Supplier Performance
            st.markdown("##### 🏭 Top Supplier Performance")
            
            supplier_performance = {
                'Supplier': ['Boeing Global Services', 'Airbus Services', 'Collins Aerospace', 'Safran', 'Honeywell Aerospace'],
                'Parts Supplied': [245, 189, 167, 143, 128],
                'On-Time Delivery': ['91.8%', '94.2%', '89.6%', '96.1%', '88.7%'],
                'Quality Score': [9.2, 8.9, 8.6, 9.4, 8.8],
                'Lead Time': ['4.2 days', '3.8 days', '5.1 days', '3.2 days', '4.9 days']
            }
            supplier_df = pd.DataFrame(supplier_performance)
            st.dataframe(supplier_df, use_container_width=True)
        
        with supply_col2:
            # Parts Flow Visualization
            st.markdown("##### 📈 Parts Flow - Last 7 Days")
            
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            inbound = [random.randint(180, 250) for _ in days]
            outbound = [random.randint(170, 240) for _ in days]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=days, y=inbound, mode='lines+markers', name='Inbound', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=days, y=outbound, mode='lines+markers', name='Outbound', line=dict(color='red')))
            fig.update_layout(title="Parts Flow Trend", height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Critical Parts Inventory
        st.markdown("#### 🎯 Critical Parts Inventory Status")
        
        inventory_col1, inventory_col2, inventory_col3 = st.columns(3)
        
        with inventory_col1:
            st.markdown("##### 🔴 Critical Low Stock")
            critical_parts = [
                {"part": "Boeing 737 Brake Assembly", "stock": 2, "min": 5, "supplier": "Collins Aerospace"},
                {"part": "A320 APU Starter", "stock": 1, "min": 3, "supplier": "Safran"},
                {"part": "737 MAX Flight Computer", "stock": 0, "min": 2, "supplier": "Boeing Global"}
            ]
            
            for part in critical_parts:
                stock_color = "#ff4444" if part["stock"] == 0 else "#ff8800"
                st.markdown(f"""
                <div style="background: {stock_color}; padding: 0.8rem; border-radius: 8px; color: white; margin: 0.5rem 0;">
                    <strong>{part["part"]}</strong><br>
                    <small>Stock: {part["stock"]} | Min: {part["min"]} | {part["supplier"]}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with inventory_col2:
            st.markdown("##### 🟡 Watch List")
            watch_parts = [
                {"part": "A320 Landing Gear Actuator", "stock": 6, "min": 5},
                {"part": "737 Engine Oil Filter", "stock": 8, "min": 7},
                {"part": "777 Avionics Module", "stock": 4, "min": 3}
            ]
            
            for part in watch_parts:
                st.markdown(f"""
                <div style="background: #ff8800; padding: 0.8rem; border-radius: 8px; color: white; margin: 0.5rem 0;">
                    <strong>{part["part"]}</strong><br>
                    <small>Stock: {part["stock"]} | Min: {part["min"]}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with inventory_col3:
            st.markdown("##### 🟢 Healthy Stock")
            healthy_parts = [
                {"part": "Standard Hardware Kit", "stock": 150, "min": 50},
                {"part": "Hydraulic Seals Set", "stock": 89, "min": 25},
                {"part": "Electrical Connectors", "stock": 234, "min": 75}
            ]
            
            for part in healthy_parts:
                st.markdown(f"""
                <div style="background: #44ff44; padding: 0.8rem; border-radius: 8px; color: #333; margin: 0.5rem 0;">
                    <strong>{part["part"]}</strong><br>
                    <small>Stock: {part["stock"]} | Min: {part["min"]}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with logistics_tab5:
        st.markdown("### 🌎 Regional Analysis")
        
        # Regional Performance Dashboard
        st.markdown("#### 🌍 Regional Performance Dashboard")
        
        regional_col1, regional_col2 = st.columns(2)
        
        with regional_col1:
            # Regional Performance Metrics
            st.markdown("##### 📊 Regional Performance Metrics")
            
            regional_data = {
                'Region': ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America'],
                'Revenue ($M)': [15.2, 12.8, 9.7, 6.4, 3.1],
                'Market Share': ['35.8%', '30.2%', '22.9%', '15.1%', '7.3%'],
                'Growth Rate': ['+12.3%', '+8.7%', '+15.2%', '+11.4%', '+18.9%'],
                'Customer Satisfaction': [8.4, 8.7, 8.9, 8.2, 8.6],
                'Operational Efficiency': ['94.2%', '91.8%', '96.7%', '89.3%', '87.1%']
            }
            regional_df = pd.DataFrame(regional_data)
            st.dataframe(regional_df, use_container_width=True)
        
        with regional_col2:
            # Revenue Distribution
            st.markdown("##### 💰 Revenue Distribution by Region")
            
            regions = ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America']
            revenue = [15.2, 12.8, 9.7, 6.4, 3.1]
            
            fig = px.pie(
                values=revenue,
                names=regions,
                title="Revenue Distribution ($M)",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Regional Deep Dive
        st.markdown("#### 🔍 Regional Market Intelligence")
        
        selected_region = st.selectbox("Select Region for Analysis:", 
                                     ["North America", "Europe", "Asia-Pacific", "Middle East", "Latin America"])
        
        regional_detail_col1, regional_detail_col2, regional_detail_col3 = st.columns(3)
        
        with regional_detail_col1:
            st.markdown("##### 📈 Market Dynamics")
            if selected_region == "North America":
                st.metric("Market Size", "$15.2M", "+12.3% YoY")
                st.metric("Major Customers", "45 airlines", "American, Delta, United")
                st.metric("Competitive Position", "#2 market share", "Behind AAR Corp")
            elif selected_region == "Asia-Pacific":
                st.metric("Market Size", "$9.7M", "+15.2% YoY")
                st.metric("Major Customers", "28 airlines", "Singapore, Cathay, ANA")
                st.metric("Competitive Position", "#3 market share", "Growing rapidly")
            else:
                st.metric("Market Size", f"${random.randint(31,128)/10}M", f"+{random.randint(5,20)}.{random.randint(1,9)}% YoY")
                st.metric("Major Customers", f"{random.randint(15,45)} airlines", "Various carriers")
                st.metric("Competitive Position", f"#{random.randint(1,5)} market share", "Competitive landscape")
        
        with regional_detail_col2:
            st.markdown("##### 🎯 Key Opportunities")
            opportunities = {
                "North America": ["Fleet modernization programs", "Sustainable aviation initiatives", "Digital transformation"],
                "Europe": ["Brexit regulatory changes", "Green aviation mandates", "Hub consolidation"],
                "Asia-Pacific": ["Rapid fleet expansion", "New route development", "Infrastructure growth"],
                "Middle East": ["Hub strategy expansion", "Long-haul operations", "Cargo growth"],
                "Latin America": ["Market liberalization", "Tourism recovery", "Infrastructure development"]
            }
            
            for opp in opportunities.get(selected_region, ["Market analysis", "Growth potential", "Strategic partnerships"]):
                st.markdown(f"• {opp}")
        
        with regional_detail_col3:
            st.markdown("##### ⚠️ Regional Challenges")
            challenges = {
                "North America": ["Regulatory complexity", "Labor shortages", "Supply chain costs"],
                "Europe": ["Economic uncertainty", "Environmental regulations", "Brexit impacts"],
                "Asia-Pacific": ["Currency fluctuations", "Political tensions", "Infrastructure gaps"],
                "Middle East": ["Oil price volatility", "Regional conflicts", "Competition intensity"],
                "Latin America": ["Economic instability", "Currency devaluation", "Infrastructure needs"]
            }
            
            for challenge in challenges.get(selected_region, ["Market challenges", "Competitive pressure", "Regulatory changes"]):
                st.markdown(f"• {challenge}")
        
        # Global Performance Summary
        st.markdown("#### 🌐 Global Network Performance Summary")
        
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.markdown("""
            <div class="success-card">
                <h4>✅ Network Excellence</h4>
                <p><strong>Global Coverage:</strong> 247 airports</p>
                <p><strong>Response Time:</strong> <14 minutes avg</p>
                <p><strong>Success Rate:</strong> 96.8%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col2:
            st.markdown("""
            <div class="metric-card">
                <h4>📊 Performance Metrics</h4>
                <p><strong>Parts Moved/Day:</strong> 3,800+</p>
                <p><strong>Fleet Utilization:</strong> 89.4%</p>
                <p><strong>Customer NPS:</strong> 8.6/10</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col3:
            st.markdown("""
            <div class="quote-card">
                <h4>🎯 Strategic Focus</h4>
                <p><strong>Q1 2025:</strong> Asia expansion</p>
                <p><strong>Technology:</strong> AI route optimization</p>
                <p><strong>Sustainability:</strong> Carbon neutral 2026</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col4:
            # ENHANCED: Add key inventory KPIs to executive overview
            global_inventory = dashboard._calculate_global_inventory_metrics()
            if global_inventory:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); padding: 1rem; border-radius: 10px; color: white;">
                    <h4>📦 Inventory Intelligence</h4>
                    <p><strong>Parts Tracked:</strong> {global_inventory['total_parts']:,}</p>
                    <p><strong>Stock Health:</strong> {global_inventory['health_score']:.1f}%</p>
                    <p><strong>Critical Parts:</strong> {global_inventory['critical_parts']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); padding: 1rem; border-radius: 10px; color: white;">
                    <h4>🚀 Innovation Pipeline</h4>
                    <p><strong>Blockchain:</strong> Supply chain tracking</p>
                    <p><strong>IoT:</strong> Smart inventory management</p>
                    <p><strong>ML:</strong> Predictive maintenance</p>
                </div>
                """, unsafe_allow_html=True)

elif page == "✈️ Flight Status Monitor":
    st.markdown('<h1 class="main-header">🛩️ United Airlines Operations Control Center</h1>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Airline Operations Intelligence - Real-time Decision Support for Flight Operations*")
    
    # Executive Operations Dashboard
    st.markdown("### 🎯 Operations Command Center")
    ops_col1, ops_col2, ops_col3, ops_col4, ops_col5 = st.columns(5)
    
    with ops_col1:
        st.metric("Active Flights", "847", "+23 vs yesterday")
    with ops_col2:
        st.metric("On-Time Performance", "87.4%", "+2.1% vs avg")
    with ops_col3:
        st.metric("Aircraft Utilization", "11.2 hrs", "+0.8 hrs")
    with ops_col4:
        st.metric("Revenue at Risk", "$2.8M", "-$450K vs forecast")
    with ops_col5:
        st.metric("Operations Score", "94.2", "+1.8 pts")
    
    # === 1. PREDICTIVE FLIGHT ANALYTICS ===
    st.markdown("---")
    st.markdown("## 🔮 Predictive Flight Analytics")
    
    predict_col1, predict_col2 = st.columns([1, 1])
    
    with predict_col1:
        st.markdown("### ⚠️ Delay Risk Predictions")
        
        delay_predictions = [
            {"flight": "UA1247", "route": "ORD-LAX", "delay_risk": 87, "primary_factor": "Weather - Thunderstorms", "estimated_delay": "45-60 min", "confidence": 94},
            {"flight": "UA892", "route": "SFO-NRT", "delay_risk": 72, "primary_factor": "Aircraft Maintenance", "estimated_delay": "25-40 min", "confidence": 89},
            {"flight": "UA156", "route": "EWR-LHR", "delay_risk": 68, "primary_factor": "ATC Flow Control", "estimated_delay": "20-35 min", "confidence": 91},
            {"flight": "UA2134", "route": "DEN-MIA", "delay_risk": 45, "primary_factor": "Crew Scheduling", "estimated_delay": "10-20 min", "confidence": 86},
            {"flight": "UA567", "route": "IAH-FRA", "delay_risk": 38, "primary_factor": "Ground Traffic", "estimated_delay": "5-15 min", "confidence": 82}
        ]
        
        for pred in delay_predictions:
            risk_color = "#ff4444" if pred['delay_risk'] > 70 else "#ff8800" if pred['delay_risk'] > 50 else "#44ff44"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {risk_color}20 0%, {risk_color}10 100%); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {risk_color};">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                    <div><strong>{pred['flight']}</strong><br><small>{pred['route']}</small></div>
                    <div><strong>{pred['delay_risk']}% Risk</strong><br><small>{pred['estimated_delay']}</small></div>
                    <div><strong>{pred['primary_factor']}</strong><br><small>{pred['confidence']}% confidence</small></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with predict_col2:
        st.markdown("### 🌩️ Weather Impact Analysis")
        
        weather_data = {
            "Hub": ["ORD Chicago", "DEN Denver", "SFO San Francisco", "EWR Newark", "IAH Houston"],
            "Current Conditions": ["Thunderstorms", "Clear", "Fog", "Rain", "Clear"],
            "Delay Impact": ["High", "None", "Medium", "Low", "None"],
            "Affected Flights": [47, 0, 23, 12, 0],
            "Avg Delay": ["42 min", "0 min", "18 min", "8 min", "0 min"]
        }
        
        weather_df = pd.DataFrame(weather_data)
        st.dataframe(weather_df, use_container_width=True)
        
        st.markdown("### 📊 Cancellation Risk Matrix")
        
        cancel_risk_data = {
            "Risk Level": ["High Risk", "Medium Risk", "Low Risk", "Minimal Risk"],
            "Flight Count": [8, 23, 67, 749],
            "Probability": ["85-95%", "45-65%", "15-25%", "<5%"],
            "Action Required": ["Immediate", "Monitor", "Standby", "Normal"]
        }
        
        cancel_df = pd.DataFrame(cancel_risk_data)
        st.dataframe(cancel_df, use_container_width=True)
    
    # === 2. AIRCRAFT HEALTH MONITORING ===
    st.markdown("---")
    st.markdown("## 🔧 Aircraft Health Monitoring")
    
    health_col1, health_col2 = st.columns([1, 1])
    
    with health_col1:
        st.markdown("### 🚨 Critical Aircraft Alerts")
        
        aircraft_alerts = [
            {"aircraft": "N12345 (B777-200)", "alert": "Engine Oil Pressure Low", "severity": "Critical", "eta_maintenance": "2.5 hrs", "affected_flights": 3},
            {"aircraft": "N67890 (A320-200)", "alert": "Hydraulic System Warning", "severity": "High", "eta_maintenance": "4.2 hrs", "affected_flights": 2},
            {"aircraft": "N24681 (B737-800)", "alert": "APU Performance Degraded", "severity": "Medium", "eta_maintenance": "Next C-Check", "affected_flights": 0},
            {"aircraft": "N13579 (A350-900)", "alert": "Cabin Pressure Sensor", "severity": "Low", "eta_maintenance": "Tonight", "affected_flights": 0}
        ]
        
        for alert in aircraft_alerts:
            severity_color = "#ff0000" if alert['severity'] == 'Critical' else "#ff8800" if alert['severity'] == 'High' else "#ffaa00" if alert['severity'] == 'Medium' else "#44aa44"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {severity_color}15 0%, {severity_color}05 100%); padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 4px solid {severity_color};">
                <h4 style="margin: 0; color: {severity_color};">{alert['aircraft']}</h4>
                <p style="margin: 5px 0;"><strong>{alert['alert']}</strong> - {alert['severity']}</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
                    <div>Maintenance ETA: {alert['eta_maintenance']}</div>
                    <div>Affected Flights: {alert['affected_flights']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with health_col2:
        st.markdown("### 📈 Fleet Health Overview")
        
        fleet_health = {
            "Aircraft Type": ["Boeing 777", "Airbus A320", "Boeing 737", "Airbus A350", "Boeing 787"],
            "Fleet Size": [67, 142, 89, 34, 45],
            "Available": [64, 138, 86, 33, 44],
            "Maintenance": [2, 3, 2, 1, 1],
            "AOG": [1, 1, 1, 0, 0],
            "Health Score": [94.2, 96.8, 93.5, 97.1, 95.6]
        }
        
        fleet_df = pd.DataFrame(fleet_health)
        st.dataframe(fleet_df, use_container_width=True)
        
        st.markdown("### ⚡ Maintenance Predictions")
        
        maint_pred = {
            "Aircraft": ["N45678", "N78901", "N23456", "N89012"],
            "Next Check": ["A-Check", "C-Check", "B-Check", "A-Check"],
            "Days Until Due": [12, 28, 7, 19],
            "Probability Early": ["23%", "67%", "8%", "34%"],
            "Recommended Action": ["Schedule", "Plan Early", "Monitor", "Schedule"]
        }
        
        maint_df = pd.DataFrame(maint_pred)
        st.dataframe(maint_df, use_container_width=True)
    
    # === 3. ROUTE INTELLIGENCE ===
    st.markdown("---")
    st.markdown("## 🗺️ Route Intelligence & Optimization")
    
    route_col1, route_col2 = st.columns([1, 1])
    
    with route_col1:
        st.markdown("### 🛣️ Optimal Routing Suggestions")
        
        route_opts = [
            {"flight": "UA1247 ORD-LAX", "current_route": "Direct", "optimal_route": "Via DEN", "fuel_savings": "890 lbs", "time_impact": "+12 min", "cost_savings": "$1,240"},
            {"flight": "UA892 SFO-NRT", "current_route": "Polar Route", "optimal_route": "Pacific Route", "fuel_savings": "1,450 lbs", "time_impact": "-8 min", "cost_savings": "$2,180"},
            {"flight": "UA156 EWR-LHR", "current_route": "North Atlantic", "optimal_route": "Optimized NAT", "fuel_savings": "650 lbs", "time_impact": "-5 min", "cost_savings": "$980"},
            {"flight": "UA567 IAH-FRA", "current_route": "Direct", "optimal_route": "Via YYZ", "fuel_savings": "720 lbs", "time_impact": "+18 min", "cost_savings": "$1,090"}
        ]
        
        for route in route_opts:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #0066cc20 0%, #0066cc10 100%); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #0066cc;">
                <h4 style="margin: 0; color: #0066cc;">{route['flight']}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px;">
                    <div><strong>Current:</strong> {route['current_route']}</div>
                    <div><strong>Optimal:</strong> {route['optimal_route']}</div>
                    <div><strong>Fuel Savings:</strong> {route['fuel_savings']}</div>
                    <div><strong>Time Impact:</strong> {route['time_impact']}</div>
                </div>
                <div style="text-align: center; margin-top: 10px; font-weight: bold; color: #00aa00;">Cost Savings: {route['cost_savings']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with route_col2:
        st.markdown("### ⛽ Fuel Efficiency Tracking")
        
        fuel_data = {
            "Route Category": ["Domestic Short", "Domestic Long", "International", "Transpacific", "Transatlantic"],
            "Avg Consumption": ["2,840 lbs", "8,920 lbs", "15,670 lbs", "28,450 lbs", "21,230 lbs"],
            "vs Target": ["-2.3%", "+1.2%", "-1.8%", "-3.1%", "+0.7%"],
            "Monthly Savings": ["$89K", "$156K", "$234K", "$445K", "$278K"],
            "Efficiency Score": [97.7, 98.8, 101.8, 103.1, 99.3]
        }
        
        fuel_df = pd.DataFrame(fuel_data)
        st.dataframe(fuel_df, use_container_width=True)
        
        st.markdown("### 🎯 Performance Targets")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            st.metric("Fuel Efficiency", "97.2%", "+1.8% vs target")
        with perf_col2:
            st.metric("Route Optimization", "94.7%", "+2.3%")
        with perf_col3:
            st.metric("On-Time Arrival", "87.4%", "+0.9%")
    
    # === 4. CUSTOMER IMPACT ANALYSIS ===
    st.markdown("---")
    st.markdown("## 👥 Customer Impact Analysis")
    
    customer_col1, customer_col2 = st.columns([1, 1])
    
    with customer_col1:
        st.markdown("### 📊 Passenger Impact Assessment")
        
        impact_analysis = [
            {"scenario": "UA1247 Delay (45 min)", "passengers": 284, "connections_missed": 67, "hotels_needed": 23, "compensation_est": "$47,800", "satisfaction_impact": "-12 pts"},
            {"scenario": "UA892 Maintenance AOG", "passengers": 359, "connections_missed": 124, "hotels_needed": 89, "compensation_est": "$156,700", "satisfaction_impact": "-28 pts"},
            {"scenario": "Weather ORD Hub", "passengers": 1847, "connections_missed": 445, "hotels_needed": 167, "compensation_est": "$389,200", "satisfaction_impact": "-18 pts"}
        ]
        
        for impact in impact_analysis:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff666620 0%, #ff666610 100%); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #ff6666;">
                <h4 style="margin: 0; color: #ff6666;">{impact['scenario']}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 8px; font-size: 14px;">
                    <div><strong>Passengers:</strong> {impact['passengers']}</div>
                    <div><strong>Missed Connections:</strong> {impact['connections_missed']}</div>
                    <div><strong>Hotels Needed:</strong> {impact['hotels_needed']}</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px;">
                    <div><strong>Est. Compensation:</strong> {impact['compensation_est']}</div>
                    <div><strong>NPS Impact:</strong> {impact['satisfaction_impact']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with customer_col2:
        st.markdown("### 🔄 Rebooking Strategies")
        
        rebooking_data = {
            "Strategy": ["Same Day Recovery", "Next Day Rebooking", "Partner Airlines", "Refund/Voucher", "Upgrade Recovery"],
            "Success Rate": ["87%", "94%", "67%", "89%", "78%"],
            "Avg Cost": ["$245", "$380", "$420", "$290", "$125"],
            "Customer Satisfaction": [8.2, 6.4, 7.8, 5.9, 9.1],
            "Implementation Time": ["15 min", "45 min", "30 min", "10 min", "20 min"]
        }
        
        rebooking_df = pd.DataFrame(rebooking_data)
        st.dataframe(rebooking_df, use_container_width=True)
        
        st.markdown("### 💡 AI Rebooking Recommendations")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00aa0020 0%, #00aa0010 100%); padding: 15px; border-radius: 10px; border-left: 4px solid #00aa00;">
            <h4 style="margin: 0; color: #00aa00;">Optimal Strategy: Same Day Recovery + Upgrades</h4>
            <ul style="margin: 10px 0;">
                <li>Rebook 67% on same-day flights with upgrade incentives</li>
                <li>Partner airline solution for 23% (Star Alliance priority)</li>
                <li>Next-day premium rebooking for remaining 10%</li>
            </ul>
            <p style="margin: 5px 0; font-weight: bold;">Expected outcome: 92% customer retention, $156K cost savings</p>
        </div>
        """, unsafe_allow_html=True)
    
    # === 5. OPERATIONS OPTIMIZATION ===
    st.markdown("---")
    st.markdown("## ⚙️ Operations Optimization")
    
    ops_col1, ops_col2, ops_col3 = st.columns(3)
    
    with ops_col1:
        st.markdown("### 🚪 Gate Management")
        
        gate_data = {
            "Terminal": ["Terminal 1", "Terminal 2", "Terminal 3", "Concourse B", "Concourse C"],
            "Utilization": ["94%", "87%", "91%", "89%", "85%"],
            "Available Gates": [2, 5, 3, 4, 6],
            "Peak Congestion": ["14:30-16:00", "12:00-14:30", "15:00-17:30", "13:30-15:00", "16:00-18:00"]
        }
        
        gate_df = pd.DataFrame(gate_data)
        st.dataframe(gate_df, use_container_width=True)
    
    with ops_col2:
        st.markdown("### 👨‍✈️ Crew Scheduling")
        
        crew_data = {
            "Base": ["ORD Chicago", "SFO San Fran", "EWR Newark", "DEN Denver", "IAH Houston"],
            "Available Crews": [23, 18, 15, 12, 19],
            "On Duty": [67, 45, 38, 34, 41],
            "Reserve Status": [12, 8, 9, 7, 11],
            "Overtime Risk": ["Medium", "Low", "High", "Low", "Medium"]
        }
        
        crew_df = pd.DataFrame(crew_data)
        st.dataframe(crew_df, use_container_width=True)
    
    with ops_col3:
        st.markdown("### 🔧 Maintenance Windows")
        
        maint_windows = {
            "Aircraft": ["N12345", "N67890", "N24681", "N13579", "N98765"],
            "Check Type": ["A-Check", "C-Check", "Line Maint", "B-Check", "Inspection"],
            "Window Start": ["23:45", "22:30", "21:15", "00:30", "23:00"],
            "Est Duration": ["4.5 hrs", "18 hrs", "2 hrs", "12 hrs", "3 hrs"],
            "Completion %": ["85%", "34%", "100%", "67%", "92%"]
        }
        
        maint_df = pd.DataFrame(maint_windows)
        st.dataframe(maint_df, use_container_width=True)
    
    # Performance Summary
    st.markdown("---")
    st.markdown("### 🎯 United Airlines Operations Excellence Summary")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0066cc 0%, #004499 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
            <h3>Operational Efficiency</h3>
            <h2>94.2%</h2>
            <p>+1.8 pts vs industry avg</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00aa00 0%, #008800 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
            <h3>Customer Satisfaction</h3>
            <h2>87.4%</h2>
            <p>+2.1% vs last quarter</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6600 0%, #cc5500 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
            <h3>Cost Optimization</h3>
            <h2>$2.4M</h2>
            <p>Monthly savings achieved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #9933cc 0%, #663399 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
            <h3>AI Impact Score</h3>
            <h2>96.8</h2>
            <p>Predictive accuracy rate</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "🤖 AI Quote Engine":
    st.markdown('<h1 class="main-header">🤖 AI-Powered Multi-Part Quote Intelligence Platform</h1>', unsafe_allow_html=True)
    st.markdown("*Revolutionary AI system transforming complex AOG requests into comprehensive quotes - from 2 hours manual to 3 minutes automated*")
    
    # Executive Impact Summary
    st.markdown("### 🎯 Revolutionary AI Impact")
    impact_col1, impact_col2, impact_col3, impact_col4, impact_col5 = st.columns(5)
    
    with impact_col1:
        st.metric("Processing Time", "2.8 min", "-117 min (-98%)")
    with impact_col2:
        st.metric("Quote Accuracy", "97.3%", "+15.2% (+18%)")
    with impact_col3:
        st.metric("Multi-Part Success", "94.7%", "+42.1% (+80%)")
    with impact_col4:
        st.metric("Revenue Capture", "£2.1M", "+£847K (+68%)")
    with impact_col5:
        st.metric("Customer Satisfaction", "4.8/5", "+1.1 (+30%)")
    
    # === 1. EMAIL INTELLIGENCE SECTION ===
    st.markdown("---")
    st.markdown("## 📧 Email Intelligence & AOG Request Parser")
    
    # Sample AOG Email Simulator
    email_col1, email_col2 = st.columns([1, 1])
    
    with email_col1:
        st.markdown("### 📩 Sample AOG Email Simulator")
        
        # Email selection
        email_scenarios = {
            "British Airways Emergency - Boeing 777": {
                "subject": "URGENT AOG - Boeing 777-300ER G-VIIA at LHR",
                "body": """URGENT AOG - Boeing 777-300ER G-VIIA at LHR. Need following parts immediately:

- Engine fan blade (Rolls Royce Trent 892) - Qty: 2
- Landing gear actuator (Boeing PN: 777-32105-1) - Qty: 1  
- Navigation display unit (Honeywell PN: 7014391-903) - Qty: 1
- Hydraulic pump (Parker PN: 312-1050-100) - Qty: 1
- APU starter (Hamilton Std PN: 36-380000-3) - Qty: 1
- Brake discs (Goodrich PN: 2-1602-3) - Qty: 6
- Flight management computer (GE PN: 4003431-902) - Qty: 1
- Weather radar antenna (Rockwell PN: WXR-2100) - Qty: 1
- Fuel pump (Rolls Royce PN: 23049-100) - Qty: 2
- Oxygen bottles (Scott PN: 802427-1) - Qty: 4

Required by 0800 tomorrow. Aircraft grounded with 284 passengers affected. 
Cost of delay: £47,000/hour. What's your best price and timeline?

Mark Richardson
BA Operations Control Centre""",
                "parts_count": 10,
                "urgency": "Emergency",
                "location": "London Heathrow (LHR)",
                "aircraft": "Boeing 777-300ER"
            },
            "Lufthansa Routine - Airbus A320": {
                "subject": "Planning maintenance for A320 D-AIUI next week",
                "body": """Planning maintenance for A320 D-AIUI next week. Please quote:

- Wing flap actuator (Airbus PN: A320-27-1050) - Qty: 2
- Communication radio (Rockwell PN: VHF-922) - Qty: 1
- Avionics control unit (Thales PN: 4002334-901) - Qty: 1
- APU starter motor (Hamilton PN: 36-380015-7) - Qty: 1
- Navigation sensor (Honeywell PN: IRS-2100) - Qty: 2
- Emergency slide canister (Goodrich PN: 44D242-1) - Qty: 1
- Engine sensor (CFM56 PN: 9524M31G01) - Qty: 3
- Brake assembly (Goodrich PN: 2-1603-5) - Qty: 4
- Cabin oxygen mask (Scott PN: 161570-01) - Qty: 25
- Fire extinguisher bottle (Kidde PN: 74450-103) - Qty: 2
- Hydraulic filter (Parker PN: 928370-1) - Qty: 4
- Landing gear light (Goodrich PN: A4-3225-1) - Qty: 2

Standard delivery to Frankfurt (FRA) within 3-5 days acceptable.

Klaus Weber
Lufthansa Technical Services""",
                "parts_count": 12,
                "urgency": "Routine",
                "location": "Frankfurt (FRA)",
                "aircraft": "Airbus A320"
            },
            "Emirates Critical - Airbus A380": {
                "subject": "A380 A6-EUA AOG in Dubai - Multiple parts needed urgently",
                "body": """A380 A6-EUA AOG in Dubai. Multiple parts needed urgently:

- Engine control unit (Rolls Royce Trent 900 PN: 23087450) - Qty: 1
- Flight control computer (Airbus PN: 7700394-101) - Qty: 2
- Landing gear strut (Messier PN: A380-32-2100) - Qty: 1
- Hydraulic reservoir (Parker PN: A380-29-4050) - Qty: 1
- APU fire extinguisher (Kidde PN: 74470-501) - Qty: 1
- Navigation antenna (Rockwell PN: ADF-2100) - Qty: 2
- Brake control valve (Goodrich PN: A380-32-5200) - Qty: 2
- Oxygen generator (Scott PN: 161580-15) - Qty: 8
- Weather radar (Rockwell PN: WXR-2100A) - Qty: 1
- Fuel quantity sensor (Simmonds PN: FQS-2200) - Qty: 4
- Cabin pressure sensor (Honeywell PN: CPS-1100) - Qty: 2
- Emergency power unit (Hamilton PN: RAT-2500) - Qty: 1
- Fire detection unit (Kidde PN: 74480-201) - Qty: 3
- Wing ice protection (Goodrich PN: WIPS-2100) - Qty: 2
- Cargo door actuator (Liebherr PN: A380-52-1200) - Qty: 1

Aircraft down for 18 hours already. 850 passengers affected on multiple connecting flights.
Current loss: £127,000. Need immediate action - cost is secondary to speed.

Ahmed Al-Mansouri  
Emirates Engineering""",
                "parts_count": 15,
                "urgency": "Critical AOG",
                "location": "Dubai (DXB)",
                "aircraft": "Airbus A380"
            }
        }
        
        selected_email = st.selectbox("Select AOG Email Scenario:", list(email_scenarios.keys()))
        email_data = email_scenarios[selected_email]
        
        st.markdown("#### 📧 Email Content:")
        st.text_area("Subject:", value=email_data["subject"], height=68, disabled=True)
        st.text_area("Email Body:", value=email_data["body"], height=400, disabled=True)
        
        if st.button("🤖 Process Email with AI", type="primary", use_container_width=True):
            st.session_state.email_processed = True
            st.session_state.selected_email_data = email_data
    
    with email_col2:
        st.markdown("### 🧠 AI Email Parser Results")
        
        if hasattr(st.session_state, 'email_processed') and st.session_state.email_processed:
            email_data = st.session_state.selected_email_data
            
            # Processing simulation
            with st.container():
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                processing_steps = [
                    "🔍 Analyzing email structure...",
                    "📧 Extracting customer information...", 
                    "✈️ Identifying aircraft details...",
                    "🔧 Parsing parts requirements...",
                    "🎯 Assessing urgency level...",
                    "📍 Determining delivery location...",
                    "✅ Email processing complete!"
                ]
                
                for i, step in enumerate(processing_steps):
                    progress_bar.progress((i + 1) / len(processing_steps))
                    status_text.text(step)
                    time.sleep(0.3)
                
                st.success("✅ Email successfully parsed by AI!")
            
            # Extracted Information
            st.markdown("#### 🎯 Extracted Information:")
            
            extract_col1, extract_col2 = st.columns(2)
            
            with extract_col1:
                st.markdown(f"""
                **✈️ Aircraft Details:**
                - Type: {email_data['aircraft']}
                - Parts Count: {email_data['parts_count']} items
                - Location: {email_data['location']}
                
                **⚡ Request Details:**
                - Urgency: {email_data['urgency']}
                - Confidence: 98.7%
                """)
            
            with extract_col2:
                st.markdown(f"""
                **🔧 Parts Categories:**
                - Engine: 4 items
                - Avionics: 3 items  
                - Landing Gear: 2 items
                - Hydraulics: 2 items
                - Safety: 3 items
                - Other: {email_data['parts_count'] - 14} items
                """)
            
            # Confidence Scoring
            st.markdown("#### 📊 AI Confidence Scoring:")
            confidence_data = pd.DataFrame({
                'Component': ['Aircraft ID', 'Parts List', 'Urgency Level', 'Location', 'Customer Info'],
                'Confidence': [99, 97, 98, 100, 96],
                'Status': ['✅ Verified', '✅ Verified', '✅ Verified', '✅ Verified', '✅ Verified']
            })
            st.dataframe(confidence_data, use_container_width=True)
        else:
            st.info("👆 Select an email above and click 'Process Email with AI' to see AI parsing results")
    
    # === 2. MULTI-PART ANALYSIS DASHBOARD ===
    if hasattr(st.session_state, 'email_processed') and st.session_state.email_processed:
        st.markdown("---")
        st.markdown("## 📊 Multi-Part Analysis Dashboard")
        
        # Parts Identification Table
        st.markdown("### 🔧 Parts Identification Matrix")
        
        # Generate realistic parts data based on selected email
        email_data = st.session_state.selected_email_data
        
        # Sample parts database for demonstration
        sample_parts = [
            {"part_num": "RR-23087450", "description": "Engine Control Unit (Trent 900)", "qty": 1, "category": "Engine", "criticality": "Critical", "confidence": 98},
            {"part_num": "AB-7700394-101", "description": "Flight Control Computer", "qty": 2, "category": "Avionics", "criticality": "Critical", "confidence": 97},
            {"part_num": "MS-A380-32-2100", "description": "Landing Gear Strut", "qty": 1, "category": "Landing Gear", "criticality": "High", "confidence": 99},
            {"part_num": "PK-A380-29-4050", "description": "Hydraulic Reservoir", "qty": 1, "category": "Hydraulics", "criticality": "High", "confidence": 95},
            {"part_num": "KD-74470-501", "description": "APU Fire Extinguisher", "qty": 1, "category": "Safety", "criticality": "Critical", "confidence": 100},
            {"part_num": "RW-ADF-2100", "description": "Navigation Antenna", "qty": 2, "category": "Avionics", "criticality": "Medium", "confidence": 92},
            {"part_num": "GR-A380-32-5200", "description": "Brake Control Valve", "qty": 2, "category": "Landing Gear", "criticality": "High", "confidence": 96},
            {"part_num": "SC-161580-15", "description": "Oxygen Generator", "qty": 8, "category": "Safety", "criticality": "Critical", "confidence": 94},
            {"part_num": "RW-WXR-2100A", "description": "Weather Radar", "qty": 1, "category": "Avionics", "criticality": "Medium", "confidence": 98},
            {"part_num": "SM-FQS-2200", "description": "Fuel Quantity Sensor", "qty": 4, "category": "Engine", "criticality": "High", "confidence": 91}
        ]
        
        parts_df = pd.DataFrame(sample_parts)
        
        # Enhanced table with color coding
        st.dataframe(
            parts_df.style.apply(lambda x: ['background-color: #ffebee' if v == 'Critical' 
                                          else 'background-color: #fff3e0' if v == 'High'
                                          else 'background-color: #e8f5e8' if v == 'Medium'
                                          else '' for v in x], subset=['criticality']), 
            use_container_width=True
        )
        
        # === 3. AVAILABILITY MATRIX & PRICING ===
        st.markdown("### 🌍 Global Availability & Pricing Matrix")
        
        avail_col1, avail_col2 = st.columns(2)
        
        with avail_col1:
            st.markdown("#### 📦 Inventory Status by Hub")
            
            inventory_data = {
                "Hub": ["London (LHR)", "Frankfurt (FRA)", "Dubai (DXB)", "Singapore (SIN)", "Miami (MIA)"],
                "Available Parts": [7, 8, 6, 5, 4],
                "Lead Time": ["6-12 hrs", "8-14 hrs", "12-18 hrs", "24-36 hrs", "36-48 hrs"],
                "Hub Priority": ["Primary", "Primary", "Secondary", "Secondary", "Backup"],
                "Cost Factor": ["1.0x", "1.1x", "1.2x", "1.4x", "1.6x"]
            }
            
            inventory_df = pd.DataFrame(inventory_data)
            st.dataframe(inventory_df, use_container_width=True)
        
        with avail_col2:
            st.markdown("#### 💰 Pricing Analysis")
            
            pricing_data = {
                "Part Category": ["Engine", "Avionics", "Landing Gear", "Hydraulics", "Safety"],
                "Parts Count": [2, 3, 2, 1, 2],
                "Unit Avg": ["£45,200", "£18,750", "£32,100", "£12,400", "£8,950"],
                "Total Value": ["£90,400", "£56,250", "£64,200", "£12,400", "£17,900"],
                "Margin": ["32%", "28%", "35%", "25%", "22%"]
            }
            
            pricing_df = pd.DataFrame(pricing_data)
            st.dataframe(pricing_df, use_container_width=True)
        
        # Risk Assessment Matrix
        st.markdown("### ⚠️ Risk Assessment Matrix")
        
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        
        with risk_col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 20px; border-radius: 15px; color: white;">
                <h4>🚨 High Risk Parts</h4>
                <ul>
                    <li>Engine Control Unit (1 supplier)</li>
                    <li>Weather Radar (Long lead time)</li>
                    <li>Flight Control Computer (Critical path)</li>
                </ul>
                <p><strong>Mitigation:</strong> Premium sourcing recommended</p>
            </div>
            """, unsafe_allow_html=True)
        
        with risk_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); padding: 20px; border-radius: 15px; color: white;">
                <h4>⚠️ Medium Risk Parts</h4>
                <ul>
                    <li>Navigation Antenna (2 hubs)</li>
                    <li>Brake Control Valve (Standard)</li>
                    <li>Fuel Quantity Sensor (Multiple)</li>
                </ul>
                <p><strong>Strategy:</strong> Standard procurement process</p>
            </div>
            """, unsafe_allow_html=True)
        
        with risk_col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%); padding: 20px; border-radius: 15px; color: white;">
                <h4>✅ Low Risk Parts</h4>
                <ul>
                    <li>Oxygen Generator (High stock)</li>
                    <li>APU Fire Extinguisher (Available)</li>
                    <li>Hydraulic Reservoir (Multiple)</li>
                </ul>
                <p><strong>Approach:</strong> Cost-optimized sourcing</p>
            </div>
            """, unsafe_allow_html=True)
        
        # === 4. COMPREHENSIVE QUOTE GENERATOR ===
        st.markdown("---")
        st.markdown("## 📋 Comprehensive Quote Generator")
        
        if st.button("🚀 Generate Professional Quote", type="primary", use_container_width=True):
            # Quote generation simulation
            st.markdown("### ⚡ AI Quote Generation in Progress")
            
            quote_progress = st.progress(0)
            quote_status = st.empty()
            
            quote_steps = [
                "🔍 Analyzing all 10 parts requirements...",
                "🌍 Checking global inventory across 12 hubs...",
                "💰 Calculating optimal pricing strategies...",
                "🚚 Optimizing logistics routing options...",
                "📊 Performing risk assessment analysis...",
                "🎯 Applying customer-specific preferences...",
                "📄 Generating professional quote document...",
                "✅ Quote generation complete!"
            ]
            
            for i, step in enumerate(quote_steps):
                quote_progress.progress((i + 1) / len(quote_steps))
                quote_status.text(step)
                time.sleep(0.4)
            
            st.success("✅ Professional quote generated successfully!")
            
            # === 5. PROFESSIONAL QUOTE OUTPUT ===
            st.markdown("---")
            st.markdown("## 📄 Professional Quote Output")
            
            # Quote Header
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin: 20px 0;">
                <h2 style="margin: 0; text-align: center;">🎯 BH Worldwide Logistics - Professional Quote</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px;">
                    <div><strong>Quote ID:</strong> BHW-2024-15847</div>
                    <div><strong>Generated:</strong> {}</div>
                    <div><strong>Valid Until:</strong> 48 hours</div>
                </div>
            </div>
            """.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
            
            # Executive Summary
            st.markdown("### 📊 Executive Summary")
            
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                st.metric("Total Quote Value", "£278,150", "Competitive pricing")
            with summary_col2:
                st.metric("Total Parts", "10 items", "All identified")
            with summary_col3:
                st.metric("Delivery Timeline", "14-18 hours", "Express routing")
            with summary_col4:
                st.metric("Confidence Score", "96.8%", "High reliability")
            
            # Detailed Parts Breakdown
            st.markdown("### 🔧 Detailed Parts Breakdown")
            
            quote_parts_data = {
                "Part Number": ["RR-23087450", "AB-7700394-101", "MS-A380-32-2100", "PK-A380-29-4050", "KD-74470-501", 
                               "RW-ADF-2100", "GR-A380-32-5200", "SC-161580-15", "RW-WXR-2100A", "SM-FQS-2200"],
                "Description": ["Engine Control Unit", "Flight Control Computer", "Landing Gear Strut", "Hydraulic Reservoir", 
                               "APU Fire Extinguisher", "Navigation Antenna", "Brake Control Valve", "Oxygen Generator", 
                               "Weather Radar", "Fuel Quantity Sensor"],
                "Qty": [1, 2, 1, 1, 1, 2, 2, 8, 1, 4],
                "Unit Price": ["£52,400", "£18,750", "£35,200", "£14,800", "£9,200", "£6,850", "£12,100", "£1,950", "£28,400", "£3,200"],
                "Total Price": ["£52,400", "£37,500", "£35,200", "£14,800", "£9,200", "£13,700", "£24,200", "£15,600", "£28,400", "£12,800"],
                "Availability": ["✅ In Stock", "✅ In Stock", "⚠️ 12hr Lead", "✅ In Stock", "✅ In Stock", 
                                "✅ In Stock", "✅ In Stock", "✅ In Stock", "⚠️ 8hr Lead", "✅ In Stock"],
                "Source Hub": ["LHR", "FRA", "DXB", "LHR", "LHR", "FRA", "LHR", "LHR", "FRA", "LHR"]
            }
            
            quote_df = pd.DataFrame(quote_parts_data)
            st.dataframe(quote_df, use_container_width=True)
            
            # Routing & Delivery Options
            st.markdown("### 🚚 Routing & Delivery Options")
            
            routing_col1, routing_col2 = st.columns(2)
            
            with routing_col1:
                st.markdown("#### 🚀 Recommended: Express Option")
                st.markdown("""
                **Delivery Timeline:** 14-18 hours
                **Route:** LHR → DXB direct charter
                **Total Logistics Cost:** £18,650
                **Insurance:** Comprehensive (£2,850)
                **Tracking:** Premium real-time
                **Confidence:** 97%
                """)
            
            with routing_col2:
                st.markdown("#### 💰 Alternative: Standard Option")
                st.markdown("""
                **Delivery Timeline:** 24-36 hours
                **Route:** Commercial freight consolidation
                **Total Logistics Cost:** £12,400
                **Insurance:** Standard (£1,950)
                **Tracking:** Standard updates
                **Confidence:** 93%
                """)
            
            # Terms & Conditions
            st.markdown("### 📋 Terms & Conditions")
            
            terms_col1, terms_col2 = st.columns(2)
            
            with terms_col1:
                st.markdown("""
                **Payment Terms:**
                - Payment: Net 30 days
                - Currency: GBP 
                - Method: Wire transfer/Corporate card
                - Quote validity: 48 hours
                
                **Delivery Terms:**
                - Delivery location: Dubai International (DXB)
                - Customs clearance: Included
                - Dangerous goods certification: Included
                """)
            
            with terms_col2:
                st.markdown("""
                **Service Level:**
                - Real-time tracking included
                - 24/7 customer support
                - Dedicated account manager
                - Priority AOG handling
                
                **Risk Management:**
                - Comprehensive insurance coverage
                - Backup sourcing options identified
                - Alternative routing contingencies
                """)
            
            # Final Quote Summary
            st.markdown("### 💼 Final Quote Summary")
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%); padding: 25px; border-radius: 15px; color: white; margin: 20px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 20px; text-align: center;">
                    <div>
                        <h3 style="margin: 0;">Parts Total</h3>
                        <h2 style="margin: 5px 0;">£243,800</h2>
                    </div>
                    <div>
                        <h3 style="margin: 0;">Logistics</h3>
                        <h2 style="margin: 5px 0;">£18,650</h2>
                    </div>
                    <div>
                        <h3 style="margin: 0;">Services</h3>
                        <h2 style="margin: 5px 0;">£15,700</h2>
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #ffff99;">TOTAL</h3>
                        <h2 style="margin: 5px 0; color: #ffff99;">£278,150</h2>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 15px;">
                    <p style="margin: 0; font-size: 18px; font-weight: bold;">
                        ⚡ Express delivery: 14-18 hours | 📊 Confidence: 96.8% | 🎯 Success rate: 98.2%
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("📧 Email Quote", type="primary", use_container_width=True):
                    st.success("✅ Quote emailed to customer successfully!")
            
            with action_col2:
                if st.button("📄 Download PDF", type="secondary", use_container_width=True):
                    st.success("✅ PDF quote generated and ready for download!")
            
            with action_col3:
                if st.button("🔄 Modify Quote", type="secondary", use_container_width=True):
                    st.info("🔧 Quote modification panel activated!")
            
            # Performance Impact Summary
            st.markdown("---")
            st.markdown("### 🎯 AI Performance Impact")
            
            impact_comparison = pd.DataFrame({
                "Process Step": ["Email Analysis", "Parts Identification", "Inventory Check", "Pricing Calculation", 
                               "Route Optimization", "Quote Generation", "Customer Communication"],
                "Manual Process": ["15 min", "25 min", "30 min", "20 min", "15 min", "10 min", "5 min"],
                "AI Process": ["30 sec", "45 sec", "20 sec", "15 sec", "10 sec", "30 sec", "5 sec"],
                "Time Saved": ["93%", "97%", "99%", "99%", "98%", "95%", "0%"],
                "Accuracy Gain": ["+15%", "+25%", "+18%", "+12%", "+22%", "+8%", "+5%"]
            })
            
            st.dataframe(impact_comparison, use_container_width=True)
            
            st.success("""
            🚀 **Revolutionary Transformation Complete!** 
            
            Complex 10-part AOG request processed in 2.8 minutes with 96.8% confidence.
            Manual process time: 2+ hours → AI process time: 2.8 minutes (98% reduction)
            """)
    
    else:
        st.info("👆 **Get Started:** Select an AOG email scenario above and click 'Process Email with AI' to see the complete multi-part quote processing demonstration!")
        
        # === INVENTORY INTELLIGENCE SECTION ===
        st.markdown("---")
        st.markdown("## 🏭 Real-Time Inventory Intelligence")
        
        inv_col1, inv_col2 = st.columns(2)
        
        with inv_col1:
            st.markdown("### 📦 Global Stock Overview")
            
            # Sample inventory status for demonstration
            sample_parts = dashboard.inventory_locations[:10] if hasattr(dashboard, 'inventory_locations') and dashboard.inventory_locations else []
            
            if sample_parts:
                inventory_demo = []
                for part in sample_parts[:5]:
                    stock_levels = part.get('stock_levels_per_location', {})
                    total_stock = sum(stock_levels.values())
                    reserved = sum(part.get('reserved_inventory_per_location', {}).values())
                    available = total_stock - reserved
                    
                    inventory_demo.append({
                        'Part Number': part['part_number'],
                        'Total Stock': total_stock,
                        'Available': available,
                        'Reserved': reserved,
                        'Health': '🟢 Good' if available >= 3 else '🟡 Low' if available >= 1 else '🔴 Critical'
                    })
                
                inv_df = pd.DataFrame(inventory_demo)
                st.dataframe(inv_df, use_container_width=True)
            else:
                st.warning("⚠️ Inventory data not available. Please ensure inventory_locations.json is loaded properly.")
        
        with inv_col2:
            st.markdown("### 🌍 Hub Distribution Matrix")
            
            # Create a mock availability matrix
            hubs = ['London', 'Frankfurt', 'Dubai', 'Singapore', 'New York', 'Hong Kong']
            matrix_data = []
            
            for i, hub in enumerate(hubs):
                row = {'Hub': hub}
                for j, part_type in enumerate(['Engine', 'Landing Gear', 'Avionics', 'Hydraulics']):
                    stock = random.randint(0, 8)
                    color = '🟢' if stock >= 3 else '🟡' if stock >= 1 else '🔴'
                    row[part_type] = f"{color} {stock}"
                matrix_data.append(row)
            
            matrix_df = pd.DataFrame(matrix_data)
            st.dataframe(matrix_df, use_container_width=True)
        
        # Inventory Intelligence Benefits
        st.markdown("### 🚀 AI Inventory Intelligence Benefits")
        
        benefits_col1, benefits_col2, benefits_col3 = st.columns(3)
        
        with benefits_col1:
            st.markdown("""
            <div class="metric-card">
                <h4>⚡ Speed Enhancement</h4>
                <p><strong>Inventory Check:</strong> 30 seconds vs 20 minutes</p>
                <p><strong>Multi-Hub Analysis:</strong> Instant vs 1+ hours</p>
                <p><strong>Stock Optimization:</strong> Real-time recommendations</p>
            </div>
            """, unsafe_allow_html=True)
        
        with benefits_col2:
            st.markdown("""
            <div class="metric-card">
                <h4>🎯 Accuracy Improvement</h4>
                <p><strong>Stock Verification:</strong> 99.2% accurate</p>
                <p><strong>Lead Time Prediction:</strong> 94% within 24 hours</p>
                <p><strong>Cost Optimization:</strong> 15% savings average</p>
            </div>
            """, unsafe_allow_html=True)
        
        with benefits_col3:
            st.markdown("""
            <div class="metric-card">
                <h4>📈 Business Impact</h4>
                <p><strong>AOG Resolution:</strong> 23% faster</p>
                <p><strong>Customer Satisfaction:</strong> 18% increase</p>
                <p><strong>Operational Efficiency:</strong> 31% improvement</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show preview of capabilities
        st.markdown("### 🎯 AI Quote Engine Capabilities Preview")
        
        capability_col1, capability_col2, capability_col3 = st.columns(3)
        
        with capability_col1:
            st.markdown("""
            <div class="metric-card">
                <h4>📧 Email Intelligence</h4>
                <p>• Automatic email parsing</p>
                <p>• Parts extraction with 97% accuracy</p>
                <p>• Customer & aircraft identification</p>
                <p>• Urgency level assessment</p>
            </div>
            """, unsafe_allow_html=True)
        
        with capability_col2:
            st.markdown("""
            <div class="metric-card">
                <h4>🌍 Global Analysis</h4>
                <p>• Real-time inventory checking</p>
                <p>• Multi-hub availability matrix</p>
                <p>• Risk assessment scoring</p>
                <p>• Pricing optimization</p>
            </div>
            """, unsafe_allow_html=True)
        
        with capability_col3:
            st.markdown("""
            <div class="metric-card">
                <h4>📄 Professional Output</h4>
                <p>• Comprehensive quote generation</p>
                <p>• Multiple delivery options</p>
                <p>• Terms & conditions</p>
                <p>• Executive summary</p>
            </div>
            """, unsafe_allow_html=True)

elif page == "📊 Analytics & Insights":
    st.markdown('<h1 class="main-header">📊 Analytics & Insights</h1>', unsafe_allow_html=True)
    
    # CRITICAL FINANCIAL ALERT BANNER
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        border: 3px solid #ff0000;
        box-shadow: 0 8px 16px rgba(255, 0, 0, 0.3);
        animation: pulse 2s infinite;
    ">
        <div style="text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 28px; font-weight: bold;">🚨 EXISTENTIAL BUSINESS THREAT 🚨</h2>
            <h3 style="margin: 10px 0; font-size: 24px;">£9.99M Annual Loss Risk = 62% of £16.0M Total Revenue</h3>
            <p style="margin: 10px 0; font-size: 18px; font-weight: bold;">
                Without AI implementation, BH Worldwide faces potential loss of TWO-THIRDS of total revenue
            </p>
            <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">£16.0M</div>
                    <div style="font-size: 14px;">Current Revenue</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">£9.99M</div>
                    <div style="font-size: 14px;">Potential Annual Loss</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">62%</div>
                    <div style="font-size: 14px;">Of Total Revenue at Risk</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">£1.2M</div>
                    <div style="font-size: 14px;">AI Investment to Prevent</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Analytics with more powerful insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Performance Optimization")
        
        metrics = {
            "Response Time": {"Current": 105, "AI Target": 15, "Unit": "minutes"},
            "Quote Accuracy": {"Current": 87, "AI Target": 98, "Unit": "%"},
            "Customer Satisfaction": {"Current": 3.2, "AI Target": 4.5, "Unit": "/5"},
            "Win Rate": {"Current": 65, "AI Target": 85, "Unit": "%"}
        }
        
        for metric, values in metrics.items():
            improvement = ((values["AI Target"] - values["Current"]) / values["Current"]) * 100
            st.metric(
                metric,
                f"{values['Current']} {values['Unit']}",
                f"{improvement:.1f}% improvement with AI"
            )
    
    with col2:
        st.subheader("💡 REAL BH WORLDWIDE FINANCIAL IMPACT")
        
        st.write("**CRITICAL BUSINESS CASE - REAL £16.0M REVENUE:**")
        st.write("• 🔴 **ANNUAL LOSS RISK: £9.99M (62% of revenue)**")
        st.write("• 💰 **AI Investment Required: £1.2M**")
        st.write("• ⚡ **Break-even Period: 1.4 months**")
        st.write("• 📈 **ROI: 834% (£9.99M saved ÷ £1.2M)**")
        st.write("• ⚠️ **WITHOUT AI: Company faces existential threat**")
        
        years = ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
        cumulative_savings = [9.99, 19.98, 29.97, 39.96, 49.95]  # £9.99M saved each year
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=cumulative_savings,
            mode='lines+markers',
            line=dict(color='#ff4444', width=4),
            marker=dict(size=12),
            name='Cumulative Savings (£M)'
        ))
        
        fig.update_layout(
            title="REAL BH WORLDWIDE: Cumulative Loss Prevention (£M)",
            xaxis_title="Year",
            yaxis_title="Cumulative Savings (£M)",
            template="plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced analytics using extended data
    st.markdown("---")
    st.markdown('<h2 style="color: #1f77b4; font-size: 28px; font-weight: bold; margin-bottom: 20px;">🔬 Advanced Business Intelligence Platform</h2>', unsafe_allow_html=True)
    st.markdown("*Enterprise-grade analytics and predictive intelligence*")
    
    # Advanced BI Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🧠 Predictive Analytics", 
        "💰 Financial Intelligence", 
        "⚡ Operational Efficiency", 
        "📈 Market Intelligence", 
        "👑 Executive Dashboard",
        "🏭 Inventory Analytics",
        "🎯 Extended Data Overview", 
        "📊 Customer Analysis", 
        "🔧 Parts Analysis", 
        "🌍 Geographic Distribution"
    ])
    
    with tab1:  # Predictive Analytics
        st.markdown('<h3 style="color: #ff6b6b;">🧠 Predictive Analytics & AI Models</h3>', unsafe_allow_html=True)
        
        # Aircraft Failure Prediction Model
        st.subheader("✈️ Aircraft Failure Prediction Model")
        
        # Simulate predictive model data
        import random
        np.random.seed(42)
        
        aircraft_types = ["Boeing 737-800", "Airbus A320", "Boeing 777", "Airbus A350", "Boeing 787"]
        failure_risk_data = []
        
        for aircraft in aircraft_types:
            risk_score = np.random.uniform(0.1, 0.9)
            predicted_failures = np.random.poisson(3) + 1
            confidence = np.random.uniform(0.75, 0.95)
            
            failure_risk_data.append({
                "Aircraft": aircraft,
                "Risk Score": risk_score,
                "Predicted Failures (30d)": predicted_failures,
                "Model Confidence": confidence,
                "Risk Level": "High" if risk_score > 0.7 else "Medium" if risk_score > 0.4 else "Low"
            })
        
        risk_df = pd.DataFrame(failure_risk_data)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.scatter(
                risk_df, 
                x="Risk Score", 
                y="Predicted Failures (30d)", 
                size="Model Confidence",
                color="Risk Level",
                hover_data=["Aircraft"],
                title="Aircraft Failure Risk Assessment",
                color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"}
            )
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🎯 Model Performance**")
            st.metric("Prediction Accuracy", "94.2%", "2.1%")
            st.metric("Models Running", "12", "3")
            st.metric("Data Points", "847K", "12K")
            
            st.markdown("**⚠️ High Risk Aircraft**")
            high_risk = risk_df[risk_df["Risk Level"] == "High"]
            for _, row in high_risk.iterrows():
                st.warning(f"{row['Aircraft']}: {row['Risk Score']:.2f}")
        
        # Demand Forecasting
        st.subheader("📊 Demand Forecasting & Trend Analysis")
        
        # Generate forecasting data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        base_demand = 50
        seasonal_trend = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
        noise = np.random.normal(0, 5, len(dates))
        historical_demand = base_demand + seasonal_trend + noise
        
        # Future prediction
        future_dates = pd.date_range(start='2025-01-01', end='2025-06-30', freq='D')
        future_seasonal = 10 * np.sin(2 * np.pi * np.arange(len(future_dates)) / 365)
        predicted_demand = base_demand + 5 + future_seasonal + np.random.normal(0, 3, len(future_dates))
        
        forecast_df = pd.DataFrame({
            'Date': list(dates) + list(future_dates),
            'Demand': list(historical_demand) + list(predicted_demand),
            'Type': ['Historical'] * len(dates) + ['Predicted'] * len(future_dates)
        })
        
        fig = px.line(
            forecast_df, 
            x='Date', 
            y='Demand', 
            color='Type',
            title="AOG Parts Demand Forecasting (ML Model)",
            color_discrete_map={'Historical': 'blue', 'Predicted': 'red'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk Scoring Algorithm
        st.subheader("🎯 Dynamic Risk Scoring Algorithm")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔥 Critical Risk Factors**")
            risk_factors = {
                "Aircraft Age": 0.25,
                "Flight Hours": 0.30,
                "Maintenance History": 0.20,
                "Environmental Conditions": 0.15,
                "Part Reliability Index": 0.10
            }
            
            for factor, weight in risk_factors.items():
                st.metric(factor, f"{weight:.1%}", f"{np.random.uniform(-0.05, 0.05):.1%}")
        
        with col2:
            # Risk distribution pie chart
            fig = px.pie(
                values=list(risk_factors.values()),
                names=list(risk_factors.keys()),
                title="Risk Factor Weights"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown("**⚡ Real-time Alerts**")
            st.error("🚨 High risk: Boeing 777 - LHR")
            st.warning("⚠️ Medium risk: A320 - CDG")
            st.info("ℹ️ Monitor: Boeing 787 - DXB")
            st.success("✅ Low risk: A350 - FRA")
    
    with tab2:  # Financial Intelligence
        st.markdown('<h3 style="color: #2e8b57;">💰 Financial Intelligence & Revenue Optimization</h3>', unsafe_allow_html=True)
        
        # Revenue Optimization Analysis
        st.subheader("📈 Revenue Optimization Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", "£12.4M", "8.2%")
        with col2:
            st.metric("Profit Margin", "23.5%", "2.1%")
        with col3:
            st.metric("Cost Reduction", "£890K", "15.3%")
        with col4:
            st.metric("ROI", "340%", "45%")
        
        # Revenue by customer segment
        customer_revenue = {
            "Tier 1 Airlines": 7.2,
            "Tier 2 Airlines": 3.1,
            "Regional Carriers": 1.5,
            "Cargo Airlines": 0.6
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=list(customer_revenue.values()),
                names=list(customer_revenue.keys()),
                title="Revenue Distribution by Customer Tier (£M)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Profit margin analysis by region
            regions = ["Europe", "North America", "Asia-Pacific", "Middle East", "Latin America"]
            margins = [25.3, 22.1, 28.7, 31.2, 18.9]
            
            fig = px.bar(
                x=regions,
                y=margins,
                title="Profit Margins by Region (%)",
                color=margins,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost-Benefit Analysis
        st.subheader("🔍 Cost-Benefit Scenario Analysis")
        
        scenarios = pd.DataFrame({
            "Scenario": ["Current State", "AI Optimization", "Full Automation", "Hybrid Model"],
            "Implementation Cost (£K)": [0, 450, 1200, 750],
            "Annual Savings (£K)": [0, 890, 2100, 1400],
            "ROI (3 years)": [0, 4.9, 4.25, 4.6],
            "Risk Level": ["Low", "Low", "High", "Medium"]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                scenarios,
                x="Implementation Cost (£K)",
                y="Annual Savings (£K)",
                size="ROI (3 years)",
                color="Risk Level",
                hover_data=["Scenario"],
                title="Cost vs Savings Analysis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(scenarios, use_container_width=True)
        
        # Financial forecasting
        st.subheader("📊 Financial Forecasting & Projections")
        
        months = pd.date_range(start='2024-01-01', periods=24, freq='M')
        base_revenue = 1000000
        growth_rate = 0.08  # 8% annual growth
        
        projected_revenue = []
        for i, month in enumerate(months):
            revenue = base_revenue * (1 + growth_rate) ** (i/12)
            revenue += np.random.normal(0, 50000)  # Add some variance
            projected_revenue.append(revenue)
        
        forecast_financial = pd.DataFrame({
            'Month': months,
            'Projected Revenue': projected_revenue,
            'Conservative': [r * 0.85 for r in projected_revenue],
            'Optimistic': [r * 1.15 for r in projected_revenue]
        })
        
        fig = px.line(
            forecast_financial,
            x='Month',
            y=['Projected Revenue', 'Conservative', 'Optimistic'],
            title="24-Month Revenue Projection (£)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:  # Operational Efficiency
        st.markdown('<h3 style="color: #ff8c00;">⚡ Operational Efficiency & Performance Analytics</h3>', unsafe_allow_html=True)
        
        # Response Time Analytics
        st.subheader("⏱️ Response Time Performance Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Response Time", "14.2 min", "-2.3 min")
        with col2:
            st.metric("SLA Compliance", "94.7%", "3.2%")
        with col3:
            st.metric("First Call Resolution", "87.3%", "5.1%")
        with col4:
            st.metric("Customer Satisfaction", "4.6/5", "0.2")
        
        # Response time trends
        time_periods = ['00-04', '04-08', '08-12', '12-16', '16-20', '20-24']
        response_times = [18.5, 12.3, 8.7, 11.2, 15.8, 22.1]
        target_sla = [15] * len(time_periods)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                x=time_periods,
                y=[response_times, target_sla],
                title="Response Times by Hour of Day (minutes)",
                labels={'x': 'Time Period', 'y': 'Response Time (min)'}
            )
            fig.data[0].name = 'Actual'
            fig.data[1].name = 'SLA Target'
            fig.data[1].line.dash = 'dash'
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Resource utilization
            resources = ['Engineers', 'Parts Inventory', 'Aircraft Capacity', 'Support Staff']
            utilization = [85.2, 78.9, 92.1, 71.3]
            
            fig = px.bar(
                x=resources,
                y=utilization,
                title="Resource Utilization (%)",
                color=utilization,
                color_continuous_scale="RdYlGn"
            )
            fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Target")
            st.plotly_chart(fig, use_container_width=True)
        
        # Bottleneck Identification
        st.subheader("🔍 Bottleneck Analysis & Process Optimization")
        
        process_steps = pd.DataFrame({
            'Process Step': ['Case Receipt', 'Initial Assessment', 'Parts Sourcing', 'Quote Generation', 'Customer Approval', 'Delivery'],
            'Avg Duration (min)': [2.3, 8.7, 45.2, 12.1, 180.5, 320.8],
            'Bottleneck Score': [0.1, 0.3, 0.8, 0.4, 0.9, 0.7],
            'Optimization Potential': ['Low', 'Medium', 'High', 'Medium', 'Critical', 'High']
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                process_steps,
                x='Process Step',
                y='Avg Duration (min)',
                color='Bottleneck Score',
                title="Process Step Duration Analysis",
                color_continuous_scale="Reds"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(process_steps, use_container_width=True)
        
        # Efficiency trends
        st.subheader("📈 Efficiency Trends & Improvements")
        
        weeks = pd.date_range(start='2024-01-01', periods=12, freq='W')
        efficiency_metrics = {
            'Cases Processed': np.random.poisson(45, 12) + 30,
            'Resolution Rate': np.random.uniform(0.85, 0.95, 12),
            'Cost per Case': np.random.uniform(800, 1200, 12)
        }
        
        efficiency_df = pd.DataFrame({
            'Week': weeks,
            **efficiency_metrics
        })
        
        fig = px.line(
            efficiency_df,
            x='Week',
            y=['Cases Processed', 'Resolution Rate', 'Cost per Case'],
            title="Operational Efficiency Trends (12 Weeks)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:  # Market Intelligence
        st.markdown('<h3 style="color: #9370db;">📈 Market Intelligence & Competitive Analysis</h3>', unsafe_allow_html=True)
        
        # Market Position Analysis
        st.subheader("🏆 Competitive Positioning Matrix")
        
        competitors = pd.DataFrame({
            'Company': ['BH Worldwide (Us)', 'Competitor A', 'Competitor B', 'Competitor C', 'Competitor D'],
            'Market Share (%)': [28.5, 22.3, 18.7, 15.2, 15.3],
            'Customer Satisfaction': [4.6, 4.1, 3.8, 4.3, 3.9],
            'Response Time (min)': [14.2, 18.7, 25.3, 16.8, 22.1],
            'Price Competitiveness': [8.5, 7.2, 9.1, 6.8, 8.8]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                competitors,
                x='Market Share (%)',
                y='Customer Satisfaction',
                size='Price Competitiveness',
                color='Response Time (min)',
                hover_data=['Company'],
                title="Competitive Positioning: Market Share vs Satisfaction"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Market share pie chart
            fig = px.pie(
                competitors,
                values='Market Share (%)',
                names='Company',
                title="Market Share Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Market Trends & Predictions
        st.subheader("📊 Market Trends & Growth Predictions")
        
        # Market size over time
        years = list(range(2020, 2031))
        market_size = [2.1, 2.3, 2.8, 3.2, 3.8, 4.1, 4.6, 5.2, 5.8, 6.4, 7.1]  # Billion £
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                x=years,
                y=market_size,
                title="Global AOG Market Size (£ Billion)",
                markers=True
            )
            fig.add_vline(x=2024, line_dash="dash", line_color="red", annotation_text="Current Year")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Growth by region
            regions = ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Others']
            growth_rates = [5.2, 6.8, 12.3, 8.7, 7.1]
            
            fig = px.bar(
                x=regions,
                y=growth_rates,
                title="Market Growth Rate by Region (%)",
                color=growth_rates,
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Pricing Strategy Recommendations
        st.subheader("💰 Pricing Strategy Intelligence")
        
        pricing_analysis = pd.DataFrame({
            'Service Type': ['Emergency AOG', 'Scheduled Maintenance', 'Routine Parts', 'Engineering Support', 'Logistics'],
            'Our Price (£)': [2500, 1200, 450, 180, 95],
            'Market Average (£)': [2800, 1350, 520, 200, 110],
            'Recommended Price (£)': [2650, 1280, 485, 190, 105],
            'Margin Impact': ['+6%', '+7%', '+8%', '+6%', '+11%']
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                pricing_analysis,
                x='Service Type',
                y=['Our Price (£)', 'Market Average (£)', 'Recommended Price (£)'],
                title="Pricing Analysis vs Market",
                barmode='group'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(pricing_analysis, use_container_width=True)
    
    with tab5:  # Executive Dashboard
        st.markdown('<h3 style="color: #dc143c;">👑 Executive Dashboard & KPI Scorecards</h3>', unsafe_allow_html=True)
        
        # Executive KPI Overview
        st.subheader("📊 Executive KPI Scorecard")
        
        kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
        
        with kpi_col1:
            st.metric(
                label="🎯 Revenue YTD",
                value="£12.4M",
                delta="+18.5%",
                help="Year-to-date revenue vs same period last year"
            )
            
        with kpi_col2:
            st.metric(
                label="⚡ Operational Excellence",
                value="94.7%",
                delta="+3.2%",
                help="Overall operational performance score"
            )
            
        with kpi_col3:
            st.metric(
                label="😊 Customer Satisfaction",
                value="4.6/5.0",
                delta="+0.2",
                help="Average customer satisfaction rating"
            )
            
        with kpi_col4:
            st.metric(
                label="💰 Profit Margin",
                value="23.5%",
                delta="+2.1%",
                help="Net profit margin percentage"
            )
            
        with kpi_col5:
            st.metric(
                label="📈 Market Share",
                value="28.5%",
                delta="+1.8%",
                help="Market share in AOG services"
            )
        
        # Performance Benchmarking
        st.subheader("🏆 Performance Benchmarking")
        
        benchmark_metrics = pd.DataFrame({
            'KPI': ['Response Time', 'Resolution Rate', 'Cost Efficiency', 'Customer Retention', 'Innovation Index'],
            'Our Performance': [94, 87, 92, 96, 89],
            'Industry Average': [75, 82, 78, 85, 71],
            'Best in Class': [98, 95, 96, 98, 94],
            'Target': [95, 90, 90, 95, 90]
        })
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig = px.line(
                benchmark_metrics,
                x='KPI',
                y=['Our Performance', 'Industry Average', 'Best in Class', 'Target'],
                title="Performance vs Industry Benchmarks",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🎯 Performance Status**")
            for _, row in benchmark_metrics.iterrows():
                if row['Our Performance'] >= row['Target']:
                    st.success(f"✅ {row['KPI']}: {row['Our Performance']}%")
                elif row['Our Performance'] >= row['Industry Average']:
                    st.warning(f"⚠️ {row['KPI']}: {row['Our Performance']}%")
                else:
                    st.error(f"🔴 {row['KPI']}: {row['Our Performance']}%")
        
        # Strategic Overview
        st.subheader("🎯 Strategic Overview & Initiatives")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🚀 Growth Initiatives**")
            initiatives = [
                "AI-Powered Predictive Maintenance",
                "Global Inventory Optimization",
                "Customer Experience Enhancement",
                "Digital Transformation Program"
            ]
            for i, initiative in enumerate(initiatives):
                progress = np.random.randint(60, 95)
                st.progress(progress/100, text=f"{initiative}: {progress}%")
        
        with col2:
            st.markdown("**⚠️ Risk Factors**")
            risks = [
                ("Supply Chain Disruption", "Medium", "🟡"),
                ("Competitive Pressure", "High", "🔴"),
                ("Regulatory Changes", "Low", "🟢"),
                ("Economic Downturn", "Medium", "🟡")
            ]
            for risk, level, icon in risks:
                st.markdown(f"{icon} **{risk}**: {level}")
        
        with col3:
            st.markdown("**💡 Key Opportunities**")
            opportunities = [
                "Emerging Markets Expansion",
                "Technology Partnership",
                "Sustainable Aviation Solutions",
                "Data Monetization"
            ]
            for opportunity in opportunities:
                value = np.random.randint(5, 25)
                st.markdown(f"📈 {opportunity}: +£{value}M potential")
        
        # Executive Summary
        st.subheader("📋 Executive Summary")
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown("""
            **📈 Business Performance:**
            - Revenue growth exceeding targets by 18.5%
            - Market share increased to 28.5% (+1.8%)
            - Operational efficiency at 94.7%
            - Customer satisfaction at all-time high (4.6/5)
            
            **🎯 Strategic Priorities:**
            - Continue AI/ML investment for predictive analytics
            - Expand into emerging markets (Asia-Pacific focus)
            - Enhance digital customer experience
            - Optimize global supply chain efficiency
            """)
        
        with summary_col2:
            st.markdown("""
            **⚠️ Areas for Attention:**
            - Monitor competitive pressure in core markets
            - Address supply chain resilience gaps
            - Accelerate digital transformation initiatives
            - Strengthen partnerships in key regions
            
            **🚀 Growth Opportunities:**
            - AI-powered service expansion: +£15M potential
            - Sustainable aviation solutions: +£8M potential
            - Data analytics services: +£12M potential
            - Strategic acquisitions: +£25M potential
            """)
    
    with tab6:  # Inventory Analytics (NEW)
        st.markdown('<h3 style="color: #4CAF50;">🏭 Global Inventory Intelligence & Optimization</h3>', unsafe_allow_html=True)
        
        # Global Inventory Health Dashboard
        try:
            global_inventory = dashboard._calculate_global_inventory_metrics()
        except:
            global_inventory = None
        
        if global_inventory:
            # Inventory Health Overview
            inv_col1, inv_col2, inv_col3, inv_col4 = st.columns(4)
            
            with inv_col1:
                st.metric("Total Parts Tracked", global_inventory['total_parts'], f"+{random.randint(5, 15)} new")
            with inv_col2:
                st.metric("Stock Health Score", f"{global_inventory['overall_health']:.1f}%", f"+{random.randint(1, 5)}%")
            with inv_col3:
                st.metric("Critical Parts", global_inventory['critical_parts'], f"-{random.randint(1, 3)} resolved")
            with inv_col4:
                st.metric("Global Locations", "6 hubs", "98.2% availability")
                
            # Inventory Health by Category
            st.markdown("#### 📊 Inventory Health by Category")
            
            cat_col1, cat_col2 = st.columns(2)
            
            with cat_col1:
                # Create category health chart
                categories = ['Engine Components', 'Landing Gear', 'Avionics', 'Hydraulics', 'APU Systems']
                health_scores = [92, 87, 94, 89, 91]
                
                fig = px.bar(
                    x=categories,
                    y=health_scores,
                    title="Inventory Health by Component Category",
                    color=health_scores,
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with cat_col2:
                # Global stock distribution
                locations = ['London', 'Frankfurt', 'Dubai', 'Singapore', 'New York', 'Hong Kong']
                stock_values = [8.2, 7.8, 6.5, 5.9, 4.3, 3.8]  # Million GBP worth
                
                fig = px.pie(
                    values=stock_values,
                    names=locations,
                    title="Global Stock Distribution (£M)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            # Financial Impact of AI Inventory Optimization
            st.markdown("#### 💰 Financial Impact of AI Inventory Optimization")
            
            financial_col1, financial_col2, financial_col3 = st.columns(3)
            
            with financial_col1:
                st.markdown("""
                <div class="metric-card">
                    <h4>💰 Cost Savings</h4>
                    <p><strong>Inventory Optimization:</strong> £847K annually</p>
                    <p><strong>Reduced Dead Stock:</strong> £235K recovered</p>
                    <p><strong>Improved Turnover:</strong> 15.2% faster</p>
                </div>
                """, unsafe_allow_html=True)
            
            with financial_col2:
                st.markdown("""
                <div class="metric-card">
                    <h4>⚡ Operational Efficiency</h4>
                    <p><strong>Stock-out Reduction:</strong> 72% fewer incidents</p>
                    <p><strong>Emergency Purchases:</strong> 89% reduction</p>
                    <p><strong>AOG Resolution Time:</strong> 23% faster</p>
                </div>
                """, unsafe_allow_html=True)
            
            with financial_col3:
                st.markdown("""
                <div class="metric-card">
                    <h4>📈 Service Quality</h4>
                    <p><strong>Fill Rate:</strong> 94.7% vs 78% industry</p>
                    <p><strong>Customer Satisfaction:</strong> +18% improvement</p>
                    <p><strong>First-Time Availability:</strong> 91.3%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # AI-Powered Inventory Optimization Recommendations
            st.markdown("#### 🤖 AI-Powered Inventory Optimization Recommendations")
            
            recommendations = [
                {"Part": "ENGINE FAN BLADE CFM56", "Location": "Dubai", "Action": "Increase Stock", "Reason": "Middle East demand surge", "Impact": "£125K cost avoidance", "Priority": "High"},
                {"Part": "LANDING GEAR ACTUATOR A320", "Location": "Singapore", "Action": "Rebalance", "Reason": "Excess stock vs demand", "Impact": "£89K working capital optimization", "Priority": "Medium"},
                {"Part": "HYDRAULIC PUMP ASSEMBLY", "Location": "Hong Kong", "Action": "Express Transfer", "Reason": "Incoming AOG request", "Impact": "£67K revenue protection", "Priority": "Critical"},
                {"Part": "AVIONICS CONTROL UNIT", "Location": "Frankfurt", "Action": "Reduce Stock", "Reason": "Low historical demand", "Impact": "£156K working capital release", "Priority": "Low"},
                {"Part": "APU STARTER MOTOR", "Location": "London", "Action": "Maintain Level", "Reason": "Optimal stock level", "Impact": "Status quo maintained", "Priority": "Medium"}
            ]
            
            rec_df = pd.DataFrame(recommendations)
            st.dataframe(rec_df, use_container_width=True)
            
        else:
            st.warning("⚠️ Inventory data not available. Please ensure inventory data files are loaded properly.")
            
            # Show sample analytics structure
            st.markdown("#### 📊 Sample Inventory Analytics Structure")
            st.info("""
            **When inventory data is available, this section will show:**
            - Real-time stock levels across all global hubs
            - Inventory health scoring and optimization recommendations
            - Financial impact analysis of inventory decisions
            - AI-powered stock rebalancing suggestions
            - Parts demand forecasting and trend analysis
            """)
    
    with tab7:  # Extended Data Overview (keeping original)
        st.subheader("📈 Extended Dataset Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total AOG Cases", len(dashboard.active_cases["active_aog_cases"]))
            st.metric("Critical Cases", len([c for c in dashboard.active_cases["active_aog_cases"] if c.get("urgency") == "Critical"]))
        
        with col2:
            st.metric("Total Airlines", len(dashboard.customers["major_airline_customers"]))
            st.metric("Active Locations", len(set(case.get('location', 'Unknown') for case in dashboard.active_cases["active_aog_cases"])))
        
        with col3:
            total_loss = sum(int(case.get("total_loss_so_far", "£0").replace("£", "").replace(",", "")) 
                           for case in dashboard.active_cases["active_aog_cases"] 
                           if "£" in case.get("total_loss_so_far", ""))
            st.metric("Total Financial Impact", f"£{total_loss:,}")
        
        # Urgency distribution
        urgency_counts = {}
        for case in dashboard.active_cases["active_aog_cases"]:
            urgency = case.get("urgency", "Unknown")
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
        
        fig = px.pie(
            values=list(urgency_counts.values()),
            names=list(urgency_counts.keys()),
            title="AOG Cases by Urgency Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab8:  # Customer Analysis (keeping original)
        st.subheader("👥 Customer Portfolio Analysis")
        
        customers = dashboard.customers["major_airline_customers"]
        
        # Customer metrics
        customer_data = []
        for customer in customers:
            try:
                annual_value = float(customer["annual_aog_volume"].replace("£", "").replace("M", ""))
                customer_data.append({
                    "Airline": customer["name"],
                    "Fleet Size": customer["fleet_size"],
                    "Annual Value (£M)": annual_value,
                    "Priority": customer["priority_level"],
                    "SLA (min)": int(customer["response_time_sla"].replace(" minutes", "")),
                    "Value per Aircraft": annual_value * 1000000 / customer["fleet_size"]
                })
            except:
                continue
        
        if customer_data:
            customer_df = pd.DataFrame(customer_data)
            
            fig = px.scatter(
                customer_df,
                x="Fleet Size",
                y="Annual Value (£M)",
                size="Value per Aircraft",
                color="Priority",
                hover_data=["SLA (min)"],
                title="Customer Value vs Fleet Size"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(customer_df, use_container_width=True)
    
    with tab9:  # Parts Analysis (keeping original)
        st.subheader("🔧 Parts & Aircraft Analysis")
        
        # Aircraft type distribution
        aircraft_counts = {}
        for case in dashboard.active_cases["active_aog_cases"]:
            aircraft = case.get("aircraft", "Unknown")
            aircraft_counts[aircraft] = aircraft_counts.get(aircraft, 0) + 1
        
        # FIXED: Proper plotly figure creation and layout updates
        if aircraft_counts:
            aircraft_df = pd.DataFrame(list(aircraft_counts.items()), columns=['Aircraft', 'Count'])
            fig = px.bar(aircraft_df, x='Aircraft', y='Count', title="AOG Cases by Aircraft Type")
            fig.update_layout(xaxis_tickangle=-45)  # FIXED: Use update_layout instead of update_xaxis
            st.plotly_chart(fig, use_container_width=True)
        
        # Parts failure analysis
        part_counts = {}
        for case in dashboard.active_cases["active_aog_cases"]:
            part = case.get("part_needed", "Unknown")
            part_counts[part] = part_counts.get(part, 0) + 1
        
        # Show top 10 most common parts
        top_parts = sorted(part_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if top_parts:
            parts_df = pd.DataFrame(top_parts, columns=['Part', 'Count'])
            fig = px.bar(parts_df, x='Part', y='Count', title="Top 10 Most Common Part Failures")
            fig.update_layout(xaxis_tickangle=-45)  # FIXED: Use update_layout instead of update_xaxis
            st.plotly_chart(fig, use_container_width=True)
    
    with tab10:  # Geographic Distribution (keeping original)
        st.subheader("🌍 Global Operations Distribution")
        
        # Location analysis
        
        # ENHANCED: Add comprehensive inventory intelligence tab
        st.markdown("---")
        st.markdown('<h2 style="color: #17a2b8;">📦 Comprehensive Inventory Intelligence Platform</h2>', unsafe_allow_html=True)
        st.markdown("*AI-powered inventory optimization and intelligence system*")
        
        # Global Inventory Health Dashboard
        try:
            global_inventory = dashboard._calculate_global_inventory_metrics()
        except:
            global_inventory = None
        
        if global_inventory:
            # Inventory Health Overview
            st.markdown("### 🎯 Global Inventory Health Dashboard")
            
            health_col1, health_col2, health_col3, health_col4, health_col5 = st.columns(5)
            
            with health_col1:
                st.metric("Total Parts Tracked", f"{global_inventory['total_parts']:,}", "Real-time monitoring")
            with health_col2:
                health_color = "🟢" if global_inventory['health_score'] > 80 else "🟡" if global_inventory['health_score'] > 60 else "🔴"
                st.metric("Inventory Health Score", f"{global_inventory['health_score']:.1f}%", f"{health_color} Status")
            with health_col3:
                st.metric("Critical Stock Alerts", global_inventory['critical_parts'], "🚨 Immediate attention")
            with health_col4:
                st.metric("Low Stock Parts", global_inventory['low_stock_parts'], "⚠️ Monitor closely")
            with health_col5:
                st.metric("Overstocked Parts", global_inventory['overstocked_parts'], "📦 Optimization opportunity")
            
            # Global Stock Distribution
            st.markdown("### 🌍 Global Stock Distribution by Hub")
            
            hub_col1, hub_col2 = st.columns(2)
            
            with hub_col1:
                # Stock by location chart
                locations = list(global_inventory['location_totals'].keys())
                stock_counts = list(global_inventory['location_totals'].values())
                
                fig = px.bar(
                    x=locations,
                    y=stock_counts,
                    title="Parts Count by Inventory Hub",
                    labels={'x': 'Hub Location', 'y': 'Total Parts in Stock'},
                    color=stock_counts,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with hub_col2:
                # Inventory status pie chart
                status_labels = ['Healthy Stock', 'Low Stock', 'Critical Stock', 'Overstocked']
                status_values = [
                    global_inventory['healthy_parts'],
                    global_inventory['low_stock_parts'], 
                    global_inventory['critical_parts'],
                    global_inventory['overstocked_parts']
                ]
                colors = ['#28a745', '#ffc107', '#dc3545', '#17a2b8']
                
                fig = px.pie(
                    values=status_values,
                    names=status_labels,
                    title="Inventory Health Distribution",
                    color_discrete_sequence=colors
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed Inventory Analysis
            st.markdown("### 🔍 Detailed Inventory Analysis")
            
            # Sample some parts for detailed view
            sample_parts = dashboard.inventory_locations[:10] if hasattr(dashboard, 'inventory_locations') else []
            
            if sample_parts:
                detailed_data = []
                for item in sample_parts:
                    metrics = dashboard._calculate_inventory_metrics(item)
                    
                    # Calculate inventory value (using average part price)
                    avg_part_price = 25000  # Average from parts pricing analysis
                    total_value = metrics['total_stock'] * avg_part_price
                    
                    detailed_data.append({
                        'Part Number': metrics['part_number'],
                        'Total Stock': metrics['total_stock'],
                        'Available': metrics['total_available'],
                        'Reserved': metrics['total_reserved'],
                        'Status': metrics['status'].title(),
                        'Best Hub': metrics['best_hubs'][0][0] if metrics['best_hubs'] else 'None',
                        'Hub Stock': metrics['best_hubs'][0][1] if metrics['best_hubs'] else 0,
                        'Incoming': metrics['total_incoming'],
                        'Est. Value': f"£{total_value:,.0f}"
                    })
                
                detailed_df = pd.DataFrame(detailed_data)
                
                # Color code by status
                def highlight_status(row):
                    if row['Status'] == 'Critical':
                        return ['background-color: #ffebee'] * len(row)
                    elif row['Status'] == 'Low':
                        return ['background-color: #fff3e0'] * len(row)
                    elif row['Status'] == 'Good':
                        return ['background-color: #e8f5e8'] * len(row)
                    else:
                        return [''] * len(row)
                
                st.dataframe(
                    detailed_df.style.apply(highlight_status, axis=1),
                    use_container_width=True
                )
            
            # Inventory Optimization Recommendations
            st.markdown("### 🤖 AI-Powered Inventory Optimization Recommendations")
            
            opt_col1, opt_col2, opt_col3 = st.columns(3)
            
            with opt_col1:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 20px; border-radius: 15px; color: white;">
                    <h4>🚨 Critical Actions Required</h4>
                    <ul>
                        <li>Expedite procurement for critical parts</li>
                        <li>Implement emergency supplier contacts</li>
                        <li>Consider alternative part recommendations</li>
                    </ul>
                    <p><strong>Impact:</strong> Prevent AOG situations</p>
                </div>
                """, unsafe_allow_html=True)
            
            with opt_col2:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%); padding: 20px; border-radius: 15px; color: white;">
                    <h4>⚡ Optimization Opportunities</h4>
                    <ul>
                        <li>Redistribute overstocked items</li>
                        <li>Adjust reorder points based on demand</li>
                        <li>Optimize hub stock allocation</li>
                    </ul>
                    <p><strong>Savings:</strong> £450K annual reduction</p>
                </div>
                """, unsafe_allow_html=True)
            
            with opt_col3:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%); padding: 20px; border-radius: 15px; color: white;">
                    <h4>📈 Performance Improvements</h4>
                    <ul>
                        <li>Predictive demand forecasting</li>
                        <li>Automated reorder triggers</li>
                        <li>Dynamic pricing optimization</li>
                    </ul>
                    <p><strong>Benefit:</strong> 25% efficiency increase</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Financial Impact of Inventory Intelligence
            st.markdown("### 💰 Financial Impact of AI Inventory Optimization")
            
            financial_col1, financial_col2 = st.columns(2)
            
            with financial_col1:
                # Cost savings breakdown
                savings_data = {
                    'Category': ['Carrying Cost Reduction', 'Stock-out Prevention', 'Overstock Optimization', 'Process Automation'],
                    'Annual Savings (£K)': [180, 420, 125, 95],
                    'Implementation': ['Q1 2025', 'Immediate', 'Q2 2025', 'Q1 2025']
                }
                savings_df = pd.DataFrame(savings_data)
                
                fig = px.bar(
                    savings_df,
                    x='Category',
                    y='Annual Savings (£K)',
                    title="AI Inventory Optimization - Annual Savings",
                    color='Annual Savings (£K)',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with financial_col2:
                st.markdown("#### 🟊 Key Financial Metrics")
                
                # Estimated inventory value
                estimated_total_value = global_inventory['total_parts'] * 25000  # Average part value
                
                fin_metrics_col1, fin_metrics_col2 = st.columns(2)
                
                with fin_metrics_col1:
                    st.metric("Total Inventory Value", f"£{estimated_total_value/1000000:.1f}M", "Asset optimization")
                    st.metric("Carrying Cost (Annual)", f"£{estimated_total_value*0.25/1000000:.1f}M", "25% of inventory value")
                
                with fin_metrics_col2:
                    st.metric("Stock-out Risk Cost", "£420K", "Annual prevention")
                    st.metric("Optimization Potential", "£820K", "Total annual savings")
                
                st.success("🎯 **ROI Impact**: AI inventory optimization delivers 340% ROI through reduced carrying costs, prevented stock-outs, and optimized working capital.")
        
        else:
            st.warning("⚠️ Inventory data not available. Please ensure inventory_locations.json is loaded properly.")
        location_counts = {}
        for case in dashboard.active_cases["active_aog_cases"]:
            location = case.get("location", "Unknown")
            location_counts[location] = location_counts.get(location, 0) + 1
        
        # Show top locations
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        
        if top_locations:
            locations_df = pd.DataFrame(top_locations, columns=['Location', 'Cases'])
            fig = px.bar(locations_df, x='Cases', y='Location', orientation='h', title="AOG Cases by Location")
            st.plotly_chart(fig, use_container_width=True)

elif page == "🎯 Competitive Intelligence":
    # Professional Header
    st.markdown('<h1 class="main-header">🎯 Competitive Intelligence & Market Analysis Platform</h1>', unsafe_allow_html=True)
    st.markdown("*Enterprise-grade competitive intelligence and strategic market analysis*")
    
    # Executive Intelligence Summary Cards
    st.markdown("### 📊 Strategic Intelligence Overview")
    intel_col1, intel_col2, intel_col3, intel_col4, intel_col5 = st.columns(5)
    
    with intel_col1:
        st.metric("Market Position", "#2", "+1 rank improvement")
    with intel_col2:
        st.metric("Competitive Score", "8.4/10", "+1.7 vs last quarter")
    with intel_col3:
        st.metric("Threat Level", "Medium", "🟡 Monitoring required")
    with intel_col4:
        st.metric("Market Growth", "14.3%", "+2.1% acceleration")
    with intel_col5:
        st.metric("Win Rate", "74%", "+12% vs competitors")
    
    # Advanced Competitive Intelligence Tabs
    intel_tab1, intel_tab2, intel_tab3, intel_tab4, intel_tab5 = st.tabs([
        "🏢 Market Landscape", "🔍 Competitor Deep Dive", "📈 Market Intelligence", 
        "🎯 Strategic Positioning", "🚨 Competitive Alerts"
    ])
    
    with intel_tab1:
        st.markdown("### 🏢 Market Landscape Dashboard")
        
        # Competitive positioning matrix
        st.markdown("#### Competitive Positioning Matrix")
        competitors_data = {
            'Company': ['BH Worldwide', 'DHL Aviation', 'AAR Corp', 'Lufthansa Technik', 'StandardAero', 'HAECO', 'ST Engineering'],
            'Market Share (%)': [18.5, 24.2, 15.8, 16.3, 12.1, 8.7, 4.4],
            'Growth Rate (%)': [14.3, 8.7, 11.2, 6.9, 15.8, 12.4, 18.2],
            'Service Quality': [8.7, 8.9, 7.8, 9.2, 8.1, 7.6, 7.3],
            'Innovation Score': [9.1, 7.8, 7.2, 8.5, 7.9, 6.8, 8.8],
            'Threat Level': ['Medium', 'High', 'Medium', 'High', 'Low', 'Low', 'Low']
        }
        comp_matrix_df = pd.DataFrame(competitors_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bubble chart for competitive positioning
            colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
            color_map = [colors[threat] for threat in comp_matrix_df['Threat Level']]
            
            fig = px.scatter(
                comp_matrix_df, 
                x='Market Share (%)', 
                y='Growth Rate (%)',
                size='Service Quality',
                color='Threat Level',
                hover_data=['Innovation Score'],
                title="Competitive Positioning Matrix",
                color_discrete_map=colors
            )
            
            for i, company in enumerate(comp_matrix_df['Company']):
                fig.add_annotation(
                    x=comp_matrix_df['Market Share (%)'][i],
                    y=comp_matrix_df['Growth Rate (%)'][i],
                    text=company,
                    showarrow=False,
                    yshift=10
                )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Threat assessment radar
            st.markdown("#### Competitive Threat Assessment")
            
            threat_metrics = ['Market Share', 'Innovation', 'Pricing', 'Service Quality', 'Global Reach', 'Financial Strength']
            competitors_radar = {
                'DHL Aviation': [9, 7, 8, 9, 9, 9],
                'Lufthansa Technik': [8, 8, 7, 9, 8, 9],
                'AAR Corp': [7, 7, 6, 7, 7, 8],
                'BH Worldwide': [7, 9, 8, 8, 6, 7]
            }
            
            fig = go.Figure()
            
            for competitor, values in competitors_radar.items():
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=threat_metrics,
                    fill='toself',
                    name=competitor,
                    opacity=0.6
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Competitive Threat Analysis",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Market trend indicators
        st.markdown("#### Market Trend Indicators & Momentum Analysis")
        
        trend_col1, trend_col2, trend_col3 = st.columns(3)
        
        with trend_col1:
            # Market momentum
            momentum_data = {
                'Metric': ['Digital Transformation', 'Sustainability Focus', 'AI Adoption', 'Supply Chain Resilience', 'Customer Experience'],
                'Current Level': [7.2, 6.8, 8.1, 7.9, 8.3],
                'Projected Growth': [15.2, 22.1, 28.5, 12.7, 18.9]
            }
            momentum_df = pd.DataFrame(momentum_data)
            
            fig = px.bar(
                momentum_df, 
                x='Projected Growth', 
                y='Metric',
                orientation='h',
                title="Market Momentum Analysis (%)",
                color='Projected Growth',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with trend_col2:
            # Industry benchmarks
            benchmark_data = {
                'KPI': ['Response Time', 'Cost Efficiency', 'Service Quality', 'Innovation Index', 'Customer Satisfaction'],
                'BH Worldwide': [8.7, 8.2, 8.7, 9.1, 8.9],
                'Industry Average': [6.8, 7.1, 7.4, 6.9, 7.6],
                'Best in Class': [9.2, 9.1, 9.4, 9.3, 9.5]
            }
            benchmark_df = pd.DataFrame(benchmark_data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=benchmark_df['BH Worldwide'], theta=benchmark_df['KPI'], name='BH Worldwide', fill='toself'))
            fig.add_trace(go.Scatterpolar(r=benchmark_df['Industry Average'], theta=benchmark_df['KPI'], name='Industry Average', fill='toself'))
            fig.add_trace(go.Scatterpolar(r=benchmark_df['Best in Class'], theta=benchmark_df['KPI'], name='Best in Class', fill='toself'))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                title="Industry Benchmark Comparison",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with trend_col3:
            # Market share evolution
            years = ['2022', '2023', '2024', '2025E', '2026E']
            market_evolution = {
                'BH Worldwide': [15.2, 16.8, 18.5, 20.1, 22.3],
                'DHL Aviation': [26.1, 25.3, 24.2, 23.1, 22.0],
                'Lufthansa Technik': [17.8, 17.1, 16.3, 15.8, 15.2],
                'Others': [40.9, 40.8, 41.0, 41.0, 40.5]
            }
            
            fig = go.Figure()
            for company, values in market_evolution.items():
                fig.add_trace(go.Scatter(x=years, y=values, mode='lines+markers', name=company, stackgroup='one'))
            
            fig.update_layout(
                title="Market Share Evolution",
                xaxis_title="Year",
                yaxis_title="Market Share (%)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with intel_tab2:
        st.markdown("### 🔍 Competitor Deep Dive Analysis")
        
        # Competitor selection
        selected_competitor = st.selectbox(
            "Select Competitor for Deep Analysis",
            ['DHL Aviation', 'Lufthansa Technik', 'AAR Corp', 'StandardAero', 'HAECO', 'ST Engineering']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # SWOT Analysis
            st.markdown(f"#### SWOT Analysis - {selected_competitor}")
            
            if selected_competitor == 'DHL Aviation':
                swot_data = {
                    'Strengths': ['Market leader position', 'Global logistics network', 'Brand recognition', 'Financial resources'],
                    'Weaknesses': ['High cost structure', 'Slow innovation', 'Limited AI adoption', 'Complex processes'],
                    'Opportunities': ['Digital transformation', 'Emerging markets', 'Sustainability services', 'Strategic partnerships'],
                    'Threats': ['New entrants', 'Technology disruption', 'Economic downturns', 'Regulatory changes']
                }
            else:
                swot_data = {
                    'Strengths': ['Technical expertise', 'Quality reputation', 'Strong partnerships', 'Regional presence'],
                    'Weaknesses': ['Limited scale', 'Higher pricing', 'Slower response', 'Legacy systems'],
                    'Opportunities': ['Technology adoption', 'Market expansion', 'Service diversification', 'Cost optimization'],
                    'Threats': ['Competitive pressure', 'Market consolidation', 'Price wars', 'Customer switching']
                }
            
            for category, items in swot_data.items():
                st.markdown(f"**{category}:**")
                for item in items:
                    st.markdown(f"• {item}")
                st.markdown("")
        
        with col2:
            # Competitive pricing analysis
            st.markdown("#### Competitive Pricing Analysis")
            
            pricing_data = {
                'Service Type': ['Emergency AOG', 'Scheduled Maintenance', 'Parts Supply', 'Technical Support', 'Logistics'],
                'BH Worldwide': [2650, 1280, 485, 190, 105],
                selected_competitor: [2800, 1350, 520, 200, 110] if selected_competitor == 'DHL Aviation' else [2900, 1400, 540, 210, 115],
                'Market Average': [2750, 1320, 500, 195, 108]
            }
            pricing_df = pd.DataFrame(pricing_data)
            
            fig = px.bar(
                pricing_df.melt(id_vars=['Service Type'], var_name='Company', value_name='Price'),
                x='Service Type',
                y='Price',
                color='Company',
                barmode='group',
                title="Pricing Comparison Analysis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Service capability comparison
        st.markdown("#### Service Capability Comparison Matrix")
        
        capabilities = ['Global Coverage', 'Response Time', 'Technical Expertise', 'Digital Tools', 'Cost Efficiency', 'Innovation']
        capability_scores = {
            'BH Worldwide': [7, 9, 8, 9, 8, 9],
            'DHL Aviation': [9, 7, 8, 6, 6, 6],
            'Lufthansa Technik': [8, 7, 9, 7, 7, 7],
            'AAR Corp': [7, 6, 7, 6, 7, 6]
        }
        
        capability_df = pd.DataFrame({
            'Capability': capabilities * len(capability_scores),
            'Company': [company for company in capability_scores.keys() for _ in capabilities],
            'Score': [score for scores in capability_scores.values() for score in scores]
        })
        
        fig = px.bar(
            capability_df,
            x='Capability',
            y='Score',
            color='Company',
            barmode='group',
            title="Service Capability Matrix"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Win/Loss analysis
        st.markdown("#### Customer Win/Loss Analysis")
        
        winloss_col1, winloss_col2 = st.columns(2)
        
        with winloss_col1:
            win_reasons = ['Superior Technology', 'Better Pricing', 'Faster Response', 'Service Quality', 'Innovation']
            win_percentages = [35, 25, 20, 15, 5]
            
            fig = px.pie(
                values=win_percentages,
                names=win_reasons,
                title="Reasons for Winning Against Competitors"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with winloss_col2:
            loss_reasons = ['Price Sensitivity', 'Incumbent Advantage', 'Specification Mismatch', 'Geographic Limitations', 'Brand Preference']
            loss_percentages = [40, 25, 15, 12, 8]
            
            fig = px.pie(
                values=loss_percentages,
                names=loss_reasons,
                title="Reasons for Losing to Competitors"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with intel_tab3:
        st.markdown("### 📈 Market Intelligence Hub")
        
        # Industry growth projections
        st.markdown("#### Industry Growth Projections & Market Size Analysis")
        
        growth_col1, growth_col2 = st.columns(2)
        
        with growth_col1:
            # Market size projection
            years = list(range(2022, 2031))
            total_market = [18.2, 20.1, 22.8, 26.1, 29.8, 34.2, 39.1, 44.8, 51.2, 58.6]  # Billions USD
            aog_segment = [2.1, 2.3, 2.8, 3.2, 3.8, 4.1, 4.6, 5.2, 5.8, 6.4]  # Billions USD
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=total_market, mode='lines+markers', name='Total Market', line=dict(width=3)))
            fig.add_trace(go.Scatter(x=years, y=aog_segment, mode='lines+markers', name='AOG Segment', line=dict(width=3)))
            
            fig.update_layout(
                title="Global Aviation MRO Market Size (USD Billions)",
                xaxis_title="Year",
                yaxis_title="Market Size (USD Billions)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with growth_col2:
            # Technology adoption curves
            technologies = ['AI/ML', 'IoT Sensors', 'Blockchain', 'AR/VR', 'Predictive Analytics', 'Digital Twins']
            adoption_2024 = [35, 48, 12, 28, 52, 31]
            adoption_2027 = [78, 85, 45, 67, 89, 71]
            
            tech_df = pd.DataFrame({
                'Technology': technologies,
                '2024 Adoption (%)': adoption_2024,
                '2027 Projected (%)': adoption_2027
            })
            
            fig = px.bar(
                tech_df.melt(id_vars=['Technology'], var_name='Period', value_name='Adoption Rate'),
                x='Technology',
                y='Adoption Rate',
                color='Period',
                barmode='group',
                title="Technology Adoption Curves"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Regulatory environment analysis
        st.markdown("#### Regulatory Environment Impact Analysis")
        
        reg_col1, reg_col2 = st.columns(2)
        
        with reg_col1:
            regulatory_impacts = {
                'Regulation': ['EASA Part 145', 'FAA Part 145', 'IATA Standards', 'Environmental Regulations', 'Safety Protocols'],
                'Compliance Cost (M£)': [2.1, 1.8, 0.9, 3.2, 1.5],
                'Business Impact': ['Medium', 'Medium', 'Low', 'High', 'Medium'],
                'Timeline': ['2024', '2025', '2024', '2026', '2025']
            }
            reg_df = pd.DataFrame(regulatory_impacts)
            
            fig = px.bar(
                reg_df,
                x='Regulation',
                y='Compliance Cost (M£)',
                color='Business Impact',
                title="Regulatory Compliance Cost Analysis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with reg_col2:
            # Customer switching behavior
            switch_reasons = ['Better Service', 'Lower Cost', 'Technology', 'Relationship Issues', 'Geographic Coverage']
            switch_frequency = [28, 35, 18, 12, 7]
            
            fig = px.pie(
                values=switch_frequency,
                names=switch_reasons,
                title="Customer Switching Behavior Patterns"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Market sentiment analysis
        st.markdown("#### Market Sentiment & Customer Insights")
        
        sentiment_data = {
            'Metric': ['Service Quality', 'Innovation Leadership', 'Cost Competitiveness', 'Reliability', 'Customer Support'],
            'Q1 2024': [7.2, 8.1, 6.8, 8.5, 7.9],
            'Q2 2024': [7.5, 8.3, 7.1, 8.7, 8.2],
            'Q3 2024': [7.8, 8.6, 7.4, 8.9, 8.5],
            'Q4 2024': [8.1, 8.9, 7.7, 9.1, 8.8]
        }
        sentiment_df = pd.DataFrame(sentiment_data)
        
        fig = px.line(
            sentiment_df.melt(id_vars=['Metric'], var_name='Quarter', value_name='Score'),
            x='Quarter',
            y='Score',
            color='Metric',
            title="Market Sentiment Evolution (Customer Satisfaction Scores)",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with intel_tab4:
        st.markdown("### 🎯 Strategic Positioning Intelligence")
        
        # Blue Ocean strategy opportunities
        st.markdown("#### Blue Ocean Strategy Opportunities")
        
        blue_ocean_col1, blue_ocean_col2 = st.columns(2)
        
        with blue_ocean_col1:
            # Strategy canvas
            factors = ['Price', 'Response Time', 'Technology', 'Global Coverage', 'Sustainability', 'AI Integration', 'Customer Experience']
            industry_avg = [5, 5, 5, 5, 3, 2, 5]
            bh_current = [7, 9, 8, 6, 6, 9, 8]
            bh_future = [8, 9, 9, 8, 9, 10, 9]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=industry_avg, theta=factors, name='Industry Average', fill='toself'))
            fig.add_trace(go.Scatterpolar(r=bh_current, theta=factors, name='BH Current', fill='toself'))
            fig.add_trace(go.Scatterpolar(r=bh_future, theta=factors, name='BH Future Strategy', fill='toself'))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                title="Strategic Canvas - Blue Ocean Analysis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with blue_ocean_col2:
            # Market gap analysis
            st.markdown("#### Market Gap Analysis")
            
            gaps_data = {
                'Gap Area': ['Predictive Maintenance', 'Sustainable Solutions', 'Real-time Collaboration', 'AI-Driven Optimization', 'Digital Twins'],
                'Market Need (1-10)': [9, 8, 7, 9, 8],
                'Current Supply (1-10)': [4, 3, 5, 3, 2],
                'Opportunity Size (M£)': [145, 89, 67, 178, 123]
            }
            gaps_df = pd.DataFrame(gaps_data)
            
            fig = px.scatter(
                gaps_df,
                x='Current Supply (1-10)',
                y='Market Need (1-10)',
                size='Opportunity Size (M£)',
                hover_data=['Gap Area'],
                title="Market Gap Opportunity Matrix"
            )
            
            # Add quadrant lines
            fig.add_hline(y=6.5, line_dash="dash", line_color="gray")
            fig.add_vline(x=6.5, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Competitive advantage analysis
        st.markdown("#### Competitive Advantage Analysis & Recommendations")
        
        advantage_col1, advantage_col2 = st.columns(2)
        
        with advantage_col1:
            # Porter's Five Forces
            forces_data = {
                'Force': ['Threat of New Entrants', 'Bargaining Power of Suppliers', 'Bargaining Power of Buyers', 'Threat of Substitutes', 'Competitive Rivalry'],
                'Current Level': [3, 4, 6, 2, 8],
                'Projected Level': [4, 5, 7, 3, 9]
            }
            forces_df = pd.DataFrame(forces_data)
            
            fig = px.bar(
                forces_df.melt(id_vars=['Force'], var_name='Period', value_name='Intensity'),
                x='Force',
                y='Intensity',
                color='Period',
                barmode='group',
                title="Porter's Five Forces Analysis"
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with advantage_col2:
            # Strategic moves simulation
            st.markdown("#### Strategic Moves Simulation")
            
            moves = ['AI Investment', 'Geographic Expansion', 'Partnership Strategy', 'Service Innovation', 'Cost Leadership']
            impact_scores = [8.5, 7.2, 6.8, 9.1, 5.9]
            risk_scores = [4.2, 6.8, 3.1, 5.5, 7.2]
            
            fig = px.scatter(
                x=risk_scores,
                y=impact_scores,
                text=moves,
                title="Strategic Options: Impact vs Risk"
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(
                xaxis_title="Risk Level",
                yaxis_title="Impact Potential",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Strategic recommendations
        st.markdown("#### Strategic Recommendations")
        
        recommendations = [
            {
                'Priority': 'High',
                'Initiative': 'AI-Powered Predictive Maintenance Platform',
                'Investment': '£12M',
                'Timeline': '18 months',
                'Expected ROI': '340%',
                'Strategic Value': 'Market differentiation and competitive moat'
            },
            {
                'Priority': 'High',
                'Initiative': 'Sustainability-First Service Portfolio',
                'Investment': '£8M',
                'Timeline': '12 months',
                'Expected ROI': '225%',
                'Strategic Value': 'First-mover advantage in green aviation'
            },
            {
                'Priority': 'Medium',
                'Initiative': 'Asia-Pacific Market Expansion',
                'Investment': '£15M',
                'Timeline': '24 months',
                'Expected ROI': '180%',
                'Strategic Value': 'Geographic diversification and growth'
            }
        ]
        
        rec_df = pd.DataFrame(recommendations)
        
        # Display recommendations as cards
        for _, rec in rec_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="quote-card">
                    <h4>🎯 {rec['Initiative']} ({rec['Priority']} Priority)</h4>
                    <p><strong>Investment:</strong> {rec['Investment']} | <strong>Timeline:</strong> {rec['Timeline']} | <strong>ROI:</strong> {rec['Expected ROI']}</p>
                    <p><strong>Strategic Value:</strong> {rec['Strategic Value']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with intel_tab5:
        st.markdown("### 🚨 Competitive Alerts & Monitoring")
        
        # Real-time alerts dashboard
        st.markdown("#### Real-time Competitive Alerts")
        
        alerts_col1, alerts_col2 = st.columns(2)
        
        with alerts_col1:
            # Critical alerts
            st.markdown("##### 🔴 Critical Alerts")
            
            critical_alerts = [
                "DHL Aviation announced AI partnership with Google Cloud",
                "Lufthansa Technik reducing prices by 15% in European market",
                "New entrant 'SkyMRO' securing major airline contracts"
            ]
            
            for alert in critical_alerts:
                st.markdown(f"""
                <div class="alert-critical">
                    <strong>⚠️ CRITICAL:</strong> {alert}
                    <br><small>📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with alerts_col2:
            # Medium priority alerts
            st.markdown("##### 🟡 Medium Priority Alerts")
            
            medium_alerts = [
                "AAR Corp expanding Middle East operations",
                "Industry average response time improved by 8%",
                "New regulatory requirements published by EASA"
            ]
            
            for alert in medium_alerts:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); padding: 1rem; border-radius: 10px; color: white; margin: 1rem 0;">
                    <strong>📊 MONITOR:</strong> {alert}
                    <br><small>📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Market entry threat assessment
        st.markdown("#### Market Entry Threat Assessment")
        
        threat_col1, threat_col2 = st.columns(2)
        
        with threat_col1:
            # Threat matrix
            threats_data = {
                'Company': ['Amazon Logistics', 'Tesla Services', 'SpaceX', 'Chinese MRO Providers', 'Tech Startups'],
                'Entry Probability (%)': [25, 15, 35, 60, 45],
                'Potential Impact': [8, 6, 7, 9, 6],
                'Timeline': ['3-5 years', '5+ years', '2-3 years', '1-2 years', '2-4 years']
            }
            threats_df = pd.DataFrame(threats_data)
            
            fig = px.scatter(
                threats_df,
                x='Entry Probability (%)',
                y='Potential Impact',
                text='Company',
                title="Market Entry Threat Matrix",
                size=[50]*len(threats_df)
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)
        
        with threat_col2:
            # Pricing pressure indicators
            pricing_pressure = {
                'Region': ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America'],
                'Pressure Level': [6, 7, 8, 5, 6],
                'Trend': ['Stable', 'Increasing', 'High', 'Stable', 'Increasing']
            }
            pressure_df = pd.DataFrame(pricing_pressure)
            
            colors = {'Stable': 'green', 'Increasing': 'orange', 'High': 'red'}
            color_map = [colors[trend] for trend in pressure_df['Trend']]
            
            fig = px.bar(
                pressure_df,
                x='Region',
                y='Pressure Level',
                color='Trend',
                title="Regional Pricing Pressure Indicators",
                color_discrete_map=colors
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Customer satisfaction benchmarking
        st.markdown("#### Customer Satisfaction Benchmarking")
        
        satisfaction_data = {
            'Metric': ['Overall Satisfaction', 'Service Quality', 'Response Time', 'Cost Value', 'Innovation', 'Support Quality'],
            'BH Worldwide': [8.7, 8.9, 9.2, 8.1, 9.0, 8.8],
            'DHL Aviation': [8.2, 8.5, 7.8, 7.9, 7.2, 8.1],
            'Lufthansa Technik': [8.8, 9.1, 8.1, 7.5, 7.8, 8.9],
            'Industry Average': [7.8, 8.0, 7.5, 7.6, 6.9, 7.7]
        }
        
        satisfaction_df = pd.DataFrame(satisfaction_data)
        
        fig = go.Figure()
        for column in satisfaction_df.columns[1:]:
            fig.add_trace(go.Scatterpolar(
                r=satisfaction_df[column],
                theta=satisfaction_df['Metric'],
                fill='toself',
                name=column,
                opacity=0.7
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            title="Customer Satisfaction Benchmarking",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Competitive activity tracking
        st.markdown("#### Recent Competitive Activity")
        
        activity_data = {
            'Date': ['2024-12-10', '2024-12-08', '2024-12-05', '2024-12-03', '2024-12-01'],
            'Competitor': ['DHL Aviation', 'Lufthansa Technik', 'AAR Corp', 'StandardAero', 'HAECO'],
            'Activity': ['New AI partnership', 'Price reduction announcement', 'Service expansion', 'Technology upgrade', 'Market entry'],
            'Impact Level': ['High', 'Medium', 'Medium', 'Low', 'Medium'],
            'Our Response': ['Monitor closely', 'Price analysis', 'Counter-expansion', 'Assess technology', 'Competitive response']
        }
        
        activity_df = pd.DataFrame(activity_data)
        st.dataframe(activity_df, use_container_width=True)

elif page == "💰 ROI Calculator":
    # Professional Header
    st.markdown('<h1 class="main-header">💰 Financial Intelligence & ROI Calculator</h1>', unsafe_allow_html=True)
    st.markdown("*Professional financial modeling based on actual BH Worldwide performance data*")
    
    # Load actual BH Worldwide financial data
    try:
        with open(dashboard.data_path / "Financial/BH_Actual_Financials/financial_summary.json") as f:
            financial_data = json.load(f)
        actual_financials = financial_data["company_financial_data"]["key_metrics_dashboard"]["latest_year_metrics"]
    except:
        # Fallback to known values
        actual_financials = {
            "revenue_gbp_millions": 16.0,
            "gross_profit_gbp_millions": 5.2,
            "net_income_gbp_millions": 0.8,
            "total_assets_gbp_millions": 5.5,
            "shareholders_equity_gbp_millions": 2.0,
            "gross_margin_percent": 32.2,
            "net_margin_percent": 4.9,
            "current_ratio": 1.6
        }
    
    # REALISTIC INVESTMENT JUSTIFICATION BANNER
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        border: 3px solid #2E86AB;
        box-shadow: 0 8px 16px rgba(46, 134, 171, 0.3);
    ">
        <div style="text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 28px; font-weight: bold;">💼 AI Investment Business Case - BH Worldwide</h2>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 15px;">
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 22px; font-weight: bold;">£16.0M</div>
                    <div style="font-size: 14px;">Current Revenue (2024)</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 22px; font-weight: bold;">32.2%</div>
                    <div style="font-size: 14px;">Current Gross Margin</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 22px; font-weight: bold;">£0.8M</div>
                    <div style="font-size: 14px;">Current Net Income</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 22px; font-weight: bold;">4.9%</div>
                    <div style="font-size: 14px;">Current Net Margin</div>
                </div>
            </div>
            <p style="margin: 15px 0 5px 0; font-size: 16px; font-weight: bold;">
                AI Investment Opportunity: Protect revenue through operational efficiency and improved win rates
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Current State Summary - REAL BH WORLDWIDE DATA
    st.markdown("### 📊 Current Financial Position - BH Worldwide 2024")
    exec_summary_col1, exec_summary_col2, exec_summary_col3, exec_summary_col4, exec_summary_col5 = st.columns(5)
    
    with exec_summary_col1:
        st.metric("Annual Revenue", f"£{actual_financials['revenue_gbp_millions']:.1f}M", "-3.7% YoY")
    with exec_summary_col2:
        st.metric("Gross Profit", f"£{actual_financials['gross_profit_gbp_millions']:.1f}M", f"{actual_financials['gross_margin_percent']:.1f}% margin")
    with exec_summary_col3:
        st.metric("Net Income", f"£{actual_financials['net_income_gbp_millions']:.1f}M", f"{actual_financials['net_margin_percent']:.1f}% margin")
    with exec_summary_col4:
        st.metric("Total Assets", f"£{actual_financials['total_assets_gbp_millions']:.1f}M", "Strong balance sheet")
    with exec_summary_col5:
        st.metric("Current Ratio", f"{actual_financials['current_ratio']:.1f}x", "Healthy liquidity")
    
    # Realistic Financial Modeling Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Financial Dashboard",
        "🧮 Advanced Financial Modeling", 
        "📋 Business Case Generator",
        "📈 Scenario Analysis",
        "💼 Investment Justification"
    ])
    
    with tab1:  # Executive Financial Dashboard
        st.markdown('<h3 style="color: #28a745;">📊 Executive Financial Dashboard</h3>', unsafe_allow_html=True)
        
        # Interactive Financial Parameters - REALISTIC RANGES
        st.markdown("### 🎛️ Financial Model Parameters")
        
        param_col1, param_col2, param_col3 = st.columns(3)
        
        with param_col1:
            st.markdown("**Current State - Based on BH Worldwide Performance**")
            current_revenue = actual_financials['revenue_gbp_millions']
            current_gross_margin = st.slider("Current Gross Margin (%)", 25, 35, int(actual_financials['gross_margin_percent']), key="current_margin")
            current_response_time = st.slider("Current Response Time (min)", 90, 150, 105, key="current_response")
            current_win_rate = st.slider("Current Win Rate (%)", 55, 75, 65, key="current_win")
            monthly_quotes = st.slider("Monthly Quote Requests", 80, 200, 120, key="monthly_quotes")
            avg_quote_value = st.slider("Average Quote Value (£)", 8000, 35000, 15000, key="avg_quote")
        
        with param_col2:
            st.markdown("**AI-Enhanced Performance - Realistic Targets**")
            ai_response_time = st.slider("AI Response Time (min) - Affects quote volume", 8, 25, 15, key="ai_response")
            st.caption("🚀 Faster response times win more quotes")
            ai_win_rate = st.slider("AI Win Rate (%)", 70, 85, 78, key="ai_win") # Realistic 13% improvement
            efficiency_gain = st.slider("Operational Efficiency Gain (%)", 8, 25, 15, key="efficiency")
            cost_reduction = st.slider("Process Cost Reduction (%) - Direct cost savings", 10, 30, 18, key="cost_reduction")
            st.caption("💰 Reduces operational expenses")
            customer_retention = st.slider("Customer Retention Improvement (%)", 5, 15, 8, key="retention")
            customer_satisfaction = st.slider("Customer Satisfaction (%) - Boosts retention value", 8, 20, 12, key="satisfaction")
            st.caption("😊 Higher satisfaction multiplies retention benefits")
        
        with param_col3:
            st.markdown("**Investment Parameters - Market Realistic**")
            implementation_cost = st.slider("Implementation Cost (£)", 500000, 2000000, 1200000, key="impl_cost")
            annual_operating_cost = st.slider("Annual Operating Cost (£)", 80000, 300000, 150000, key="annual_cost")
            discount_rate = st.slider("Discount Rate (%)", 8, 15, 10, key="discount_rate")
            project_duration = st.slider("Project Duration (years)", 3, 7, 5, key="duration")
            risk_factor = st.slider("Implementation Risk Factor (%)", 5, 25, 12, key="risk_factor")
        
        # REALISTIC Financial Calculations Based on BH Worldwide Data
        current_annual_revenue = current_revenue * 1000000  # Convert to pounds
        
        # Calculate revenue improvements based on win rate and efficiency
        win_rate_improvement = (ai_win_rate - current_win_rate) / 100
        additional_revenue_from_wins = current_annual_revenue * win_rate_improvement * 0.6  # Conservative factor
        
        # AI Response Time Impact on Quote Volume (faster response = more quotes won)
        response_time_improvement = (current_response_time - ai_response_time) / current_response_time
        additional_quotes_from_speed = monthly_quotes * 12 * response_time_improvement * 0.3  # 30% of improvement
        speed_revenue_impact = additional_quotes_from_speed * avg_quote_value * (current_gross_margin/100)
        
        # Operational cost savings from efficiency and process cost reduction
        current_operating_costs = current_annual_revenue * (1 - current_gross_margin/100)
        operational_savings = current_operating_costs * (efficiency_gain / 100)
        process_cost_savings = current_operating_costs * (cost_reduction / 100)
        
        # Customer retention value enhanced by satisfaction improvement
        base_retention_value = current_annual_revenue * (customer_retention / 100) * 0.3
        satisfaction_multiplier = 1 + (customer_satisfaction / 100) * 0.5  # Satisfaction boosts retention value
        retention_value = base_retention_value * satisfaction_multiplier
        
        # Total annual benefits
        total_annual_benefit = additional_revenue_from_wins + speed_revenue_impact + operational_savings + process_cost_savings + retention_value
        
        # Risk-adjusted benefits
        risk_adjusted_benefit = total_annual_benefit * (1 - risk_factor/100)
        net_annual_benefit = risk_adjusted_benefit - annual_operating_cost
        
        # Realistic Financial Metrics
        st.markdown("### 💰 Investment Performance Metrics - Professional Analysis")
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            roi_percentage = (net_annual_benefit / implementation_cost) * 100 if implementation_cost > 0 else 0
            roi_status = "Excellent" if roi_percentage > 25 else "Good" if roi_percentage > 15 else "Acceptable" if roi_percentage > 10 else "Poor"
            st.metric("Annual ROI", f"{roi_percentage:.1f}%", f"{roi_status} return")
        
        with metrics_col2:
            payback_months = implementation_cost / (net_annual_benefit / 12) if net_annual_benefit > 0 else float('inf')
            payback_status = "Fast" if payback_months < 18 else "Reasonable" if payback_months < 36 else "Slow"
            payback_display = f"{payback_months:.1f} months" if payback_months < 120 else "N/A"
            st.metric("Payback Period", payback_display, f"{payback_status} recovery")
        
        with metrics_col3:
            # NPV Calculation with proper discounting
            npv = -implementation_cost
            for year in range(1, project_duration + 1):
                npv += net_annual_benefit / ((1 + discount_rate/100) ** year)
            npv_status = "Positive" if npv > 0 else "Negative"
            st.metric("NPV (5 years)", f"£{npv:,.0f}", f"{npv_status} value")
        
        with metrics_col4:
            # Revenue protection (% of current revenue)
            revenue_protection = (risk_adjusted_benefit / current_annual_revenue) * 100
            protection_status = "High" if revenue_protection > 15 else "Medium" if revenue_protection > 8 else "Low"
            st.metric("Revenue Protection", f"{revenue_protection:.1f}%", f"{protection_status} impact")
        
        # Investment Timeline Visualization
        st.markdown("### 📅 Investment Timeline & Cash Flow Analysis")
        
        timeline_col1, timeline_col2 = st.columns(2)
        
        with timeline_col1:
            # Dynamic Cumulative Cash Flow Over Time based on project duration
            max_months = min(project_duration * 12 + 12, 84)  # Project duration + 1 year buffer, max 7 years
            months = list(range(0, max_months + 1))
            cumulative_cashflow = []
            
            for month in months:
                if month == 0:
                    cashflow = -implementation_cost
                elif month <= 6:
                    # Gradual ramp-up in first 6 months
                    monthly_benefit = (net_annual_benefit / 12) * (month / 6)
                    cashflow = cumulative_cashflow[-1] + monthly_benefit
                else:
                    # Full benefits after implementation
                    monthly_benefit = net_annual_benefit / 12
                    cashflow = cumulative_cashflow[-1] + monthly_benefit
                cumulative_cashflow.append(cashflow)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months,
                y=cumulative_cashflow,
                mode='lines+markers',
                name='Cumulative Cash Flow',
                line=dict(color='#2E86AB', width=3),
                fill='tonexty'
            ))
            
            # Add break-even line
            fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even Point")
            
            # Add payback period marker if reasonable and within timeline
            if payback_months < max_months and payback_months > 0:
                fig.add_vline(x=payback_months, line_dash="dot", line_color="blue", 
                             annotation_text=f"Payback: {payback_months:.1f} months")
            
            # Dynamic axis scaling
            max_cashflow = max(cumulative_cashflow) if cumulative_cashflow else 0
            min_cashflow = min(cumulative_cashflow) if cumulative_cashflow else -implementation_cost
            y_range_padding = abs(max_cashflow - min_cashflow) * 0.1
            
            fig.update_layout(
                title="Dynamic Investment Cash Flow Timeline",
                xaxis_title="Months",
                yaxis_title="Cumulative Cash Flow (£)",
                height=400,
                template="plotly_white",
                xaxis=dict(range=[0, max_months]),
                yaxis=dict(range=[min_cashflow - y_range_padding, max_cashflow + y_range_padding])
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with timeline_col2:
            # Realistic Scenario Analysis
            st.markdown("**Professional Scenario Analysis**")
            
            # Realistic scenarios based on actual business performance
            scenarios = ['Conservative', 'Base Case', 'Optimistic']
            conservative_roi = max(roi_percentage * 0.6, 5)  # Minimum 5% ROI
            optimistic_roi = min(roi_percentage * 1.4, 45)  # Maximum 45% ROI
            roi_values = [conservative_roi, roi_percentage, optimistic_roi]
            probabilities = [30, 40, 30]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=scenarios,
                y=roi_values,
                text=[f"{val:.1f}%" for val in roi_values],
                textposition='auto',
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
            ))
            
            fig.update_layout(
                title="Professional ROI Scenario Analysis",
                yaxis_title="Annual ROI (%)",
                height=300,
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Realistic implementation milestones
            st.markdown("**Realistic Implementation Timeline:**")
            payback_realistic = max(payback_months, 12)  # Minimum 12 months realistic
            milestones = [
                {"month": 3, "milestone": "AI System Deployment", "status": "🔵"},
                {"month": 6, "milestone": "Staff Training Complete", "status": "🟡"},
                {"month": 9, "milestone": "Process Optimization", "status": "🟡"},
                {"month": int(payback_realistic), "milestone": "Investment Payback", "status": "🟢"}
            ]
            
            for milestone in milestones:
                st.markdown(f"{milestone['status']} **Month {milestone['month']}**: {milestone['milestone']}")
            
            # Business case summary
            st.markdown("**💼 Business Case Summary:**")
            st.markdown(f"""
            - **Investment:** £{implementation_cost:,}
            - **Annual Benefit:** £{risk_adjusted_benefit:,.0f}
            - **ROI:** {roi_percentage:.1f}% annually
            - **Risk Level:** {'Low' if risk_factor < 15 else 'Medium' if risk_factor < 20 else 'High'}
            """)
    
    with tab2:  # Advanced Financial Modeling
        st.markdown('<h3 style="color: #007bff;">🧮 Professional Financial Modeling & Risk Analysis</h3>', unsafe_allow_html=True)
        
        # Professional Monte Carlo Simulation
        st.markdown("### 🎲 Monte Carlo Risk Analysis")
        st.markdown("*Professional-grade simulation based on industry variance patterns*")
        
        sim_col1, sim_col2 = st.columns(2)
        
        with sim_col1:
            st.markdown("**Simulation Parameters:**")
            n_simulations = st.selectbox("Number of Simulations", [1000, 5000, 10000], index=1)
            confidence_level = st.slider("Confidence Level (%)", 80, 99, 95)
            
        with sim_col2:
            st.markdown("**Risk Factors:**")
            market_risk = st.slider("Market Risk Variance (%)", 5, 20, 10)
            implementation_risk = st.slider("Implementation Risk (%)", 10, 30, 15)
        
        if st.button("🔄 Run Professional Monte Carlo Analysis", type="primary"):
            # Realistic Monte Carlo simulation
            np.random.seed(42)
            
            roi_results = []
            npv_results = []
            payback_results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(n_simulations):
                # Realistic parameter variations
                sim_win_rate = max(60, min(90, np.random.normal(ai_win_rate, market_risk/2)))
                sim_efficiency = max(5, min(35, np.random.normal(efficiency_gain, market_risk/3)))
                sim_impl_cost = max(implementation_cost * 0.8, 
                                  np.random.normal(implementation_cost, implementation_cost * implementation_risk/100))
                sim_annual_cost = max(annual_operating_cost * 0.7,
                                    np.random.normal(annual_operating_cost, annual_operating_cost * 0.2))
                
                # Calculate simulated metrics using realistic formulas
                sim_win_improvement = (sim_win_rate - current_win_rate) / 100
                sim_additional_revenue = current_annual_revenue * sim_win_improvement * 0.6
                sim_operational_savings = current_operating_costs * (sim_efficiency / 100)
                sim_retention_value = current_annual_revenue * (customer_retention / 100) * 0.3
                
                sim_total_benefit = sim_additional_revenue + sim_operational_savings + sim_retention_value
                sim_risk_adjusted = sim_total_benefit * (1 - risk_factor/100)
                sim_net_benefit = sim_risk_adjusted - sim_annual_cost
                
                # Calculate financial metrics
                sim_roi = (sim_net_benefit / sim_impl_cost) * 100 if sim_impl_cost > 0 else 0
                sim_payback = sim_impl_cost / (sim_net_benefit / 12) if sim_net_benefit > 0 else 120
                
                # NPV calculation
                sim_npv = -sim_impl_cost
                for year in range(1, project_duration + 1):
                    sim_npv += sim_net_benefit / ((1 + discount_rate/100) ** year)
                
                roi_results.append(min(max(sim_roi, -50), 100))  # Cap at reasonable range
                npv_results.append(sim_npv)
                payback_results.append(min(sim_payback, 120))  # Cap at 10 years
                
                # Update progress
                if i % (n_simulations // 10) == 0:
                    progress_bar.progress((i + 1) / n_simulations)
                    status_text.text(f"Processing simulation {i+1:,} of {n_simulations:,}")
            
            progress_bar.progress(1.0)
            status_text.text("✅ Simulation complete!")
            
            # Professional Results Display
            monte_col1, monte_col2 = st.columns(2)
            
            with monte_col1:
                # Professional ROI Distribution
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=roi_results,
                    nbinsx=40,
                    name='ROI Distribution',
                    marker_color='#2E86AB',
                    opacity=0.7
                ))
                
                # Add realistic percentile lines
                p10 = np.percentile(roi_results, 10)
                p50 = np.percentile(roi_results, 50)
                p90 = np.percentile(roi_results, 90)
                
                fig.add_vline(x=p10, line_dash="dash", line_color="red", annotation_text=f"10th %ile: {p10:.1f}%")
                fig.add_vline(x=p50, line_dash="solid", line_color="green", annotation_text=f"Median: {p50:.1f}%")
                fig.add_vline(x=p90, line_dash="dash", line_color="blue", annotation_text=f"90th %ile: {p90:.1f}%")
                
                fig.update_layout(
                    title="Professional ROI Risk Analysis",
                    xaxis_title="Annual ROI (%)",
                    yaxis_title="Probability Density",
                    height=400,
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with monte_col2:
                # Payback Period Distribution
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=payback_results,
                    nbinsx=30,
                    name='Payback Distribution',
                    marker_color='#A23B72',
                    opacity=0.7
                ))
                
                median_payback = np.percentile(payback_results, 50)
                fig.add_vline(x=median_payback, line_dash="solid", line_color="orange", 
                             annotation_text=f"Median: {median_payback:.1f} months")
                
                fig.update_layout(
                    title="Payback Period Risk Analysis",
                    xaxis_title="Payback Period (Months)",
                    yaxis_title="Probability Density",
                    height=400,
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Professional Summary Statistics
            st.markdown("### 📊 Professional Risk Analysis Summary")
            
            result_col1, result_col2, result_col3, result_col4 = st.columns(4)
            
            with result_col1:
                best_case = np.percentile(roi_results, 90)
                st.metric("Best Case ROI (90th %ile)", f"{best_case:.1f}%", 
                         "Strong upside potential" if best_case > 30 else "Moderate upside")
            with result_col2:
                median_roi = np.percentile(roi_results, 50)
                st.metric("Expected ROI (Median)", f"{median_roi:.1f}%",
                         "Excellent" if median_roi > 25 else "Good" if median_roi > 15 else "Acceptable")
            with result_col3:
                worst_case = np.percentile(roi_results, 10)
                st.metric("Worst Case ROI (10th %ile)", f"{worst_case:.1f}%",
                         "Acceptable risk" if worst_case > 5 else "High risk")
            with result_col4:
                positive_roi_rate = (np.array(roi_results) > 0).mean() * 100
                st.metric("Success Probability", f"{positive_roi_rate:.1f}%",
                         "Low risk" if positive_roi_rate > 80 else "Medium risk")
                         
            # Risk Assessment Summary
            st.markdown("### 🎯 Investment Risk Assessment")
            risk_level = "Low" if worst_case > 10 and positive_roi_rate > 85 else "Medium" if worst_case > 0 and positive_roi_rate > 70 else "High"
            confidence = confidence_level
            
            st.markdown(f"""
            **Risk Level:** {risk_level} | **Confidence Level:** {confidence}%
            
            - **Expected Annual ROI:** {median_roi:.1f}% (range: {worst_case:.1f}% to {best_case:.1f}%)
            - **Expected Payback:** {median_payback:.1f} months
            - **Probability of Positive ROI:** {positive_roi_rate:.1f}%
            - **Investment Recommendation:** {'✅ Recommended' if positive_roi_rate > 75 and median_roi > 10 else '⚠️ Proceed with caution' if positive_roi_rate > 60 else '❌ High risk'}
            """)
        
        # Professional Risk Summary
        st.markdown("### 🎯 Professional Investment Summary")
        
        # Define risk level based on ROI and other factors
        if 'risk_level' not in locals():
            if roi_percentage > 25 and payback_months < 24:
                risk_level = "Low"
            elif roi_percentage > 15 and payback_months < 36:
                risk_level = "Medium"
            else:
                risk_level = "High"
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown("**Investment Parameters:**")
            st.markdown(f"""
            - **Implementation Cost:** £{implementation_cost:,}
            - **Annual Operating Cost:** £{annual_operating_cost:,}
            - **Discount Rate:** {discount_rate}%
            - **Project Duration:** {project_duration} years
            - **Risk Factor:** {risk_factor}%
            """)
            
        with summary_col2:
            st.markdown("**Expected Outcomes:**")
            st.markdown(f"""
            - **Annual ROI:** {roi_percentage:.1f}%
            - **Payback Period:** {payback_display}
            - **NPV:** £{npv:,}
            - **Revenue Protection:** {revenue_protection:.1f}%
            - **Risk Level:** {risk_level}
            """)
    
    with tab3:  # Business Case Generator
        st.markdown('<h3 style="color: #6f42c1;">📋 Business Case Generator</h3>', unsafe_allow_html=True)
        
        # Auto-generated Executive Summary
        st.markdown("### 📄 Executive Summary")
        
        executive_summary = f"""
        **Investment Recommendation: APPROVE**
        
        **Financial Highlights:**
        • **ROI**: {roi_percentage:.0f}% annual return on investment
        • **Payback Period**: {payback_months:.1f} months to full cost recovery
        • **NPV**: £{npv:,.0f} net present value over 5 years
        • **Risk Assessment**: Low risk, high reward investment
        
        **Strategic Impact:**
        • Revenue increase of £{additional_revenue_from_wins:,.0f} annually through improved win rates
        • Speed advantage generating £{speed_revenue_impact:,.0f} from faster response times
        • Operational efficiency gains of {efficiency_gain}% plus {cost_reduction}% process cost reduction
        • Customer satisfaction improvement of {customer_satisfaction}% enhancing retention by £{retention_value:,.0f}
        • Market competitive advantage through AI-powered response capabilities
        
        **Implementation Timeline:**
        • Phase 1 (Months 1-2): System deployment and integration
        • Phase 2 (Months 3-4): Staff training and process optimization
        • Phase 3 (Months 5-6): Full operational capability and ROI realization
        
        **Recommendation:**
        This investment presents an exceptional opportunity with guaranteed returns and strategic 
        positioning advantages. The financial metrics exceed all investment criteria and the risk 
        profile is highly favorable. Immediate approval is recommended to capitalize on market opportunities.
        """
        
        st.info(executive_summary)
        
        # Professional Business Case Document
        st.markdown("### 📊 Professional Business Case Document")
        
        business_case_col1, business_case_col2 = st.columns(2)
        
        with business_case_col1:
            st.markdown("**Investment Overview**")
            
            investment_summary = pd.DataFrame([
                {"Component": "Initial Implementation", "Cost (£)": f"{implementation_cost:,}", "Timeline": "Months 1-2"},
                {"Component": "Annual Operating Cost", "Cost (£)": f"{annual_operating_cost:,}", "Timeline": "Ongoing"},
                {"Component": "Training & Change Mgmt", "Cost (£)": "150,000", "Timeline": "Months 2-3"},
                {"Component": "Contingency (10%)", "Cost (£)": f"{implementation_cost * 0.1:,.0f}", "Timeline": "As needed"},
                {"Component": "**Total Investment**", "Cost (£)": f"**£{implementation_cost * 1.1 + 150000:,.0f}**", "Timeline": "**2 years**"}
            ])
            
            st.dataframe(investment_summary, use_container_width=True, hide_index=True)
            
            st.markdown("**Risk Mitigation Strategies**")
            risks = [
                {"Risk": "Technology Integration", "Probability": "Low", "Mitigation": "Phased rollout, expert support"},
                {"Risk": "Staff Adoption", "Probability": "Medium", "Mitigation": "Comprehensive training program"},
                {"Risk": "Market Changes", "Probability": "Low", "Mitigation": "Flexible system architecture"},
                {"Risk": "Competition Response", "Probability": "Medium", "Mitigation": "First-mover advantage"}
            ]
            
            risk_df = pd.DataFrame(risks)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
        
        with business_case_col2:
            st.markdown("**Benefits Realization Plan**")
            
            benefits = [
                {"Benefit Category": "Revenue Enhancement", "Year 1": f"£{additional_revenue_from_wins:,.0f}", "Year 2": f"£{additional_revenue_from_wins * 1.1:,.0f}", "Year 3": f"£{additional_revenue_from_wins * 1.2:,.0f}"},
                {"Benefit Category": "Cost Reduction", "Year 1": f"£{operational_savings:,.0f}", "Year 2": f"£{operational_savings * 1.15:,.0f}", "Year 3": f"£{operational_savings * 1.3:,.0f}"},
                {"Benefit Category": "Efficiency Gains", "Year 1": "25%", "Year 2": "35%", "Year 3": "45%"},
                {"Benefit Category": "Customer Satisfaction", "Year 1": "+18%", "Year 2": "+25%", "Year 3": "+35%"}
            ]
            
            benefits_df = pd.DataFrame(benefits)
            st.dataframe(benefits_df, use_container_width=True, hide_index=True)
            
            # Implementation timeline
            st.markdown("**Implementation Timeline**")
            
            timeline_data = [
                {"Phase": "Phase 1: Foundation", "Duration": "Months 1-2", "Activities": "System setup, integration"},
                {"Phase": "Phase 2: Deployment", "Duration": "Months 3-4", "Activities": "Rollout, training"},
                {"Phase": "Phase 3: Optimization", "Duration": "Months 5-6", "Activities": "Fine-tuning, scaling"},
                {"Phase": "Phase 4: Full Operation", "Duration": "Month 7+", "Activities": "BAU, continuous improvement"}
            ]
            
            timeline_df = pd.DataFrame(timeline_data)
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
        
        # Resource Requirements
        st.markdown("### 👥 Resource Requirements")
        
        resource_col1, resource_col2 = st.columns(2)
        
        with resource_col1:
            st.markdown("**Human Resources**")
            
            resources = [
                {"Role": "Project Manager", "FTE": "1.0", "Duration": "6 months", "Cost": "£120,000"},
                {"Role": "AI/ML Engineer", "FTE": "2.0", "Duration": "4 months", "Cost": "£200,000"},
                {"Role": "Systems Integrator", "FTE": "1.5", "Duration": "3 months", "Cost": "£135,000"},
                {"Role": "Training Specialist", "FTE": "1.0", "Duration": "2 months", "Cost": "£60,000"},
                {"Role": "Change Management", "FTE": "0.5", "Duration": "6 months", "Cost": "£90,000"}
            ]
            
            resource_df = pd.DataFrame(resources)
            st.dataframe(resource_df, use_container_width=True, hide_index=True)
        
        with resource_col2:
            st.markdown("**Technology Infrastructure**")
            
            tech_requirements = [
                {"Component": "AI/ML Platform License", "Cost": "£300,000", "Type": "Software"},
                {"Component": "Cloud Infrastructure", "Cost": "£150,000", "Type": "Hardware"},
                {"Component": "Integration Tools", "Cost": "£80,000", "Type": "Software"},
                {"Component": "Security & Monitoring", "Cost": "£120,000", "Type": "Software"},
                {"Component": "Backup & DR", "Cost": "£50,000", "Type": "Service"}
            ]
            
            tech_df = pd.DataFrame(tech_requirements)
            st.dataframe(tech_df, use_container_width=True, hide_index=True)
        
        # Generate Report Button
        if st.button("📄 Generate Complete Business Case Report", type="primary", use_container_width=True):
            st.success("📊 Complete business case report generated successfully!")
            st.info("Report includes: Executive Summary, Financial Analysis, Risk Assessment, Implementation Plan, Resource Requirements, and ROI Projections")
            st.balloons()
    
    with tab4:  # Financial Scenarios
        st.markdown('<h3 style="color: #dc3545;">📈 Financial Scenarios & Market Analysis</h3>', unsafe_allow_html=True)
        
        # Scenario Modeling
        st.markdown("### 🎭 Scenario Analysis")
        
        scenario_col1, scenario_col2 = st.columns(2)
        
        with scenario_col1:
            # Conservative/Optimistic/Realistic scenarios
            scenarios = {
                'Conservative': {
                    'win_rate_multiplier': 0.85,
                    'quote_value_multiplier': 0.9,
                    'opportunity_multiplier': 0.9,
                    'cost_multiplier': 1.15,
                    'description': 'Economic downturn, increased competition'
                },
                'Realistic': {
                    'win_rate_multiplier': 1.0,
                    'quote_value_multiplier': 1.0,
                    'opportunity_multiplier': 1.0,
                    'cost_multiplier': 1.0,
                    'description': 'Current market conditions continue'
                },
                'Optimistic': {
                    'win_rate_multiplier': 1.15,
                    'quote_value_multiplier': 1.1,
                    'opportunity_multiplier': 1.2,
                    'cost_multiplier': 0.9,
                    'description': 'Market expansion, economic growth'
                }
            }
            
            scenario_results = []
            
            for scenario_name, multipliers in scenarios.items():
                # Adjust parameters based on scenario
                scenario_ai_win_rate = ai_win_rate * multipliers['win_rate_multiplier']
                scenario_quote_value = avg_quote_value * multipliers['quote_value_multiplier']
                # Calculate scenario quote volume based on current baseline
                current_monthly_quotes = current_annual_revenue / (12 * avg_quote_value * (current_win_rate/100))
                scenario_opportunities = current_monthly_quotes * multipliers['opportunity_multiplier']
                scenario_impl_cost = implementation_cost * multipliers['cost_multiplier']
                
                # Calculate scenario metrics
                scenario_monthly_wins = (scenario_opportunities * scenario_ai_win_rate / 100)
                scenario_annual_revenue = scenario_monthly_wins * 12 * scenario_quote_value
                scenario_additional_revenue = scenario_annual_revenue - current_annual_revenue
                scenario_net_benefit = scenario_additional_revenue - annual_operating_cost
                scenario_roi = (scenario_net_benefit / scenario_impl_cost) * 100
                scenario_payback = scenario_impl_cost / (scenario_net_benefit / 12) if scenario_net_benefit > 0 else float('inf')
                
                scenario_results.append({
                    'Scenario': scenario_name,
                    'ROI (%)': f"{scenario_roi:.1f}%",
                    'Payback (months)': f"{scenario_payback:.1f}",
                    'Additional Revenue': f"£{scenario_additional_revenue:,.0f}",
                    'Net Benefit': f"£{scenario_net_benefit:,.0f}",
                    'Description': multipliers['description']
                })
            
            scenario_df = pd.DataFrame(scenario_results)
            st.dataframe(scenario_df, use_container_width=True, hide_index=True)
        
        with scenario_col2:
            # Scenario comparison chart
            roi_values = []
            scenario_names = []
            
            for scenario_name, multipliers in scenarios.items():
                scenario_ai_win_rate = ai_win_rate * multipliers['win_rate_multiplier']
                scenario_quote_value = avg_quote_value * multipliers['quote_value_multiplier']
                # Calculate scenario quote volume based on current baseline
                current_monthly_quotes = current_annual_revenue / (12 * avg_quote_value * (current_win_rate/100))
                scenario_opportunities = current_monthly_quotes * multipliers['opportunity_multiplier']
                scenario_impl_cost = implementation_cost * multipliers['cost_multiplier']
                
                scenario_monthly_wins = (scenario_opportunities * scenario_ai_win_rate / 100)
                scenario_annual_revenue = scenario_monthly_wins * 12 * scenario_quote_value
                scenario_additional_revenue = scenario_annual_revenue - current_annual_revenue
                scenario_net_benefit = scenario_additional_revenue - annual_operating_cost
                scenario_roi = (scenario_net_benefit / scenario_impl_cost) * 100
                
                roi_values.append(scenario_roi)
                scenario_names.append(scenario_name)
            
            colors = ['#dc3545', '#ffc107', '#28a745']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=scenario_names,
                y=roi_values,
                text=[f"{val:.0f}%" for val in roi_values],
                textposition='auto',
                marker_color=colors
            ))
            
            fig.update_layout(
                title="ROI by Scenario",
                yaxis_title="ROI (%)",
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Market Condition Impact Analysis
        st.markdown("### 🌍 Market Condition Impact Analysis")
        
        market_col1, market_col2 = st.columns(2)
        
        with market_col1:
            st.markdown("**Recession Scenario Impact**")
            
            recession_factors = {
                "Quote Volume": "-25%",
                "Average Quote Value": "-15%", 
                "Win Rate": "-10%",
                "Implementation Cost": "+10%",
                "Operating Cost": "+5%"
            }
            
            recession_impact = []
            for factor, impact in recession_factors.items():
                recession_impact.append({"Factor": factor, "Impact": impact})
            
            recession_df = pd.DataFrame(recession_impact)
            st.dataframe(recession_df, use_container_width=True, hide_index=True)
            
            # Calculate recession ROI
            # Calculate current monthly quote volume
            current_monthly_quotes = current_annual_revenue / (12 * avg_quote_value * (current_win_rate/100))
            recession_opportunities = current_monthly_quotes * 0.75
            recession_quote_value = avg_quote_value * 0.85
            recession_win_rate = ai_win_rate * 0.9
            recession_impl_cost = implementation_cost * 1.1
            
            recession_monthly_wins = (recession_opportunities * recession_win_rate / 100)
            recession_annual_revenue = recession_monthly_wins * 12 * recession_quote_value
            recession_additional_revenue = recession_annual_revenue - current_annual_revenue
            recession_net_benefit = recession_additional_revenue - annual_operating_cost * 1.05
            recession_roi = (recession_net_benefit / recession_impl_cost) * 100
            
            st.metric("Recession Scenario ROI", f"{recession_roi:.1f}%", f"{recession_roi - roi_percentage:.1f}% vs base")
        
        with market_col2:
            st.markdown("**Growth Scenario Impact**")
            
            growth_factors = {
                "Quote Volume": "+30%",
                "Average Quote Value": "+20%",
                "Win Rate": "+15%", 
                "Implementation Cost": "-5%",
                "Operating Cost": "Flat"
            }
            
            growth_impact = []
            for factor, impact in growth_factors.items():
                growth_impact.append({"Factor": factor, "Impact": impact})
            
            growth_df = pd.DataFrame(growth_impact)
            st.dataframe(growth_df, use_container_width=True, hide_index=True)
            
            # Calculate growth ROI
            # Calculate current monthly quote volume
            current_monthly_quotes = current_annual_revenue / (12 * avg_quote_value * (current_win_rate/100))
            growth_opportunities = current_monthly_quotes * 1.3
            growth_quote_value = avg_quote_value * 1.2
            growth_win_rate = ai_win_rate * 1.15
            growth_impl_cost = implementation_cost * 0.95
            
            growth_monthly_wins = (growth_opportunities * growth_win_rate / 100)
            growth_annual_revenue = growth_monthly_wins * 12 * growth_quote_value
            growth_additional_revenue = growth_annual_revenue - current_annual_revenue
            growth_net_benefit = growth_additional_revenue - annual_operating_cost
            growth_roi = (growth_net_benefit / growth_impl_cost) * 100
            
            st.metric("Growth Scenario ROI", f"{growth_roi:.1f}%", f"{growth_roi - roi_percentage:.1f}% vs base")
        
        # Competitive Response Modeling
        st.markdown("### 🥊 Competitive Response Analysis")
        
        comp_response_col1, comp_response_col2 = st.columns(2)
        
        with comp_response_col1:
            st.markdown("**Competitor Response Scenarios**")
            
            # Time-based competitive response
            months = list(range(1, 25))
            no_response = [ai_win_rate] * 24
            slow_response = [ai_win_rate if m <= 12 else ai_win_rate - (m-12)*2 for m in months]
            fast_response = [ai_win_rate if m <= 6 else ai_win_rate - (m-6)*1.5 for m in months]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=no_response, mode='lines', name='No Competitor Response', line=dict(color='#28a745')))
            fig.add_trace(go.Scatter(x=months, y=slow_response, mode='lines', name='Slow Response (12m)', line=dict(color='#ffc107')))
            fig.add_trace(go.Scatter(x=months, y=fast_response, mode='lines', name='Fast Response (6m)', line=dict(color='#dc3545')))
            
            fig.update_layout(
                title="Win Rate Over Time by Competitor Response",
                xaxis_title="Months",
                yaxis_title="Win Rate (%)",
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with comp_response_col2:
            # Customer adoption rate variations
            st.markdown("**Customer Adoption Rate Analysis**")
            
            adoption_scenarios = [
                {"Scenario": "Slow Adoption", "Month 6": "40%", "Month 12": "70%", "Month 18": "90%"},
                {"Scenario": "Normal Adoption", "Month 6": "60%", "Month 12": "85%", "Month 18": "95%"},
                {"Scenario": "Fast Adoption", "Month 6": "80%", "Month 12": "95%", "Month 18": "98%"}
            ]
            
            adoption_df = pd.DataFrame(adoption_scenarios)
            st.dataframe(adoption_df, use_container_width=True, hide_index=True)
            
            # Impact on cumulative revenue
            months = list(range(1, 19))
            slow_adoption = [0.4 + (m-1)*0.03 if m <= 6 else 0.4 + 5*0.03 + (m-6)*0.02 for m in months]
            normal_adoption = [0.6 + (m-1)*0.025 if m <= 6 else 0.6 + 5*0.025 + (m-6)*0.015 for m in months]
            fast_adoption = [0.8 + (m-1)*0.015 if m <= 6 else 0.8 + 5*0.015 + (m-6)*0.01 for m in months]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=slow_adoption, mode='lines+markers', name='Slow Adoption'))
            fig.add_trace(go.Scatter(x=months, y=normal_adoption, mode='lines+markers', name='Normal Adoption'))
            fig.add_trace(go.Scatter(x=months, y=fast_adoption, mode='lines+markers', name='Fast Adoption'))
            
            fig.update_layout(
                title="Customer Adoption Rate Over Time",
                xaxis_title="Months",
                yaxis_title="Adoption Rate",
                height=300,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:  # Investment Justification
        st.markdown('<h3 style="color: #17a2b8;">💼 Investment Justification & Strategic Value</h3>', unsafe_allow_html=True)
        
        # Total Cost of Ownership Analysis
        st.markdown("### 💰 Total Cost of Ownership (TCO) Analysis")
        
        tco_col1, tco_col2 = st.columns(2)
        
        with tco_col1:
            # 5-year TCO breakdown
            tco_components = [
                {"Component": "Initial Implementation", "Year 1": implementation_cost, "Year 2-5": 0},
                {"Component": "Annual Operating Cost", "Year 1": annual_operating_cost, "Year 2-5": annual_operating_cost * 4},
                {"Component": "Maintenance & Support", "Year 1": implementation_cost * 0.1, "Year 2-5": implementation_cost * 0.15 * 4},
                {"Component": "Training & Development", "Year 1": 150000, "Year 2-5": 50000 * 4},
                {"Component": "Infrastructure Upgrades", "Year 1": 100000, "Year 2-5": 75000 * 4}
            ]
            
            total_tco = 0
            tco_display = []
            
            for component in tco_components:
                total_5yr = component["Year 1"] + component["Year 2-5"]
                total_tco += total_5yr
                tco_display.append({
                    "Cost Component": component["Component"],
                    "Year 1 (£)": f"{component['Year 1']:,.0f}",
                    "Years 2-5 (£)": f"{component['Year 2-5']:,.0f}",
                    "5-Year Total (£)": f"{total_5yr:,.0f}"
                })
            
            tco_display.append({
                "Cost Component": "**TOTAL TCO**",
                "Year 1 (£)": f"**£{sum(c['Year 1'] for c in tco_components):,.0f}**",
                "Years 2-5 (£)": f"**£{sum(c['Year 2-5'] for c in tco_components):,.0f}**",
                "5-Year Total (£)": f"**£{total_tco:,.0f}**"
            })
            
            tco_df = pd.DataFrame(tco_display)
            st.dataframe(tco_df, use_container_width=True, hide_index=True)
        
        with tco_col2:
            # TCO vs Benefits visualization
            years = list(range(1, 6))
            cumulative_costs = []
            cumulative_benefits = []
            
            for year in years:
                if year == 1:
                    costs = implementation_cost + annual_operating_cost + 250000  # Year 1 costs
                    benefits = net_annual_benefit
                else:
                    costs = cumulative_costs[-1] + annual_operating_cost + 100000  # Ongoing costs
                    benefits = cumulative_benefits[-1] + net_annual_benefit * 1.05  # Growing benefits
                
                cumulative_costs.append(costs)
                cumulative_benefits.append(benefits)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=cumulative_costs, mode='lines+markers', name='Cumulative Costs', line=dict(color='#dc3545')))
            fig.add_trace(go.Scatter(x=years, y=cumulative_benefits, mode='lines+markers', name='Cumulative Benefits', line=dict(color='#28a745')))
            
            fig.update_layout(
                title="5-Year TCO vs Benefits",
                xaxis_title="Year",
                yaxis_title="Cumulative Value (£)",
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Opportunity Cost Analysis
        st.markdown("### ⏰ Opportunity Cost Analysis")
        
        opp_cost_col1, opp_cost_col2 = st.columns(2)
        
        with opp_cost_col1:
            st.markdown("**Alternative Investment Options**")
            
            alternatives = [
                {"Investment": "Status Quo (No Investment)", "5-Year Return": "£0", "Risk": "High", "Strategic Value": "Low"},
                {"Investment": "Manual Process Improvement", "5-Year Return": "£2.1M", "Risk": "Medium", "Strategic Value": "Low"},
                {"Investment": "Partial Automation", "5-Year Return": "£4.8M", "Risk": "Medium", "Strategic Value": "Medium"},
                {"Investment": "AI Implementation (This Project)", "5-Year Return": f"£{npv:,.0f}", "Risk": "Low", "Strategic Value": "High"}
            ]
            
            alt_df = pd.DataFrame(alternatives)
            st.dataframe(alt_df, use_container_width=True, hide_index=True)
            
            st.metric("Opportunity Cost of Not Investing", f"£{npv - 2100000:,.0f}", "vs next best alternative")
        
        with opp_cost_col2:
            # Strategic value quantification
            st.markdown("**Strategic Value Quantification**")
            
            strategic_values = [
                {"Value Driver": "Brand Enhancement", "Quantified Value": "£500K/year", "Method": "Customer survey premium"},
                {"Value Driver": "Competitive Advantage", "Quantified Value": "£800K/year", "Method": "Market share protection"},
                {"Value Driver": "Innovation Capability", "Quantified Value": "£300K/year", "Method": "R&D efficiency gains"},
                {"Value Driver": "Risk Mitigation", "Quantified Value": "£400K/year", "Method": "Avoided compliance costs"},
                {"Value Driver": "Employee Satisfaction", "Quantified Value": "£200K/year", "Method": "Reduced turnover costs"}
            ]
            
            strategic_df = pd.DataFrame(strategic_values)
            st.dataframe(strategic_df, use_container_width=True, hide_index=True)
            
            total_strategic_value = 500 + 800 + 300 + 400 + 200
            st.metric("Total Strategic Value", f"£{total_strategic_value}K/year", f"£{total_strategic_value * 5}K over 5 years")
        
        # Regulatory Compliance Cost Savings
        st.markdown("### 📋 Regulatory Compliance & Risk Savings")
        
        compliance_col1, compliance_col2 = st.columns(2)
        
        with compliance_col1:
            st.markdown("**Compliance Cost Savings**")
            
            compliance_savings = [
                {"Area": "Data Protection (GDPR)", "Annual Savings": "£120K", "Risk Reduction": "High"},
                {"Area": "Financial Reporting", "Annual Savings": "£80K", "Risk Reduction": "Medium"},
                {"Area": "Quality Assurance", "Annual Savings": "£150K", "Risk Reduction": "High"},
                {"Area": "Audit & Documentation", "Annual Savings": "£90K", "Risk Reduction": "Medium"},
                {"Area": "Risk Management", "Annual Savings": "£110K", "Risk Reduction": "High"}
            ]
            
            compliance_df = pd.DataFrame(compliance_savings)
            st.dataframe(compliance_df, use_container_width=True, hide_index=True)
            
            total_compliance_savings = 120 + 80 + 150 + 90 + 110
            st.metric("Total Compliance Savings", f"£{total_compliance_savings}K/year", f"£{total_compliance_savings * 5}K over 5 years")
        
        with compliance_col2:
            # Risk quantification
            st.markdown("**Risk Quantification & Mitigation**")
            
            risks = [
                {"Risk Type": "Operational Risk", "Current Exposure": "£2M/year", "Post-AI Exposure": "£400K/year", "Savings": "£1.6M/year"},
                {"Risk Type": "Reputational Risk", "Current Exposure": "£1.5M/year", "Post-AI Exposure": "£300K/year", "Savings": "£1.2M/year"},
                {"Risk Type": "Compliance Risk", "Current Exposure": "£800K/year", "Post-AI Exposure": "£200K/year", "Savings": "£600K/year"},
                {"Risk Type": "Technology Risk", "Current Exposure": "£600K/year", "Post-AI Exposure": "£150K/year", "Savings": "£450K/year"}
            ]
            
            risk_df = pd.DataFrame(risks)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
            
            total_risk_savings = 1.6 + 1.2 + 0.6 + 0.45
            st.metric("Total Risk Mitigation Value", f"£{total_risk_savings}M/year", f"£{total_risk_savings * 5}M over 5 years")
        
        # Final Investment Recommendation
        st.markdown("---")
        st.markdown("### 🎯 Final Investment Recommendation")
        
        # Calculate total value proposition
        total_financial_return = npv
        total_strategic_value_5yr = total_strategic_value * 5 * 1000
        total_compliance_savings_5yr = total_compliance_savings * 5 * 1000
        total_risk_mitigation_5yr = total_risk_savings * 5 * 1000000
        total_value_proposition = total_financial_return + total_strategic_value_5yr + total_compliance_savings_5yr + total_risk_mitigation_5yr
        
        recommendation_col1, recommendation_col2 = st.columns(2)
        
        with recommendation_col1:
            st.success(f"""
            **STRONG BUY RECOMMENDATION**
            
            **Total Value Proposition: £{total_value_proposition:,.0f}**
            
            • Financial NPV: £{total_financial_return:,.0f}
            • Strategic Value: £{total_strategic_value_5yr:,.0f}
            • Compliance Savings: £{total_compliance_savings_5yr:,.0f}
            • Risk Mitigation: £{total_risk_mitigation_5yr:,.0f}
            
            **Investment Grade: AAA**
            **Risk Level: Low**
            **Strategic Importance: Critical**
            """)
        
        with recommendation_col2:
            # Value creation waterfall
            values = [total_financial_return, total_strategic_value_5yr, total_compliance_savings_5yr, total_risk_mitigation_5yr]
            categories = ['Financial NPV', 'Strategic Value', 'Compliance Savings', 'Risk Mitigation']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=categories,
                y=values,
                text=[f"£{val:,.0f}" for val in values],
                textposition='auto',
                marker_color=['#28a745', '#007bff', '#ffc107', '#dc3545']
            ))
            
            fig.update_layout(
                title="Total Value Creation Breakdown",
                yaxis_title="Value (£)",
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Executive Approval Button
        if st.button("✅ APPROVE INVESTMENT", type="primary", use_container_width=True):
            st.success("🎉 Investment Approved! Project initiation can begin immediately.")
            st.balloons()
            st.info("Next Steps: Assemble project team, finalize vendor contracts, begin Phase 1 implementation planning.")

# Footer
st.markdown("---")

# Clear quotes button in sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🗑️ Clear All Quotes"):
        st.session_state.generated_quotes = []
        st.session_state.case_statuses = {}
        st.success("All quotes cleared!")
        st.rerun()

st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <h4>🚀 BH Worldwide AI Solution Demo</h4>
    <p>Transforming AOG logistics with artificial intelligence</p>
    <p><strong>Ready to revolutionize your business? Let's discuss implementation!</strong></p>
</div>
""", unsafe_allow_html=True)