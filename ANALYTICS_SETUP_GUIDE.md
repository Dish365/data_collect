# Analytics System Setup Guide

This guide explains how to set up and use the integrated analytics system for the Research Data Collector application.

## Overview

The analytics system consists of two main components:
1. **GUI Analytics Interface** - Located in `gui/screens/analytics.py` and `gui/kv/analytics.kv`
2. **Backend Analytics Engine** - Located in `backend/analytics/`

## Prerequisites

1. **Python Environment**: Python 3.8+ with virtual environment
2. **GUI Application**: The main GUI application should be running and have at least one project with responses
3. **Database**: The `research_data.db` file should exist in your home directory

## Setup Instructions

### 1. Set Up the Analytics Backend

```bash
# Navigate to the analytics backend directory
cd backend/analytics

# Activate virtual environment (Windows PowerShell)
venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Start the analytics backend
python start_analytics.py
```

The backend will start on `http://127.0.0.1:8001` and provide the following endpoints:
- `/api/v1/analytics/health` - Health check
- `/api/v1/analytics/project/{project_id}/data-characteristics` - Data analysis
- `/api/v1/analytics/project/{project_id}/recommendations` - Analysis recommendations
- `/api/v1/analytics/project/{project_id}/analyze` - Run analysis

### 2. Set Up the GUI

```bash
# Navigate to the GUI directory
cd gui

# Activate virtual environment (Windows PowerShell)
venv\Scripts\Activate

# Run the GUI application
python main.py
```

### 3. Test the Integration

Run the integration test script from the project root:

```bash
python test_analytics_integration.py
```

## Using the Analytics System

### 1. Access Analytics

1. Open the GUI application
2. Navigate to the Analytics screen
3. Select a project from the dropdown
4. Choose an analysis type from the tabs:
   - **Auto-Detection**: Automatically recommends appropriate analyses
   - **Descriptive**: Basic statistics and summaries
   - **Inferential**: Statistical tests and hypothesis testing
   - **Qualitative**: Text analysis and sentiment analysis

### 2. Analysis Types

#### Auto-Detection
- Analyzes your data characteristics
- Recommends appropriate statistical methods
- Provides confidence scores for recommendations
- Shows data quality warnings

#### Descriptive Analysis
- Basic statistics (mean, median, mode, standard deviation)
- Frequency distributions for categorical data
- Data completeness and quality metrics
- Variable type identification

#### Inferential Analysis
- T-tests for comparing means
- ANOVA for multiple group comparisons
- Chi-square tests for categorical data
- Correlation significance tests
- Regression analysis

#### Qualitative Analysis
- Sentiment analysis of text responses
- Word frequency analysis
- Thematic analysis
- Content categorization
- Text similarity analysis

### 3. Offline Mode

The system works in both online and offline modes:

- **Online Mode**: When the backend is running, full analysis capabilities are available
- **Offline Mode**: Basic local analysis is performed using the GUI's analytics service

## Analysis Engines

The system integrates with four specialized analysis engines:

### 1. Auto-Detection Engine (`backend/analytics/app/analytics/auto_detect/`)
- **Purpose**: Automatically detect the most appropriate analysis methods
- **Features**: 
  - Data type detection
  - Statistical test recommendations
  - Analysis configuration suggestions
  - Confidence scoring

### 2. Descriptive Engine (`backend/analytics/app/analytics/descriptive/`)
- **Purpose**: Generate descriptive statistics and summaries
- **Features**:
  - Basic statistics calculation
  - Distribution analysis
  - Outlier detection
  - Missing data analysis
  - Categorical analysis

### 3. Inferential Engine (`backend/analytics/app/analytics/inferential/`)
- **Purpose**: Perform statistical hypothesis testing
- **Features**:
  - Hypothesis testing
  - Confidence intervals
  - Effect size calculations
  - Power analysis
  - Multiple comparisons correction

### 4. Qualitative Engine (`backend/analytics/app/analytics/qualitative/`)
- **Purpose**: Analyze text and qualitative data
- **Features**:
  - Sentiment analysis
  - Text classification
  - Thematic analysis
  - Content analysis
  - Survey response analysis

## Database Integration

The analytics system connects to the GUI's SQLite database (`research_data.db`) with the following tables:

- **projects**: Project metadata
- **questions**: Survey questions
- **responses**: Survey responses
- **respondents**: Respondent information

## API Endpoints

### Health Check
```
GET /api/v1/analytics/health
```

### Data Characteristics
```
GET /api/v1/analytics/project/{project_id}/data-characteristics
```

### Analysis Recommendations
```
GET /api/v1/analytics/project/{project_id}/recommendations
```

### Run Analysis
```
POST /api/v1/analytics/project/{project_id}/analyze
Content-Type: application/json

{
  "analysis_type": "descriptive|inferential|qualitative|auto"
}
```

## Troubleshooting

### Common Issues

1. **"No projects found"**
   - Ensure you have created at least one project in the GUI
   - Check that the project has questions and responses
   - Verify the database exists at `~/research_data.db`

2. **Backend connection failed**
   - Ensure the analytics backend is running on port 8001
   - Check firewall settings
   - Verify all dependencies are installed

3. **Analysis fails**
   - Check that the project has sufficient data
   - Verify the data types are supported
   - Check backend logs for detailed error messages

### Debug Mode

To enable debug mode:

1. **Backend**: Set `DEBUG=True` in `backend/analytics/core/config.py`
2. **GUI**: Add `print()` statements in `gui/screens/analytics.py`

### Log Files

- **Backend logs**: Console output when running `start_analytics.py`
- **GUI logs**: Console output when running `main.py`

## Performance Considerations

- **Large datasets**: Analysis may take longer for projects with >1000 responses
- **Memory usage**: The system loads all project data into memory for analysis
- **Concurrent users**: The backend supports multiple concurrent requests

## Security Notes

- The analytics backend runs on localhost only by default
- No authentication is required for local access
- Database access is read-only for analytics operations

## Future Enhancements

Planned features include:
- Real-time analysis updates
- Custom analysis templates
- Export functionality for results
- Advanced visualization options
- Machine learning integration 