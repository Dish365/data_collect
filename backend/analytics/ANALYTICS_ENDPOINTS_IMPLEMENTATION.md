# Analytics Endpoints Implementation Guide

This document provides a comprehensive overview of the analytics endpoints implementation with auto-detection capabilities.

## Overview

We have successfully implemented intelligent auto-detection endpoints for three analytics modules:

1. **Descriptive Analytics** - Data exploration and summary statistics
2. **Inferential Statistics** - Statistical testing and hypothesis testing
3. **Qualitative Analytics** - Text analysis and qualitative methods

Each module includes auto-detection capabilities that intelligently recommend appropriate analysis methods based on data characteristics.

## Architecture

### Base Components

#### 1. Base Detector (`base_detector.py`)
- **BaseAutoDetector**: Abstract base class for all auto-detection systems
- **DataCharacteristics**: Standardized data profiling structure
- **AnalysisRecommendation**: Structured recommendations with confidence scores
- **AnalysisSuggestions**: Container for multiple recommendations
- **StandardizedDataProfiler**: Unified data profiling across all modules

#### 2. Unified Auto-Detector (`auto_detect/__init__.py`)
- **UnifiedAutoDetector**: Coordinates all analytics modules
- Cross-module intelligence and analysis coordination
- Generates unified recommendations across different analysis types

### Module-Specific Detectors

#### 1. Descriptive Auto-Detector (`descriptive/auto_detection.py`)
- Detects data types and suggests appropriate descriptive analyses
- Methods: basic_statistics, distribution_analysis, correlation_analysis, etc.
- Auto-configures parameters based on data characteristics

#### 2. Inferential Auto-Detector (`inferential/auto_detection.py`)
- Suggests statistical tests based on research design
- Methods: t-tests, ANOVA, non-parametric tests, regression, etc.
- Checks statistical assumptions and suggests alternatives

#### 3. Qualitative Auto-Detector (`qualitative/auto_detection.py`)
- Analyzes text data and suggests qualitative methods
- Methods: sentiment_analysis, thematic_analysis, content_analysis, coding
- Detects text types (interviews, surveys, narratives, etc.)

## API Endpoints

### Base URL Structure
```
/api/v1/{module}/
```

### Descriptive Analytics Endpoints

#### POST `/api/v1/descriptive/analyze`
Comprehensive descriptive analysis with auto-detection
```json
{
  "data": {"column1": [1, 2, 3], "column2": ["A", "B", "C"]},
  "analysis_goals": ["data_overview", "relationships"],
  "target_variables": ["column1"],
  "variable_metadata": [...]
}
```

#### POST `/api/v1/descriptive/suggest-analyses`
Get analysis method suggestions
```json
{
  "data": {...},
  "analysis_goals": [...],
  "variable_metadata": [...]
}
```

#### POST `/api/v1/descriptive/configure/{method_name}`
Auto-configure parameters for specific method
```json
{
  "data": {...},
  "target_variables": [...],
  "custom_parameters": {...}
}
```

#### POST `/api/v1/descriptive/quick-recommendation`
Get quick analysis recommendation
```json
{
  "data": {...},
  "analysis_type": "auto"
}
```

#### GET `/api/v1/descriptive/methods`
List all available descriptive methods

### Inferential Statistics Endpoints

#### POST `/api/v1/inferential/analyze`
Comprehensive inferential analysis with auto-detection
```json
{
  "data": {...},
  "target_variable": "dependent_var",
  "grouping_variable": "independent_var",
  "research_question": "compare_groups",
  "alpha": 0.05
}
```

#### POST `/api/v1/inferential/suggest-tests`
Get statistical test suggestions
```json
{
  "data": {...},
  "target_variable": "outcome",
  "grouping_variable": "group",
  "alpha": 0.05
}
```

#### POST `/api/v1/inferential/configure-test/{method_name}`
Auto-configure test parameters
```json
{
  "data": {...},
  "target_variable": "outcome",
  "grouping_variable": "group",
  "custom_parameters": {...}
}
```

#### POST `/api/v1/inferential/check-assumptions`
Check statistical assumptions for a test
```json
{
  "data": {...},
  "test_name": "two_sample_t_test",
  "target_variable": "outcome",
  "grouping_variable": "group"
}
```

