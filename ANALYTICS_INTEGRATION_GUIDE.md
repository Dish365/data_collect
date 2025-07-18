# Analytics Integration Guide

## Overview

This guide explains how to use the enhanced analytics system that properly integrates the Kivy GUI with the FastAPI analytics backend, providing comprehensive data analysis capabilities for research data collection.

## Architecture

The analytics system consists of three main components:

1. **FastAPI Backend** (`backend/fastapi/`) - Analytics engine with advanced algorithms
2. **GUI Frontend** (`gui/`) - Kivy-based interface for researchers
3. **Django Backend** (`backend/`) - Data storage and management

## Quick Start

### 1. Start the Analytics Backend

```bash
# Navigate to the FastAPI directory
cd backend/fastapi

# Activate virtual environment
source ../../venv/bin/activate  # Linux/Mac
# or
../../venv/Scripts/activate     # Windows

# Start the analytics backend
python start_analytics_backend.py
```

This will start the FastAPI server on `http://localhost:8001` with:
- API Documentation: `http://localhost:8001/docs`
- Health Check: `http://localhost:8001/api/v1/analytics/health`

### 2. Start the GUI Application

```bash
# Navigate to GUI directory
cd gui

# Activate virtual environment
source ../venv/bin/activate  # Linux/Mac
# or
../venv/Scripts/activate     # Windows

# Start the GUI
python main.py
```

### 3. Access Analytics Features

1. **Login** to the application
2. **Select a Project** with data
3. **Navigate to Analytics** tab
4. **Choose Analysis Type:**
   - **Auto-Detection**: AI-powered recommendations
   - **Descriptive**: Basic statistics and summaries
   - **Inferential**: Hypothesis testing and inference
   - **Qualitative**: Text analysis and sentiment

## Analytics Features

### Auto-Detection Tab

The Auto-Detection feature uses AI to analyze your data and provide smart recommendations:

- **Data Characteristics Analysis**: Automatically detects variable types, data quality issues, and patterns
- **Smart Recommendations**: Suggests appropriate analysis methods based on your data
- **Automated Analysis**: Runs multiple analysis types and presents results

**Usage:**
1. Select a project with data
2. Click "Analyze Data" button
3. Review recommendations and analysis results

### Descriptive Analytics Tab

Provides comprehensive descriptive statistics and data summaries:

- **Basic Statistics**: Mean, median, standard deviation, etc.
- **Categorical Analysis**: Frequency tables and distributions
- **Distribution Analysis**: Histograms, box plots, and normality tests
- **Correlation Analysis**: Relationships between variables

**Usage:**
1. Select variables to analyze
2. Choose analysis type (Basic Statistics, Distributions, Correlations)
3. View results in interactive cards

### Inferential Analytics Tab

Advanced statistical testing and inference:

- **Hypothesis Testing**: t-tests, ANOVA, chi-square tests
- **Regression Analysis**: Linear and logistic regression
- **Confidence Intervals**: Parameter estimation
- **Effect Size Calculations**: Cohen's d, eta-squared, etc.

**Usage:**
1. Select target and grouping variables
2. Choose test type (T-Tests, ANOVA, Regression)
3. Interpret statistical results

### Qualitative Analytics Tab

Text analysis and qualitative data processing:

- **Sentiment Analysis**: Emotional tone detection
- **Theme Analysis**: Topic modeling and clustering
- **Content Analysis**: Word frequency and patterns
- **Survey Analysis**: Open-ended response analysis

**Usage:**
1. Select text fields to analyze
2. Set theme count (for topic modeling)
3. Choose analysis type (Sentiment, Theme, Content)
4. Review qualitative insights

## API Endpoints

### Project Statistics
```
GET /api/v1/analytics/project/{project_id}/stats
```
Returns basic project statistics including response counts, question counts, and completion rates.

### Data Characteristics
```
GET /api/v1/analytics/project/{project_id}/data-characteristics
```
Analyzes data structure, variable types, and data quality metrics.

### Analysis Recommendations
```
GET /api/v1/analytics/project/{project_id}/recommendations
```
Provides AI-powered analysis recommendations based on data characteristics.

### Run Analysis
```
POST /api/v1/analytics/project/{project_id}/analyze
```
Executes analysis with specified parameters:
- `analysis_type`: "auto", "descriptive", "correlation", "text"
- Additional configuration parameters

### Custom Data Analysis
```
POST /api/v1/analytics/project/{project_id}/analyze/custom
```
Analyzes custom data (for testing or external datasets).

## Configuration

### FastAPI Backend Settings

