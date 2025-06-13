"""
Generate realistic mock research data for testing descriptive statistics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# African countries and regions for realistic data
AFRICAN_REGIONS = {
    "East Africa": ["Kenya", "Tanzania", "Uganda", "Ethiopia", "Rwanda"],
    "West Africa": ["Nigeria", "Ghana", "Senegal", "Mali", "Burkina Faso"],
    "Southern Africa": ["South Africa", "Zimbabwe", "Zambia", "Botswana", "Mozambique"],
    "North Africa": ["Egypt", "Morocco", "Tunisia", "Algeria", "Libya"],
    "Central Africa": ["DRC", "Cameroon", "Chad", "CAR", "Gabon"]
}

# Research locations with coordinates
RESEARCH_LOCATIONS = {
    "Kibera, Nairobi": (-1.3133, 36.7846),
    "Soweto, Johannesburg": (-26.2309, 27.8589),
    "Makoko, Lagos": (6.4969, 3.3903),
    "Khayelitsha, Cape Town": (-34.0440, 18.6739),
    "Mathare, Nairobi": (-1.2620, 36.8588),
    "Mukuru, Nairobi": (-1.3147, 36.8791),
    "Accra Slums": (5.5600, -0.2057),
    "Cairo Slums": (30.0626, 31.2497),
    "Dar es Salaam Slums": (-6.8160, 39.2803),
    "Kampala Slums": (0.3476, 32.5825)
}

def generate_rural_health_survey_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate mock rural health survey data.
    
    Args:
        n_samples: Number of survey responses to generate
        
    Returns:
        DataFrame with mock survey data
    """
    data = []
    
    # Generate temporal distribution - surveys collected over 6 months
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 6, 30)
    
    for i in range(n_samples):
        # Basic demographics
        age = int(np.random.lognormal(3.4, 0.4))  # Skewed age distribution
        age = max(18, min(age, 85))  # Clamp to reasonable range
        
        gender = np.random.choice(['Male', 'Female'], p=[0.48, 0.52])
        
        # Education - correlated with age
        if age < 30:
            education = np.random.choice(
                ['None', 'Primary', 'Secondary', 'Tertiary'],
                p=[0.05, 0.25, 0.50, 0.20]
            )
        else:
            education = np.random.choice(
                ['None', 'Primary', 'Secondary', 'Tertiary'],
                p=[0.30, 0.40, 0.25, 0.05]
            )
        
        # Location
        location_name = random.choice(list(RESEARCH_LOCATIONS.keys()))
        lat, lon = RESEARCH_LOCATIONS[location_name]
        # Add some noise to coordinates
        lat += np.random.normal(0, 0.01)
        lon += np.random.normal(0, 0.01)
        
        # Collection date - more responses on weekdays
        days_since_start = random.randint(0, (end_date - start_date).days)
        collection_date = start_date + timedelta(days=days_since_start)
        if collection_date.weekday() >= 5:  # Weekend
            if random.random() > 0.3:  # 70% chance to skip weekend
                continue
        
        # Health metrics
        # BMI - normal distribution with some outliers
        if random.random() < 0.05:  # 5% extreme values
            bmi = random.choice([random.uniform(14, 18), random.uniform(35, 45)])
        else:
            bmi = np.random.normal(24, 4)
            bmi = max(16, min(bmi, 40))
        
        # Blood pressure - correlated with age and BMI
        systolic_base = 90 + age * 0.5 + bmi * 0.8
        systolic = int(np.random.normal(systolic_base, 10))
        diastolic = int(systolic * np.random.uniform(0.6, 0.7))
        
        # Health score (0-100) - multimodal distribution
        if education == 'Tertiary':
            health_score = np.random.normal(75, 10)
        elif education == 'None':
            health_score = np.random.normal(45, 15)
        else:
            health_score = np.random.normal(60, 12)
        health_score = max(0, min(health_score, 100))
        
        # Income - lognormal with missing data
        if random.random() < 0.15:  # 15% missing income data
            monthly_income = np.nan
        else:
            income_base = {'None': 50, 'Primary': 100, 'Secondary': 200, 'Tertiary': 500}
            monthly_income = np.random.lognormal(
                np.log(income_base.get(education, 100)), 0.8
            )
        
        # Disease prevalence
        has_malaria = random.random() < 0.25  # 25% prevalence
        has_diabetes = random.random() < (0.05 + age/1000)  # Age-dependent
        has_hypertension = systolic > 140 or diastolic > 90
        
        # Water access
        water_access = np.random.choice(
            ['Piped', 'Well', 'River', 'None'],
            p=[0.15, 0.40, 0.35, 0.10]
        )
        
        # Distance to health facility (km) - exponential distribution
        distance_to_clinic = np.random.exponential(5)
        distance_to_clinic = min(distance_to_clinic, 50)  # Cap at 50km
        
        # Survey metadata
        survey_duration_minutes = np.random.normal(15, 3)
        survey_duration_minutes = max(5, min(survey_duration_minutes, 30))
        
        # Missing data patterns
        # If no education info, likely to miss other data too
        if education == 'None' and random.random() < 0.3:
            water_access = np.nan
            
        # Add some completely missing responses (incomplete surveys)
        if random.random() < 0.02:  # 2% incomplete
            health_score = np.nan
            has_malaria = np.nan
            has_diabetes = np.nan
        
        # Survey weights (for sampling design)
        # Rural areas get higher weights
        if 'Slums' not in location_name:
            survey_weight = 1.5
        else:
            survey_weight = 1.0
            
        record = {
            'respondent_id': f'R{i+1:04d}',
            'age': age,
            'gender': gender,
            'education_level': education,
            'location_name': location_name,
            'latitude': lat,
            'longitude': lon,
            'collection_date': collection_date,
            'collection_time': collection_date + timedelta(
                hours=random.randint(6, 18),
                minutes=random.randint(0, 59)
            ),
            'bmi': round(bmi, 1),
            'systolic_bp': systolic,
            'diastolic_bp': diastolic,
            'health_score': round(health_score, 1),
            'monthly_income_usd': round(monthly_income, 2) if not pd.isna(monthly_income) else np.nan,
            'has_malaria': has_malaria,
            'has_diabetes': has_diabetes,
            'has_hypertension': has_hypertension,
            'water_access': water_access,
            'distance_to_clinic_km': round(distance_to_clinic, 1),
            'survey_duration_minutes': round(survey_duration_minutes, 1),
            'survey_weight': survey_weight,
            'data_collector_id': f'DC{random.randint(1, 10):02d}'
        }
        
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # Add some data quality issues
    # Duplicate entries (same person surveyed twice)
    if len(df) > 10:
        duplicate_indices = random.sample(range(len(df)), k=min(5, len(df)//100))
        for idx in duplicate_indices:
            duplicate = df.iloc[idx].copy()
            duplicate['collection_date'] += timedelta(days=random.randint(1, 7))
            duplicate['respondent_id'] = duplicate['respondent_id'] + '_dup'
            df = pd.concat([df, pd.DataFrame([duplicate])], ignore_index=True)
    
    return df

def generate_education_study_data(n_students: int = 500) -> pd.DataFrame:
    """
    Generate mock education study data.
    
    Args:
        n_students: Number of students to generate
        
    Returns:
        DataFrame with mock education data
    """
    data = []
    
    # Schools in different regions
    schools = [
        ("Nairobi Primary", "Kenya", "Urban", (-1.2921, 36.8219)),
        ("Lagos Secondary", "Nigeria", "Urban", (6.5244, 3.3792)),
        ("Cape Town High", "South Africa", "Urban", (-33.9249, 18.4241)),
        ("Rural Uganda School", "Uganda", "Rural", (0.3476, 32.5825)),
        ("Accra Academy", "Ghana", "Urban", (5.6037, -0.1870))
    ]
    
    for i in range(n_students):
        school = random.choice(schools)
        school_name, country, area_type, (lat, lon) = school
        
        # Student demographics
        age = random.randint(10, 18)
        gender = random.choice(['Male', 'Female'])
        grade = min(age - 5, 12)  # Approximate grade from age
        
        # Academic performance - normal distribution with school effects
        if "Primary" in school_name:
            base_score = 65
        elif "Academy" in school_name:
            base_score = 75
        else:
            base_score = 70
            
        math_score = np.random.normal(base_score, 15)
        math_score = max(0, min(math_score, 100))
        
        reading_score = np.random.normal(base_score + 5, 12)
        reading_score = max(0, min(reading_score, 100))
        
        science_score = np.random.normal(base_score - 2, 18)
        science_score = max(0, min(science_score, 100))
        
        # Attendance - beta distribution
        attendance_rate = np.random.beta(9, 2) * 100  # Skewed towards high attendance
        
        # Socioeconomic factors
        if area_type == "Rural":
            has_electricity = random.random() < 0.3
            has_internet = random.random() < 0.1
            books_at_home = random.randint(0, 20)
        else:
            has_electricity = random.random() < 0.9
            has_internet = random.random() < 0.6
            books_at_home = random.randint(5, 100)
        
        # Parent education
        parent_education = random.choice(['None', 'Primary', 'Secondary', 'Tertiary'])
        
        # Class size
        class_size = random.randint(20, 60) if area_type == "Urban" else random.randint(30, 80)
        
        # Missing data - some students don't complete all tests
        if random.random() < 0.05:
            science_score = np.nan
        if random.random() < 0.02:
            math_score = np.nan
            
        record = {
            'student_id': f'S{i+1:04d}',
            'school_name': school_name,
            'country': country,
            'area_type': area_type,
            'latitude': lat + np.random.normal(0, 0.005),
            'longitude': lon + np.random.normal(0, 0.005),
            'age': age,
            'gender': gender,
            'grade': grade,
            'math_score': round(math_score, 1) if not pd.isna(math_score) else np.nan,
            'reading_score': round(reading_score, 1),
            'science_score': round(science_score, 1) if not pd.isna(science_score) else np.nan,
            'attendance_rate': round(attendance_rate, 1),
            'has_electricity': has_electricity,
            'has_internet': has_internet,
            'books_at_home': books_at_home,
            'parent_education': parent_education,
            'class_size': class_size,
            'assessment_date': datetime(2024, 3, 1) + timedelta(days=random.randint(0, 90))
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def generate_agricultural_survey_data(n_farmers: int = 300) -> pd.DataFrame:
    """
    Generate mock agricultural survey data.
    
    Args:
        n_farmers: Number of farmers to generate
        
    Returns:
        DataFrame with mock agricultural data
    """
    data = []
    
    crops = ['Maize', 'Rice', 'Cassava', 'Wheat', 'Sorghum', 'Millet', 'Beans', 'Groundnuts']
    regions = ['Northern', 'Southern', 'Eastern', 'Western', 'Central']
    
    for i in range(n_farmers):
        # Farm characteristics
        farm_size_hectares = np.random.lognormal(1.5, 0.8)
        farm_size_hectares = max(0.1, min(farm_size_hectares, 50))
        
        region = random.choice(regions)
        
        # Crop selection based on region
        if region == 'Northern':
            primary_crop = random.choice(['Millet', 'Sorghum', 'Groundnuts'])
        elif region == 'Southern':
            primary_crop = random.choice(['Maize', 'Wheat'])
        else:
            primary_crop = random.choice(crops)
        
        # Yield - affected by various factors
        base_yield = {'Maize': 2000, 'Rice': 3000, 'Cassava': 15000, 
                     'Wheat': 2500, 'Sorghum': 1200, 'Millet': 900,
                     'Beans': 800, 'Groundnuts': 1000}
        
        # Add variability
        yield_kg_per_hectare = np.random.normal(base_yield[primary_crop], base_yield[primary_crop] * 0.3)
        yield_kg_per_hectare = max(100, yield_kg_per_hectare)
        
        # Farming practices
        uses_fertilizer = random.random() < 0.6
        uses_irrigation = random.random() < 0.3
        uses_improved_seeds = random.random() < 0.4
        
        # If using modern practices, increase yield
        if uses_fertilizer:
            yield_kg_per_hectare *= 1.3
        if uses_irrigation:
            yield_kg_per_hectare *= 1.2
        if uses_improved_seeds:
            yield_kg_per_hectare *= 1.15
            
        # Income and expenses
        income_per_season = yield_kg_per_hectare * farm_size_hectares * random.uniform(0.3, 0.8)
        expenses = income_per_season * random.uniform(0.4, 0.7)
        
        # Demographics
        farmer_age = random.randint(25, 70)
        years_farming = min(farmer_age - 18, random.randint(5, 40))
        household_size = random.randint(2, 12)
        
        # Technology adoption
        has_mobile_phone = random.random() < 0.8
        uses_mobile_money = has_mobile_phone and random.random() < 0.6
        
        # Climate impact
        experienced_drought = random.random() < 0.4
        experienced_flood = random.random() < 0.2
        
        # Missing data - some farmers reluctant to share income
        if random.random() < 0.2:
            income_per_season = np.nan
            expenses = np.nan
            
        record = {
            'farmer_id': f'F{i+1:04d}',
            'region': region,
            'farmer_age': farmer_age,
            'years_farming': years_farming,
            'household_size': household_size,
            'farm_size_hectares': round(farm_size_hectares, 2),
            'primary_crop': primary_crop,
            'yield_kg_per_hectare': round(yield_kg_per_hectare, 0),
            'uses_fertilizer': uses_fertilizer,
            'uses_irrigation': uses_irrigation,
            'uses_improved_seeds': uses_improved_seeds,
            'income_per_season_usd': round(income_per_season, 2) if not pd.isna(income_per_season) else np.nan,
            'expenses_usd': round(expenses, 2) if not pd.isna(expenses) else np.nan,
            'has_mobile_phone': has_mobile_phone,
            'uses_mobile_money': uses_mobile_money,
            'experienced_drought': experienced_drought,
            'experienced_flood': experienced_flood,
            'survey_date': datetime(2024, 4, 1) + timedelta(days=random.randint(0, 60))
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
                df.loc[idx, col] = df[col].mean() + 5 * df[col].std()
            else:
                # Extremely low value
                df.loc[idx, col] = df[col].mean() - 5 * df[col].std()
        
        # Add some data entry errors
        if 'age' in df.columns:
            # Impossible ages
            error_indices = random.sample(range(len(df)), k=min(3, n_errors))
            for idx in error_indices:
                df.loc[idx, 'age'] = random.choice([0, 150, 999])
    
    return df

def generate_all_datasets() -> Dict[str, pd.DataFrame]:
    """
    Generate all mock datasets for testing.
    
    Returns:
        Dictionary of DataFrames
    """
    print("Generating mock datasets...")
    
    datasets = {
        'rural_health': generate_rural_health_survey_data(1000),
        'education': generate_education_study_data(500),
        'agriculture': generate_agricultural_survey_data(300)
    }
    
    # Add some data quality issues
    for name, df in datasets.items():
        datasets[name] = add_data_quality_issues(df, error_rate=0.02)
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