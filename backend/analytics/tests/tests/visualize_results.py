"""
Visualize results from descriptive statistics tests.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import json
from mock_data_generator import generate_all_datasets

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class DescriptiveStatsVisualizer:
    """Visualize descriptive statistics results."""
    
    def __init__(self):
        self.datasets = generate_all_datasets()
        self.fig_num = 1
        
    def visualize_basic_statistics(self):
        """Visualize basic statistics for numeric variables."""
        df = self.datasets['rural_health']
        
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle('Basic Statistics Visualization - Rural Health Survey', fontsize=16)
        
        gs = GridSpec(3, 3, figure=fig)
        
        # 1. Distribution plots for key variables
        variables = ['age', 'bmi', 'health_score']
        for i, var in enumerate(variables):
            ax = fig.add_subplot(gs[0, i])
            
            # Histogram with KDE
            df[var].hist(bins=30, alpha=0.7, ax=ax, density=True)
            df[var].plot.kde(ax=ax, color='red', linewidth=2)
            
            # Add mean and median lines
            mean_val = df[var].mean()
            median_val = df[var].median()
            ax.axvline(mean_val, color='blue', linestyle='--', label=f'Mean: {mean_val:.1f}')
            ax.axvline(median_val, color='green', linestyle='--', label=f'Median: {median_val:.1f}')
            
            ax.set_title(f'Distribution of {var}')
            ax.set_xlabel(var)
            ax.legend()
        
        # 2. Box plots
        ax = fig.add_subplot(gs[1, :])
        numeric_cols = ['age', 'bmi', 'health_score', 'systolic_bp', 'distance_to_clinic_km']
        df[numeric_cols].boxplot(ax=ax)
        ax.set_title('Box Plots of Numeric Variables')
        ax.set_ylabel('Value')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 3. Correlation heatmap
        ax = fig.add_subplot(gs[2, :2])
        corr_cols = ['age', 'bmi', 'health_score', 'systolic_bp', 'monthly_income_usd']
        corr_matrix = df[corr_cols].corr()
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                    center=0, ax=ax, square=True)
        ax.set_title('Correlation Matrix')
        
        # 4. Missing data pattern
        ax = fig.add_subplot(gs[2, 2])
        missing_counts = df.isnull().sum()
        missing_counts = missing_counts[missing_counts > 0]
        if not missing_counts.empty:
            missing_counts.plot(kind='barh', ax=ax)
            ax.set_title('Missing Data by Column')
            ax.set_xlabel('Count')
        
        plt.tight_layout()
        plt.savefig('basic_statistics_visualization.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def visualize_distributions(self):
        """Visualize distribution analysis results."""
        df = self.datasets['rural_health']
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Distribution Analysis - Normality and Shape', fontsize=16)
        axes = axes.flatten()
        
        variables = ['age', 'bmi', 'health_score', 'monthly_income_usd', 
                    'distance_to_clinic_km', 'survey_duration_minutes']
        
        for i, var in enumerate(variables):
            ax = axes[i]
            data = df[var].dropna()
            
            # Q-Q plot for normality assessment
            from scipy import stats
            stats.probplot(data, dist="norm", plot=ax)
            
            # Add skewness and kurtosis info
            skew = data.skew()
            kurt = data.kurtosis()
            ax.text(0.05, 0.95, f'Skewness: {skew:.2f}\nKurtosis: {kurt:.2f}', 
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_title(f'Q-Q Plot: {var}')
        
        plt.tight_layout()
        plt.savefig('distribution_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def visualize_categorical_analysis(self):
        """Visualize categorical data analysis."""
        df = self.datasets['rural_health']
        
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle('Categorical Data Analysis', fontsize=16)
        
        gs = GridSpec(3, 3, figure=fig)
        
        # 1. Bar plots for categorical variables
        cat_vars = ['gender', 'education_level', 'water_access']
        for i, var in enumerate(cat_vars):
            ax = fig.add_subplot(gs[0, i])
            df[var].value_counts().plot(kind='bar', ax=ax)
            ax.set_title(f'Distribution of {var}')
            ax.set_xlabel('')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. Stacked bar chart - Education vs Water Access
        ax = fig.add_subplot(gs[1, :])
        crosstab = pd.crosstab(df['education_level'], df['water_access'], normalize='index') * 100
        crosstab.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title('Water Access by Education Level (%)')
        ax.set_ylabel('Percentage')
        ax.legend(title='Water Access', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 3. Mosaic plot simulation (using heatmap)
        ax = fig.add_subplot(gs[2, :])
        crosstab_counts = pd.crosstab(df['gender'], df['has_malaria'])
        sns.heatmap(crosstab_counts, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
        ax.set_title('Gender vs Malaria Status')
        
        plt.tight_layout()
        plt.savefig('categorical_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def visualize_outliers(self):
        """Visualize outlier detection results."""
        df = self.datasets['rural_health']
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Outlier Detection Analysis', fontsize=16)
        
        # 1. BMI outliers with different methods
        ax = axes[0, 0]
        bmi_data = df['bmi'].dropna()
        
        # Calculate outliers using IQR
        Q1 = bmi_data.quantile(0.25)
        Q3 = bmi_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Plot
        ax.scatter(range(len(bmi_data)), bmi_data, alpha=0.5)
        outliers_mask = (bmi_data < lower_bound) | (bmi_data > upper_bound)
        outliers = bmi_data[outliers_mask]
        ax.scatter(outliers.index, outliers, color='red', s=100, label='IQR Outliers')
        ax.axhline(lower_bound, color='red', linestyle='--', label='IQR Bounds')
        ax.axhline(upper_bound, color='red', linestyle='--')
        ax.set_title('BMI Outliers (IQR Method)')
        ax.set_ylabel('BMI')
        ax.legend()
        
        # 2. Z-score visualization
        ax = axes[0, 1]
        z_scores = np.abs((bmi_data - bmi_data.mean()) / bmi_data.std())
        ax.scatter(range(len(z_scores)), z_scores, alpha=0.5)
        ax.axhline(3, color='red', linestyle='--', label='Z-score = 3')
        ax.set_title('BMI Z-scores')
        ax.set_ylabel('|Z-score|')
        ax.legend()
        
        # 3. Multivariate outliers
        ax = axes[1, 0]
        ax.scatter(df['age'], df['bmi'], alpha=0.5)
        ax.set_xlabel('Age')
        ax.set_ylabel('BMI')
        ax.set_title('Age vs BMI (for multivariate outlier detection)')
        
        # 4. Outlier summary across variables
        ax = axes[1, 1]
        outlier_counts = {}
        for col in ['age', 'bmi', 'health_score', 'systolic_bp']:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)).sum()
            outlier_counts[col] = outliers
        
        pd.Series(outlier_counts).plot(kind='bar', ax=ax)
        ax.set_title('Outlier Count by Variable (IQR Method)')
        ax.set_ylabel('Number of Outliers')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig('outlier_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def visualize_temporal_patterns(self):
        """Visualize temporal analysis results."""
        df = self.datasets['rural_health']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Temporal Patterns Analysis', fontsize=16)
        
        # 1. Data collection over time
        ax = axes[0, 0]
        daily_counts = df.groupby(df['collection_date'].dt.date).size()
        daily_counts.plot(ax=ax, color='blue', linewidth=2)
        ax.set_title('Daily Response Count')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Responses')
        
        # 2. Day of week pattern
        ax = axes[0, 1]
        df['day_of_week'] = df['collection_date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = df['day_of_week'].value_counts().reindex(day_order)
        day_counts.plot(kind='bar', ax=ax, color='green')
        ax.set_title('Responses by Day of Week')
        ax.set_ylabel('Count')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 3. Health score trend over time
        ax = axes[1, 0]
        weekly_health = df.groupby(pd.Grouper(key='collection_date', freq='W'))['health_score'].agg(['mean', 'std'])
        weekly_health['mean'].plot(ax=ax, label='Mean Health Score', linewidth=2)
        ax.fill_between(weekly_health.index, 
                       weekly_health['mean'] - weekly_health['std'],
                       weekly_health['mean'] + weekly_health['std'],
                       alpha=0.3, label='±1 SD')
        ax.set_title('Weekly Health Score Trend')
        ax.set_ylabel('Health Score')
        ax.legend()
        
        # 4. Hour of day pattern
        ax = axes[1, 1]
        df['hour'] = df['collection_time'].dt.hour
        hour_counts = df['hour'].value_counts().sort_index()
        hour_counts.plot(kind='bar', ax=ax, color='orange')
        ax.set_title('Data Collection by Hour of Day')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Count')
        
        plt.tight_layout()
        plt.savefig('temporal_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def visualize_geospatial_patterns(self):
        """Visualize geospatial analysis results."""
        df = self.datasets['rural_health']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Geospatial Analysis', fontsize=16)
        
        # 1. Spatial distribution of responses
        ax = axes[0, 0]
        scatter = ax.scatter(df['longitude'], df['latitude'], 
                           c=df['health_score'], cmap='RdYlGn', 
                           alpha=0.6, s=50)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Spatial Distribution of Health Scores')
        plt.colorbar(scatter, ax=ax, label='Health Score')
        
        # 2. Location clusters
        ax = axes[0, 1]
        location_counts = df['location_name'].value_counts().head(10)
        location_counts.plot(kind='barh', ax=ax)
        ax.set_title('Top 10 Survey Locations')
        ax.set_xlabel('Number of Responses')
        
        # 3. Health score by location
        ax = axes[1, 0]
        location_health = df.groupby('location_name')['health_score'].mean().sort_values(ascending=False).head(10)
        location_health.plot(kind='barh', ax=ax, color='skyblue')
        ax.set_title('Average Health Score by Location (Top 10)')
        ax.set_xlabel('Average Health Score')
        
        # 4. Distance to clinic distribution
        ax = axes[1, 1]
        df['distance_to_clinic_km'].hist(bins=30, ax=ax, alpha=0.7, color='purple')
        ax.axvline(df['distance_to_clinic_km'].mean(), color='red', 
                  linestyle='--', label=f"Mean: {df['distance_to_clinic_km'].mean():.1f} km")
        ax.set_title('Distribution of Distance to Health Clinic')
        ax.set_xlabel('Distance (km)')
        ax.set_ylabel('Frequency')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig('geospatial_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_summary_dashboard(self):
        """Create a comprehensive dashboard of all analyses."""
        df = self.datasets['rural_health']
        
        fig = plt.figure(figsize=(20, 12))
        fig.suptitle('Comprehensive Descriptive Statistics Dashboard - Rural Health Survey', fontsize=20)
        
        gs = GridSpec(4, 4, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Key metrics
        ax = fig.add_subplot(gs[0, :2])
        ax.axis('off')
        metrics_text = f"""
        Dataset Overview:
        • Total Responses: {len(df)}
        • Date Range: {df['collection_date'].min().strftime('%Y-%m-%d')} to {df['collection_date'].max().strftime('%Y-%m-%d')}
        • Missing Data: {df.isnull().sum().sum()} cells ({df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100:.1f}%)
        • Complete Cases: {df.dropna().shape[0]} ({df.dropna().shape[0] / len(df) * 100:.1f}%)
        
        Key Health Indicators:
        • Average Health Score: {df['health_score'].mean():.1f} ± {df['health_score'].std():.1f}
        • Malaria Prevalence: {df['has_malaria'].sum() / df['has_malaria'].count() * 100:.1f}%
        • Hypertension Rate: {df['has_hypertension'].sum() / df['has_hypertension'].count() * 100:.1f}%
        """
        ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes, 
               fontsize=12, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        # 2. Age distribution
        ax = fig.add_subplot(gs[0, 2])
        df['age'].hist(bins=20, ax=ax, alpha=0.7, color='blue')
        ax.set_title('Age Distribution')
        ax.set_xlabel('Age')
        
        # 3. Gender split
        ax = fig.add_subplot(gs[0, 3])
        df['gender'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_title('Gender Distribution')
        ax.set_ylabel('')
        
        # 4. Health score by education
        ax = fig.add_subplot(gs[1, :2])
        df.boxplot(column='health_score', by='education_level', ax=ax)
        ax.set_title('Health Score by Education Level')
        ax.set_xlabel('Education Level')
        ax.set_ylabel('Health Score')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 5. BMI categories
        ax = fig.add_subplot(gs[1, 2:])
        bmi_categories = pd.cut(df['bmi'], bins=[0, 18.5, 25, 30, 100], 
                               labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
        bmi_categories.value_counts().sort_index().plot(kind='bar', ax=ax, color='orange')
        ax.set_title('BMI Categories')
        ax.set_ylabel('Count')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 6. Water access
        ax = fig.add_subplot(gs[2, :2])
        water_counts = df['water_access'].value_counts()
        water_counts.plot(kind='bar', ax=ax, color='cyan')
        ax.set_title('Water Access Type')
        ax.set_ylabel('Count')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 7. Correlation heatmap
        ax = fig.add_subplot(gs[2, 2:])
        corr_cols = ['age', 'bmi', 'health_score', 'systolic_bp', 'distance_to_clinic_km']
        corr_data = df[corr_cols].corr()
        sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm', 
                    center=0, ax=ax, square=True, cbar_kws={'shrink': 0.8})
        ax.set_title('Variable Correlations')
        
        # 8. Temporal trend
        ax = fig.add_subplot(gs[3, :])
        daily_responses = df.groupby(df['collection_date'].dt.date).size()
        daily_health = df.groupby(df['collection_date'].dt.date)['health_score'].mean()
        
        ax2 = ax.twinx()
        daily_responses.plot(ax=ax, color='blue', linewidth=2, label='Daily Responses')
        daily_health.plot(ax=ax2, color='red', linewidth=2, label='Avg Health Score')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Responses', color='blue')
        ax2.set_ylabel('Average Health Score', color='red')
        ax.set_title('Data Collection Timeline')
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig('comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def run_all_visualizations(self):
        """Run all visualization methods."""
        print("Creating visualizations...")
        
        visualization_methods = [
            ('Basic Statistics', self.visualize_basic_statistics),
            ('Distribution Analysis', self.visualize_distributions),
            ('Categorical Analysis', self.visualize_categorical_analysis),
            ('Outlier Detection', self.visualize_outliers),
            ('Temporal Patterns', self.visualize_temporal_patterns),
            ('Geospatial Patterns', self.visualize_geospatial_patterns),
            ('Summary Dashboard', self.create_summary_dashboard)
        ]
        
        for name, method in visualization_methods:
            print(f"\nCreating {name} visualization...")
            try:
                method()
                print(f"✓ {name} visualization saved")
            except Exception as e:
                print(f"✗ Error in {name}: {str(e)}")
        
        print("\nAll visualizations completed!")

if __name__ == "__main__":
    visualizer = DescriptiveStatsVisualizer()
    visualizer.run_all_visualizations()