Edit `backend/fastapi/core/config.py`:

```python
class Settings:
    PROJECT_NAME: str = "Research Analytics Engine"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"
    
    # CORS settings for GUI integration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Analytics settings
    MAX_ANALYSIS_ROWS: int = 10000
    DEFAULT_SAMPLE_SIZE: int = 1000
```

### GUI Service Configuration

The GUI automatically connects to the FastAPI backend at `http://127.0.0.1:8001`.

To change the backend URL, edit `gui/services/analytics_service.py`:

```python
def __init__(self, auth_service, db_service):
    self.base_url = "http://127.0.0.1:8001"  # Change this if needed
```

## Available Analytics Algorithms

### Descriptive Analytics (`backend/fastapi/app/analytics/descriptive/`)

- **Basic Statistics**: Mean, median, mode, standard deviation, variance
- **Categorical Analysis**: Frequency tables, cross-tabulations
- **Distribution Analysis**: Histograms, Q-Q plots, normality tests
- **Outlier Detection**: Z-score, IQR, isolation forest methods
- **Missing Data Analysis**: Patterns and imputation strategies
- **Temporal Analysis**: Time series decomposition and trends
- **Geospatial Analysis**: Spatial clustering and mapping

### Inferential Analytics (`backend/fastapi/app/analytics/inferential/`)

- **Hypothesis Testing**: t-tests, ANOVA, chi-square, Mann-Whitney U
- **Regression Analysis**: Linear, logistic, polynomial regression
- **Confidence Intervals**: Bootstrap and parametric methods
- **Effect Size Calculations**: Cohen's d, eta-squared, Cramér's V
- **Power Analysis**: Sample size calculations and power curves
- **Bayesian Inference**: Bayesian t-tests and regression
- **Time Series Analysis**: ARIMA, seasonal decomposition

### Qualitative Analytics (`backend/fastapi/app/analytics/qualitative/`)

- **Text Analysis**: Word frequency, n-grams, readability scores
- **Sentiment Analysis**: Polarity, emotion detection, opinion mining
- **Thematic Analysis**: Topic modeling, theme extraction
- **Content Analysis**: Coding schemes, content categorization
- **Survey Analysis**: Open-ended response analysis
- **Coding Systems**: Automated and manual coding support

### Auto-Detection (`backend/fastapi/app/analytics/auto_detect/`)

- **Survey Detection**: Automatic survey structure recognition
- **Variable Type Detection**: Automatic classification of variables
- **Data Quality Assessment**: Completeness, accuracy, consistency
- **Analysis Recommendations**: AI-powered method suggestions

## Error Handling

The system includes comprehensive error handling:

### Backend Errors
- Database connection issues
- Invalid data formats
- Analysis algorithm failures
- Resource limitations

### GUI Fallbacks
- Local analysis when backend is unavailable
- Cached results for improved performance
- User-friendly error messages
- Graceful degradation

## Performance Optimization

### Caching
- Analysis results are cached for 5 minutes
- Data characteristics cached until data changes
- Recommendations cached per project

### Data Limits
- Maximum 10,000 rows per analysis (configurable)
- Automatic sampling for large datasets
- Progress indicators for long-running analyses

### Parallel Processing
- Multiple analysis types run concurrently
- Background threading for UI responsiveness
- Asynchronous API calls

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure FastAPI server is running on port 8001
   - Check CORS settings in `core/config.py`
   - Verify network connectivity

2. **Analysis Failed**
   - Check data quality and completeness
   - Verify variable types are correct
   - Review server logs for detailed errors

3. **GUI Doesn't Load Results**
   - Check analytics service initialization
   - Verify project selection
   - Look for JavaScript/Python errors in logs

### Debug Mode

Start the FastAPI backend with debug logging:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level debug
```

Start the GUI with debug output:

```bash
python main.py --debug
```

## Development

### Adding New Analytics Methods

1. Create new analysis class in appropriate directory
2. Import and integrate in `app/utils/shared.py`
3. Add endpoint in `app/api/v1/endpoints/analytics.py`
4. Update GUI service methods as needed

### Testing

Run the analytics backend tests:

```bash
cd backend/fastapi
python -m pytest tests/
```

Test the GUI analytics features:

```bash
cd gui
python test_analytics.py
```

## Support

For issues and questions:
- Check the logs in `backend/fastapi/logs/`
- Review the API documentation at `http://localhost:8001/docs`
- Consult the research tool plan in `docs/research-tool-plan.md`

## License

This analytics system is part of the Research Data Collection Tool and follows the same license terms. 