#### POST `/api/v1/inferential/quick-test-suggestion`
Get quick test suggestion for simple data
```json
{
  "data1": [1, 2, 3, 4, 5],
  "data2": [2, 3, 4, 5, 6],
  "paired": false
}
```

### Qualitative Analytics Endpoints

#### POST `/api/v1/qualitative/analyze`
Comprehensive qualitative analysis with auto-detection
```json
{
  "data": {"text_column": ["text1", "text2", "text3"]},
  "text_columns": ["text_column"],
  "research_goals": ["themes", "sentiment"],
  "metadata": [...]
}
```

#### POST `/api/v1/qualitative/suggest-methods`
Get qualitative method suggestions
```json
{
  "data": {...},
  "text_columns": ["comments"],
  "research_goals": ["sentiment_analysis"]
}
```

#### POST `/api/v1/qualitative/detect-data-type`
Detect qualitative data type
```json
{
  "data": {...},
  "text_columns": ["text_field"],
  "metadata": [...]
}
```

#### POST `/api/v1/qualitative/text-characteristics`
Get detailed text characteristics
```json
{
  "data": {...},
  "text_columns": ["text_field"],
  "include_linguistic_features": true
}
```

#### POST `/api/v1/qualitative/quick-recommendation`
Get quick qualitative recommendation
```json
{
  "texts": ["text1", "text2", "text3"],
  "analysis_focus": "auto"
}
```

### Unified Auto-Detection Endpoints

#### POST `/api/v1/auto-detect/analyze/comprehensive`
Comprehensive analysis using all modules
```json
{
  "data": {...},
  "analysis_type": "auto",
  "include_descriptive": true,
  "include_inferential": true,
  "include_qualitative": true,
  "target_variable": "outcome",
  "grouping_variable": "group"
}
```

#### POST `/api/v1/auto-detect/suggest-methods`
Get intelligent method suggestions across all modules
```json
{
  "data": {...},
  "analysis_focus": "auto",
  "research_context": {...}
}
```

#### POST `/api/v1/auto-detect/data-characteristics`
Get comprehensive data profiling
```json
{
  "data": {...},
  "variable_metadata": [...]
}
```

## Key Features

### 1. Intelligent Auto-Detection
- Automatically detects data types and characteristics
- Suggests optimal analysis methods based on data properties
- Provides confidence scores for recommendations

### 2. Cross-Module Intelligence
- Coordinates recommendations across descriptive, inferential, and qualitative modules
- Identifies opportunities for mixed-methods analysis
- Provides unified analysis workflows

### 3. Standardized Interface
- Consistent API design across all modules
- Standardized data structures and response formats
- Common error handling and validation

### 4. Auto-Configuration
- Automatically configures analysis parameters
- Adapts to data size, quality, and characteristics
- Provides parameter explanations and guidance

### 5. Assumption Checking
- Tests statistical assumptions for inferential methods
- Suggests alternative methods when assumptions are violated
- Provides detailed assumption violation reports

### 6. Quality Assessment
- Comprehensive data quality analysis
- Missing data patterns and recommendations
- Sample size adequacy assessment

## Usage Examples

### Example 1: Descriptive Analysis
```python
import requests

data = {
    "data": {
        "age": [25, 30, 35, 40, 45],
        "income": [50000, 60000, 70000, 80000, 90000],
        "category": ["A", "B", "A", "B", "A"]
    }
}

response = requests.post("/api/v1/descriptive/analyze", json=data)
result = response.json()

print(f"Recommended analyses: {result['recommendations']['primary_recommendations']}")
```

### Example 2: Statistical Testing
```python
data = {
    "data": {
        "score": [85, 90, 78, 92, 88, 76, 89, 91],
        "group": ["A", "A", "A", "A", "B", "B", "B", "B"]
    },
    "target_variable": "score",
    "grouping_variable": "group"
}

response = requests.post("/api/v1/inferential/suggest-tests", json=data)
tests = response.json()

print(f"Recommended test: {tests['primary_recommendations'][0]['method']}")
```

### Example 3: Text Analysis
```python
data = {
    "texts": [
        "I love this product, it's amazing!",
        "Terrible service, would not recommend.",
        "Good quality for the price.",
        "Excellent customer support team."
    ]
}

response = requests.post("/api/v1/qualitative/quick-recommendation", json=data)
recommendation = response.json()

print(f"Recommended method: {recommendation['recommendation']}")
```

