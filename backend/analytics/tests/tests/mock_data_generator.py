"""
Generate realistic mock research data for commodity value chain analysis in African countries.
Focus: Trade, sustainability, climate impact, and traceability research.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import uuid

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# African countries and their main commodities for research
COMMODITY_COUNTRIES = {
    "Ghana": {
        "commodities": ["Cocoa", "Maize", "Palm Oil"],
        "major_regions": ["Ashanti", "Eastern", "Western", "Brong-Ahafo"],
        "coordinates": (7.9465, -1.0232),
        "main_exports": ["Cocoa", "Palm Oil"],
        "trade_partners": ["Netherlands", "Germany", "Belgium", "USA"]
    },
    "Nigeria": {
        "commodities": ["Groundnut", "Maize", "Palm Oil", "Fish"],
        "major_regions": ["Kano", "Kaduna", "Lagos", "Rivers"],
        "coordinates": (9.0820, 8.6753),
        "main_exports": ["Palm Oil", "Fish", "Groundnut"],
        "trade_partners": ["Spain", "Netherlands", "France", "UK"]
    },
    "South Africa": {
        "commodities": ["Honey", "Maize"],
        "major_regions": ["Western Cape", "Eastern Cape", "KwaZulu-Natal", "Gauteng"],
        "coordinates": (-30.5595, 22.9375),
        "main_exports": ["Honey", "Maize"],
        "trade_partners": ["Germany", "UK", "Netherlands", "France"]
    },
    "Kenya": {
        "commodities": ["Maize", "Groundnut"],
        "major_regions": ["Central", "Rift Valley", "Eastern", "Nyanza"],
        "coordinates": (-0.0236, 37.9062),
        "main_exports": ["Maize", "Groundnut"],
        "trade_partners": ["Uganda", "Tanzania", "Netherlands", "Germany"]
    },
    "Burkina Faso": {
        "commodities": ["Maize", "Groundnut"],
        "major_regions": ["Centre", "Hauts-Bassins", "Cascades", "Sud-Ouest"],
        "coordinates": (12.2383, -1.5616),
        "main_exports": ["Groundnut", "Maize"],
        "trade_partners": ["Côte d'Ivoire", "Ghana", "France", "Netherlands"]
    },
    "Senegal": {
        "commodities": ["Maize", "Palm Oil", "Groundnut"],
        "major_regions": ["Thiès", "Kaolack", "Fatick", "Diourbel"],
        "coordinates": (14.4974, -14.4524),
        "main_exports": ["Groundnut", "Palm Oil"],
        "trade_partners": ["France", "Mali", "India", "Netherlands"]
    }
}

# Value chain stages
VALUE_CHAIN_STAGES = [
    "Production", "Collection", "Processing", "Wholesale", "Export", "Retail"
]

# Sustainability certifications
CERTIFICATIONS = [
    "Organic", "Fair Trade", "Rainforest Alliance", "UTZ", "RSPO", "None"
]

def generate_commodity_production_data(n_producers: int = 1000) -> pd.DataFrame:
    """
    Generate mock commodity production data across African countries.
    
    Args:
        n_producers: Number of producers to generate
        
    Returns:
        DataFrame with production data
    """
    data = []
    
    for i in range(n_producers):
        # Select country and commodity
        country = random.choice(list(COMMODITY_COUNTRIES.keys()))
        country_info = COMMODITY_COUNTRIES[country]
        commodity = random.choice(country_info["commodities"])
        region = random.choice(country_info["major_regions"])
        
        # Producer characteristics
        producer_id = f"PROD_{country[:2].upper()}_{i+1:04d}"
        producer_name = f"{region} {commodity} Producer {i+1}"
        
        # Location with noise around country center
        base_lat, base_lon = country_info["coordinates"]
        latitude = base_lat + np.random.normal(0, 2.0)
        longitude = base_lon + np.random.normal(0, 2.0)
        
        # Production metrics
        if commodity == "Cocoa":
            farm_size_hectares = np.random.lognormal(0.5, 0.8)  # Small farms
            yield_per_hectare = np.random.normal(450, 150)  # kg/hectare
            price_per_kg_usd = np.random.normal(2.5, 0.5)
        elif commodity == "Maize":
            farm_size_hectares = np.random.lognormal(1.0, 1.0)
            yield_per_hectare = np.random.normal(2000, 600)
            price_per_kg_usd = np.random.normal(0.35, 0.1)
        elif commodity == "Palm Oil":
            farm_size_hectares = np.random.lognormal(1.5, 0.8)
            yield_per_hectare = np.random.normal(3500, 800)
            price_per_kg_usd = np.random.normal(0.8, 0.2)
        elif commodity == "Groundnut":
            farm_size_hectares = np.random.lognormal(0.8, 0.7)
            yield_per_hectare = np.random.normal(1200, 300)
            price_per_kg_usd = np.random.normal(1.2, 0.3)
        elif commodity == "Fish":
            farm_size_hectares = np.random.lognormal(0.3, 0.5)  # Pond size
            yield_per_hectare = np.random.normal(8000, 2000)  # kg/hectare
            price_per_kg_usd = np.random.normal(3.5, 0.8)
        elif commodity == "Honey":
            farm_size_hectares = np.random.lognormal(0.1, 0.3)  # Beehive area
            yield_per_hectare = np.random.normal(25, 10)  # kg/hectare
            price_per_kg_usd = np.random.normal(8.0, 2.0)
        
        # Ensure positive values
        farm_size_hectares = max(0.1, farm_size_hectares)
        yield_per_hectare = max(50, yield_per_hectare)
        price_per_kg_usd = max(0.1, price_per_kg_usd)
        
        total_production_kg = farm_size_hectares * yield_per_hectare
        gross_revenue_usd = total_production_kg * price_per_kg_usd
        
        # Costs and sustainability
        production_costs_usd = gross_revenue_usd * np.random.uniform(0.4, 0.7)
        net_income_usd = gross_revenue_usd - production_costs_usd
        
        # Sustainability metrics
        has_certification = random.choice([True, False])
        certification_type = random.choice(CERTIFICATIONS) if has_certification else "None"
        
        # Environmental impact
        water_usage_liters_per_kg = np.random.normal(500, 200) if commodity != "Fish" else 2000
        carbon_footprint_kg_co2_per_kg = np.random.normal(2.5, 1.0)
        pesticide_use_kg_per_hectare = np.random.normal(15, 8) if certification_type != "Organic" else 0
        
        # Climate resilience
        climate_adaptation_score = np.random.uniform(1, 10)  # 1-10 scale
        drought_risk_level = random.choice(["Low", "Medium", "High"])
        flood_risk_level = random.choice(["Low", "Medium", "High"])
        
        # Traceability
        has_traceability_system = random.choice([True, False])
        traceability_id = str(uuid.uuid4())[:8] if has_traceability_system else None
        
        # Cooperative membership
        is_cooperative_member = random.choice([True, False])
        cooperative_name = f"{region} {commodity} Cooperative" if is_cooperative_member else None
        
        # Collection date
        collection_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        
        # Missing data patterns
        if random.random() < 0.1:  # 10% missing income data
            net_income_usd = np.nan
            production_costs_usd = np.nan
        
        if random.random() < 0.05:  # 5% missing environmental data
            carbon_footprint_kg_co2_per_kg = np.nan
            water_usage_liters_per_kg = np.nan
        
        record = {
            'producer_id': producer_id,
            'country': country,
            'region': region,
            'commodity': commodity,
            'producer_name': producer_name,
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6),
            'farm_size_hectares': round(farm_size_hectares, 2),
            'yield_per_hectare_kg': round(yield_per_hectare, 1),
            'total_production_kg': round(total_production_kg, 1),
            'price_per_kg_usd': round(price_per_kg_usd, 2),
            'gross_revenue_usd': round(gross_revenue_usd, 2),
            'production_costs_usd': round(production_costs_usd, 2) if not pd.isna(production_costs_usd) else np.nan,
            'net_income_usd': round(net_income_usd, 2) if not pd.isna(net_income_usd) else np.nan,
            'has_certification': has_certification,
            'certification_type': certification_type,
            'water_usage_liters_per_kg': round(water_usage_liters_per_kg, 1) if not pd.isna(water_usage_liters_per_kg) else np.nan,
            'carbon_footprint_kg_co2_per_kg': round(carbon_footprint_kg_co2_per_kg, 2) if not pd.isna(carbon_footprint_kg_co2_per_kg) else np.nan,
            'pesticide_use_kg_per_hectare': round(pesticide_use_kg_per_hectare, 1),
            'climate_adaptation_score': round(climate_adaptation_score, 1),
            'drought_risk_level': drought_risk_level,
            'flood_risk_level': flood_risk_level,
            'has_traceability_system': has_traceability_system,
            'traceability_id': traceability_id,
            'is_cooperative_member': is_cooperative_member,
            'cooperative_name': cooperative_name,
            'collection_date': collection_date
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def generate_trade_flow_data(n_trades: int = 800) -> pd.DataFrame:
    """
    Generate mock trade flow data between African countries and to Europe.
    
    Args:
        n_trades: Number of trade transactions to generate
        
    Returns:
        DataFrame with trade flow data
    """
    data = []
    
    for i in range(n_trades):
        # Origin country
        origin_country = random.choice(list(COMMODITY_COUNTRIES.keys()))
        origin_info = COMMODITY_COUNTRIES[origin_country]
        commodity = random.choice(origin_info["commodities"])
        
        # Destination - either within Africa or to Europe
        if random.random() < 0.6:  # 60% intra-Africa trade
            destination_country = random.choice([c for c in COMMODITY_COUNTRIES.keys() if c != origin_country])
            trade_type = "Intra-Africa"
        else:  # 40% Africa-Europe trade
            destination_country = random.choice(origin_info["trade_partners"])
            trade_type = "Africa-Europe"
        
        # Trade transaction details
        trade_id = f"TRADE_{i+1:06d}"
        quantity_kg = np.random.lognormal(8, 2)  # Large shipments
        quantity_kg = max(1000, quantity_kg)  # Minimum 1 ton
        
        # Price varies by commodity and destination
        base_prices = {
            "Cocoa": 3.0, "Maize": 0.4, "Palm Oil": 0.9,
            "Groundnut": 1.4, "Fish": 4.0, "Honey": 9.0
        }
        
        price_per_kg_usd = base_prices[commodity]
        
        # Premium for European exports
        if trade_type == "Africa-Europe":
            price_per_kg_usd *= np.random.uniform(1.2, 1.8)
        
        # Premium for certified products
        is_certified = random.choice([True, False])
        if is_certified:
            price_per_kg_usd *= np.random.uniform(1.1, 1.4)
            certification_type = random.choice(["Organic", "Fair Trade", "Rainforest Alliance"])
        else:
            certification_type = "None"
        
        total_value_usd = quantity_kg * price_per_kg_usd
        
        # Logistics and costs
        transportation_cost_usd = total_value_usd * np.random.uniform(0.08, 0.15)
        customs_fees_usd = total_value_usd * np.random.uniform(0.02, 0.05)
        insurance_cost_usd = total_value_usd * np.random.uniform(0.01, 0.03)
        
        # Transportation method
        if trade_type == "Intra-Africa":
            transport_method = random.choice(["Road", "Rail", "River"])
            transport_distance_km = np.random.uniform(500, 3000)
        else:
            transport_method = random.choice(["Sea", "Air"])
            transport_distance_km = np.random.uniform(5000, 12000)
        
        # Quality and traceability
        quality_grade = random.choice(["A", "B", "C"])
        has_traceability = random.choice([True, False])
        traceability_code = f"TR_{i+1:08d}" if has_traceability else None
        
        # Sustainability metrics
        carbon_footprint_transport_kg = transport_distance_km * 0.12  # kg CO2 per km
        sustainable_packaging = random.choice([True, False])
        
        # Time metrics
        trade_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        transit_time_days = random.randint(3, 30)
        delivery_date = trade_date + timedelta(days=transit_time_days)
        
        # Value chain stage
        stage_from = random.choice(["Production", "Processing", "Wholesale"])
        stage_to = random.choice(["Processing", "Wholesale", "Export", "Retail"])
        
        # Payment terms
        payment_terms = random.choice(["Cash", "30 days", "60 days", "90 days"])
        
        # Missing data
        if random.random() < 0.08:  # 8% missing cost data
            transportation_cost_usd = np.nan
            customs_fees_usd = np.nan
        
        record = {
            'trade_id': trade_id,
            'origin_country': origin_country,
            'destination_country': destination_country,
            'commodity': commodity,
            'trade_type': trade_type,
            'quantity_kg': round(quantity_kg, 1),
            'price_per_kg_usd': round(price_per_kg_usd, 2),
            'total_value_usd': round(total_value_usd, 2),
            'is_certified': is_certified,
            'certification_type': certification_type,
            'quality_grade': quality_grade,
            'transportation_cost_usd': round(transportation_cost_usd, 2) if not pd.isna(transportation_cost_usd) else np.nan,
            'customs_fees_usd': round(customs_fees_usd, 2) if not pd.isna(customs_fees_usd) else np.nan,
            'insurance_cost_usd': round(insurance_cost_usd, 2),
            'transport_method': transport_method,
            'transport_distance_km': round(transport_distance_km, 1),
            'carbon_footprint_transport_kg': round(carbon_footprint_transport_kg, 2),
            'sustainable_packaging': sustainable_packaging,
            'has_traceability': has_traceability,
            'traceability_code': traceability_code,
            'stage_from': stage_from,
            'stage_to': stage_to,
            'payment_terms': payment_terms,
            'trade_date': trade_date,
            'delivery_date': delivery_date,
            'transit_time_days': transit_time_days
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def generate_value_chain_participant_data(n_participants: int = 600) -> pd.DataFrame:
    """
    Generate mock value chain participant data.
    
    Args:
        n_participants: Number of participants to generate
        
    Returns:
        DataFrame with value chain participant data
    """
    data = []
    
    for i in range(n_participants):
        # Participant details
        participant_id = f"VC_{i+1:05d}"
        country = random.choice(list(COMMODITY_COUNTRIES.keys()))
        country_info = COMMODITY_COUNTRIES[country]
        commodity = random.choice(country_info["commodities"])
        
        # Value chain stage
        stage = random.choice(VALUE_CHAIN_STAGES)
        
        # Business characteristics
        if stage == "Production":
            business_type = "Farm"
            business_size = random.choice(["Small", "Medium", "Large"])
            employees = random.randint(1, 50)
        elif stage == "Processing":
            business_type = "Processing Plant"
            business_size = random.choice(["Small", "Medium", "Large"])
            employees = random.randint(5, 200)
        else:
            business_type = "Trading Company"
            business_size = random.choice(["Small", "Medium", "Large"])
            employees = random.randint(2, 100)
        
        # Location
        region = random.choice(country_info["major_regions"])
        base_lat, base_lon = country_info["coordinates"]
        latitude = base_lat + np.random.normal(0, 1.5)
        longitude = base_lon + np.random.normal(0, 1.5)
        
        # Financial metrics
        if business_size == "Small":
            annual_revenue_usd = np.random.lognormal(8, 1)
        elif business_size == "Medium":
            annual_revenue_usd = np.random.lognormal(10, 1)
        else:
            annual_revenue_usd = np.random.lognormal(12, 1)
        
        annual_costs_usd = annual_revenue_usd * np.random.uniform(0.6, 0.8)
        profit_margin = (annual_revenue_usd - annual_costs_usd) / annual_revenue_usd
        
        # Capacity and volume
        if stage == "Production":
            annual_capacity_kg = np.random.lognormal(7, 1.5)
        else:
            annual_capacity_kg = np.random.lognormal(9, 1.5)
        
        capacity_utilization = np.random.uniform(0.5, 0.95)
        actual_volume_kg = annual_capacity_kg * capacity_utilization
        
        # Technology and innovation
        technology_level = random.choice(["Basic", "Intermediate", "Advanced"])
        digital_adoption_score = np.random.uniform(1, 10)
        
        # Sustainability practices
        sustainability_score = np.random.uniform(1, 10)
        environmental_certification = random.choice([True, False])
        waste_reduction_practices = random.choice([True, False])
        renewable_energy_use = random.choice([True, False])
        
        # Supply chain relationships
        num_suppliers = random.randint(1, 20)
        num_buyers = random.randint(1, 15)
        avg_contract_length_months = random.randint(3, 36)
        
        # Challenges and risks
        main_challenges = random.choice([
            "Access to Finance", "Market Access", "Climate Change",
            "Infrastructure", "Regulation", "Competition"
        ])
        
        risk_level = random.choice(["Low", "Medium", "High"])
        
        # Traceability and compliance
        traceability_system = random.choice([True, False])
        compliance_certifications = random.randint(0, 5)
        
        # Missing data patterns
        if random.random() < 0.12:  # 12% missing financial data
            annual_revenue_usd = np.nan
            annual_costs_usd = np.nan
            profit_margin = np.nan
        
        record = {
            'participant_id': participant_id,
            'country': country,
            'region': region,
            'commodity': commodity,
            'value_chain_stage': stage,
            'business_type': business_type,
            'business_size': business_size,
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6),
            'employees': employees,
            'annual_revenue_usd': round(annual_revenue_usd, 2) if not pd.isna(annual_revenue_usd) else np.nan,
            'annual_costs_usd': round(annual_costs_usd, 2) if not pd.isna(annual_costs_usd) else np.nan,
            'profit_margin': round(profit_margin, 3) if not pd.isna(profit_margin) else np.nan,
            'annual_capacity_kg': round(annual_capacity_kg, 1),
            'capacity_utilization': round(capacity_utilization, 2),
            'actual_volume_kg': round(actual_volume_kg, 1),
            'technology_level': technology_level,
            'digital_adoption_score': round(digital_adoption_score, 1),
            'sustainability_score': round(sustainability_score, 1),
            'environmental_certification': environmental_certification,
            'waste_reduction_practices': waste_reduction_practices,
            'renewable_energy_use': renewable_energy_use,
            'num_suppliers': num_suppliers,
            'num_buyers': num_buyers,
            'avg_contract_length_months': avg_contract_length_months,
            'main_challenges': main_challenges,
            'risk_level': risk_level,
            'traceability_system': traceability_system,
            'compliance_certifications': compliance_certifications,
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def add_data_quality_issues(df: pd.DataFrame, 
                           error_rate: float = 0.02) -> pd.DataFrame:
    """
    Add realistic data quality issues to a dataset.
    
    Args:
        df: Original DataFrame
        error_rate: Proportion of errors to introduce
        
    Returns:
        DataFrame with data quality issues
    """
    df = df.copy()
    n_errors = int(len(df) * error_rate)
    
    if n_errors > 0:
        # Add some outliers to numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for _ in range(n_errors):
            col = random.choice(numeric_cols.tolist())
            idx = random.randint(0, len(df) - 1)
            
            # Create outlier
            if random.random() < 0.5:
                # Extremely high value
                outlier_value = df[col].mean() + 5 * df[col].std()
            else:
                # Extremely low value
                outlier_value = df[col].mean() - 5 * df[col].std()
            
            # Convert to appropriate type to avoid dtype warnings
            if df[col].dtype == 'int64':
                outlier_value = int(outlier_value)
            elif df[col].dtype == 'float64':
                outlier_value = float(outlier_value)
            
            df.loc[idx, col] = outlier_value
        
        # Add some data entry errors
        if 'age' in df.columns:
            # Impossible ages
            error_indices = random.sample(range(len(df)), k=min(3, n_errors))
            for idx in error_indices:
                df.loc[idx, 'age'] = random.choice([0, 150, 999])
    
    return df

def generate_all_datasets() -> Dict[str, pd.DataFrame]:
    """
    Generate all mock datasets for commodity value chain research.
    
    Returns:
        Dictionary of DataFrames
    """
    print("Generating mock commodity research datasets...")
    
    datasets = {
        'commodity_production': generate_commodity_production_data(1000),
        'trade_flows': generate_trade_flow_data(800),
        'value_chain_participants': generate_value_chain_participant_data(600)
    }
    
    # Add some data quality issues
    for name, df in datasets.items():
        datasets[name] = add_data_quality_issues(df, error_rate=0.01)
        print(f"Generated {name} dataset with {len(df)} records")
    
    return datasets

if __name__ == "__main__":
    # Generate and save datasets
    datasets = generate_all_datasets()
    
    for name, df in datasets.items():
        filename = f"mock_{name}_data.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {filename}")
    
    # Display basic info
    print("\nDataset Summary:")
    for name, df in datasets.items():
        print(f"\n{name.upper()}:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {', '.join(df.columns[:5])}...")
        print(f"  Missing data: {df.isna().sum().sum()} cells")
        
        # Show commodity distribution
        if 'commodity' in df.columns:
            print(f"  Commodity distribution: {df['commodity'].value_counts().to_dict()}")
        
        # Show country distribution
        if 'country' in df.columns:
            print(f"  Country distribution: {df['country'].value_counts().to_dict()}")