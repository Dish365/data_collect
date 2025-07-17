"""
Shared utilities for analytics functionality.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class AnalyticsUtils:
    """Utility class for analytics operations"""
    
    @staticmethod
    def format_api_response(status: str, data: Any = None, message: str = None) -> Dict[str, Any]:
        """Format API response"""
        response = {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
            
        return response
    
    @staticmethod
    def handle_analysis_error(error: Exception, operation: str) -> Dict[str, Any]:
        """Handle analysis errors"""
        return AnalyticsUtils.format_api_response(
            'error',
            None,
            f"Error during {operation}: {str(error)}"
        )
    
    @staticmethod
    async def get_project_data(project_id: str) -> pd.DataFrame:
        """Get project data as pandas DataFrame"""
        from core.database import get_project_data
        
        data = await get_project_data(project_id)
        if not data:
            return pd.DataFrame()
        
        return pd.DataFrame(data)
    
    @staticmethod
    async def get_project_stats(project_id: str) -> Dict[str, Any]:
        """Get project statistics"""
        from core.database import get_project_stats
        
        return await get_project_stats(project_id)
    
    @staticmethod
    def get_django_db_connection():
        """Get Django database connection"""
        from core.database import get_django_db_connection
        
        return get_django_db_connection()
    
    @staticmethod
    def analyze_data_characteristics(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data characteristics"""
        if df.empty:
            return {
                'sample_size': 0,
                'variable_count': 0,
                'completeness_score': 0,
                'data_types': {},
                'numeric_variables': [],
                'text_variables': [],
                'datetime_variables': [],
                'categorical_variables': []
            }
        
        characteristics = {
            'sample_size': len(df),
            'variable_count': len(df.columns),
            'completeness_score': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'data_types': df.dtypes.to_dict(),
            'numeric_variables': [],
            'text_variables': [],
            'datetime_variables': [],
            'categorical_variables': []
        }
        
        # Analyze each column
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                characteristics['numeric_variables'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                characteristics['datetime_variables'].append(col)
            elif df[col].dtype == 'object':
                # Check if it's categorical or text
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:  # Less than 50% unique values
                    characteristics['categorical_variables'].append(col)
                else:
                    characteristics['text_variables'].append(col)
        
        return characteristics
    
    @staticmethod
    def generate_analysis_recommendations(characteristics: Dict[str, Any]) -> List[str]:
        """Generate analysis recommendations based on data characteristics"""
        recommendations = []
        
        if characteristics['sample_size'] == 0:
            recommendations.append("No data available for analysis")
            return recommendations
        
        # Basic recommendations
        if characteristics['sample_size'] < 30:
            recommendations.append("Small sample size - consider collecting more data for reliable analysis")
        
        if characteristics['completeness_score'] < 80:
            recommendations.append("Data has missing values - consider data cleaning before analysis")
        
        # Analysis type recommendations
        if len(characteristics['numeric_variables']) >= 2:
            recommendations.append("Multiple numeric variables available - correlation analysis recommended")
        
        if len(characteristics['categorical_variables']) >= 1:
            recommendations.append("Categorical variables present - frequency analysis recommended")
        
        if len(characteristics['text_variables']) >= 1:
            recommendations.append("Text variables present - text analysis recommended")
        
        if len(characteristics['datetime_variables']) >= 1:
            recommendations.append("Time-based variables present - temporal analysis recommended")
        
        return recommendations
    
    @staticmethod
    def run_descriptive_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run descriptive analysis"""
        if df.empty:
            return {"error": "No data available for analysis"}
        
        # Basic statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        results = {
            'summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().to_dict()
            },
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Numeric variables summary
        for col in numeric_cols:
            if col in df.columns:
                results['numeric_summary'][col] = {
                    'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                    'median': float(df[col].median()) if not df[col].isnull().all() else None,
                    'std': float(df[col].std()) if not df[col].isnull().all() else None,
                    'min': float(df[col].min()) if not df[col].isnull().all() else None,
                    'max': float(df[col].max()) if not df[col].isnull().all() else None,
                    'missing_count': int(df[col].isnull().sum())
                }
        
        # Categorical variables summary
        for col in categorical_cols:
            if col in df.columns:
                value_counts = df[col].value_counts()
                results['categorical_summary'][col] = {
                    'unique_values': int(df[col].nunique()),
                    'most_common': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'missing_count': int(df[col].isnull().sum()),
                    'top_values': value_counts.head(5).to_dict()
                }
        
        return results
    
    @staticmethod
    def run_correlation_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run correlation analysis"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric variables for correlation analysis"}
        
        # Calculate correlation matrix
        correlation_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        'variable1': numeric_cols[i],
                        'variable2': numeric_cols[j],
                        'correlation': float(corr_value),
                        'strength': 'strong' if abs(corr_value) > 0.8 else 'moderate'
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'variables_analyzed': list(numeric_cols)
        }
    
    @staticmethod
    def run_basic_text_analysis(df: pd.DataFrame, text_columns: List[str]) -> Dict[str, Any]:
        """Run basic text analysis"""
        if not text_columns:
            return {"error": "No text columns specified for analysis"}
        
        results = {
            'text_columns': text_columns,
            'analysis': {}
        }
        
        for col in text_columns:
            if col not in df.columns:
                continue
                
            # Basic text statistics
            text_data = df[col].dropna()
            if len(text_data) == 0:
                continue
                
            # Calculate text statistics
            text_lengths = text_data.astype(str).str.len()
            
            results['analysis'][col] = {
                'total_texts': len(text_data),
                'average_length': float(text_lengths.mean()),
                'median_length': float(text_lengths.median()),
                'min_length': int(text_lengths.min()),
                'max_length': int(text_lengths.max()),
                'empty_texts': int((text_data == '').sum()),
                'unique_texts': int(text_data.nunique())
            }
        
        return results 