### Example 4: Comprehensive Analysis
```python
data = {
    "data": {
        "numeric_var": [1, 2, 3, 4, 5],
        "categorical_var": ["A", "B", "C", "A", "B"],
        "text_var": ["Good", "Bad", "Excellent", "Poor", "Fair"]
    },
    "analysis_type": "comprehensive"
}

response = requests.post("/api/v1/auto-detect/analyze/comprehensive", json=data)
results = response.json()

print(f"Modules used: {results['modules_used']}")
print(f"Cross-module insights: {results['cross_module_insights']}")
```

## Testing

Run the test suite to verify implementation:

```bash
cd backend/analytics
python test_endpoints.py
```

The test suite includes:
- Import verification
- Module functionality testing
- API endpoint structure validation
- Sample data analysis tests

## Error Handling

All endpoints include comprehensive error handling:

- **400 Bad Request**: Invalid data or parameters
- **404 Not Found**: Unknown method or endpoint
- **422 Unprocessable Entity**: Data validation errors
- **500 Internal Server Error**: Processing errors

Error responses include detailed messages:
```json
{
  "detail": "Error description",
  "status_code": 400,
  "error_type": "ValidationError"
}
```

## Performance Considerations

### Data Size Limits
- Descriptive: Optimized for datasets up to 100k rows
- Inferential: Best performance with < 10k observations
- Qualitative: Optimized for up to 1k text documents

### Caching
- Data characteristics are cached for repeated analyses
- Method recommendations are memoized
- Auto-configurations are cached by data fingerprint

### Async Processing
- Large datasets are processed asynchronously
- Progress tracking for long-running analyses
- Background task queuing for complex workflows

## Configuration

### Environment Variables
```bash
# Analytics configuration
ANALYTICS_MAX_DATA_SIZE=100000
ANALYTICS_CACHE_TTL=3600
ANALYTICS_ASYNC_THRESHOLD=10000

# Module-specific settings
DESCRIPTIVE_MAX_VARIABLES=1000
INFERENTIAL_MIN_SAMPLE_SIZE=5
QUALITATIVE_MAX_TEXT_LENGTH=10000
```

### Database Configuration
The endpoints use the existing database configuration from `core/database.py` for session management and result storage.

## Extending the System

### Adding New Methods

1. **Define method requirements** in the detector's `get_method_requirements()`
2. **Implement assessment logic** in `assess_method_suitability()`
3. **Add configuration logic** in the auto-configuration methods
4. **Update endpoint documentation**

### Custom Detectors

1. **Inherit from BaseAutoDetector**
2. **Implement required abstract methods**
3. **Register with UnifiedAutoDetector**
4. **Add endpoint routes**

### Integration with Frontend

The endpoints are designed to integrate seamlessly with the existing GUI:

1. **Dashboard Integration**: Use `/api/v1/auto-detect/data-characteristics` for data overview
2. **Analysis Workflows**: Use comprehensive analysis endpoints for full workflows
3. **Method Selection**: Use suggestion endpoints for guided analysis
4. **Parameter Configuration**: Use auto-configuration for user-friendly setup

## Support and Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and paths are correct
2. **Memory Issues**: Reduce data size or enable async processing
3. **Method Not Found**: Check method names against available methods list
4. **Configuration Errors**: Verify data types and parameter formats

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger('app.analytics').setLevel(logging.DEBUG)
```

### Getting Help

- Check endpoint documentation: `/api/v1/docs`
- Run test suite for validation
- Review error messages and status codes
- Check method requirements and data compatibility

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**: Automated model selection and tuning
2. **Advanced Visualizations**: Intelligent chart recommendations
3. **Report Generation**: Automated analysis reports with insights
4. **Real-time Analysis**: Streaming data analysis capabilities
5. **Custom Workflows**: User-defined analysis pipelines

### API Evolution

- **Version 2**: Enhanced ML capabilities and real-time processing
- **GraphQL Support**: Flexible query capabilities
- **Webhook Integration**: Event-driven analysis triggers
- **Batch Processing**: Large-scale data analysis capabilities

This implementation provides a solid foundation for intelligent, automated analytics that can grow with your application's needs. 