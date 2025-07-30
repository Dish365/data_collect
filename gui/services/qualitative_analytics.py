"""
Qualitative Analytics Handler
Specialized service for qualitative text analysis - Business Logic Only
"""

from typing import Dict, List, Any, Optional
import threading
import urllib.parse
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class QualitativeAnalyticsHandler:
    """Handler for qualitative analytics operations - Business Logic Only"""
    
    def __init__(self, analytics_service, screen):
        self.analytics_service = analytics_service
        self.screen = screen
    
    def run_text_analysis(self, project_id: str, analysis_config: Dict = None):
        """Run text analysis for a project"""
        print(f"[DEBUG] run_text_analysis called with project_id: {project_id}")
        
        if not project_id:
            print(f"[DEBUG] No project_id provided")
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_text_analysis_thread,
            args=(project_id, analysis_config),
            daemon=True
        ).start()
    
    def _run_text_analysis_thread(self, project_id: str, analysis_config: Dict):
        """Background thread for text analysis"""
        try:
            results = self.analytics_service.run_analysis(
                project_id, "text", analysis_config
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_text_analysis_results(results), 0
            )
        except Exception as e:
            print(f"Error in text analysis: {e}")
            Clock.schedule_once(
                lambda dt: self.screen.show_error("Text analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_text_analysis_results(self, results):
        """Handle text analysis results - delegate to UI"""
        print(f"[DEBUG] Text analysis results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                toast("Backend connection error")
            else:
                toast(f"Text Analysis Error: {error_msg}")
            return
        
        # Delegate to screen to handle UI display
        self.screen.display_qualitative_results(results)
    
    def get_text_analysis_summary(self, results: Dict) -> Dict:
        """Extract text analysis summary data for UI consumption"""
        data_chars = results.get('data_characteristics', {})
        text_vars = data_chars.get('text_variables', [])
        
        # Check for text analysis summary
        text_analysis = results.get('analyses', {}).get('text', {})
        summary = text_analysis.get('summary', {})
        
        return {
            'text_fields_analyzed': len(text_vars),
            'total_text_entries': summary.get('total_text_entries', 'N/A'),
            'fields': text_vars[:3],  # First 3 fields
            'has_more_fields': len(text_vars) > 3,
            'status': 'Analysis completed successfully'
        }
    
    def get_text_results_data(self, text_data: Dict) -> Dict:
        """Extract text results data for UI consumption"""
        text_analysis = text_data.get('text_analysis', {})
        
        if text_analysis:
            # Get the first field analysis as example
            first_field = list(text_analysis.keys())[0] if text_analysis else None
            field_data = text_analysis.get(first_field, {}) if first_field else {}
            
            return {
                'has_results': True,
                'field_analyzed': first_field or 'N/A',
                'total_entries': field_data.get('total_entries', 'N/A'),
                'average_length': field_data.get('average_length', 0),
                'word_count': field_data.get('word_count', 'N/A'),
                'unique_entries': field_data.get('unique_entries', 'N/A')
            }
        else:
            return {
                'has_results': False,
                'message': 'Text analysis data processed - Results ready for detailed review'
            }
    
    def show_sentiment_analysis(self):
        """Show sentiment analysis"""
        toast("Sentiment analysis coming soon!")

    def show_theme_analysis(self):
        """Show theme analysis"""
        toast("Theme analysis coming soon!")

    def show_detailed_text_results(self, text_data):
        """Show detailed text results"""
        toast("Detailed text results view - coming soon!")

    def export_text_results(self, text_data):
        """Export text results"""
        toast("Text analysis export - coming soon!")
    

    
    def get_text_field_data(self, field_name: str, field_data: Dict) -> Dict:
        """Extract text field data for UI consumption"""
        return {
            'field_name': field_name,
            'total_entries': field_data.get('total_entries', 'N/A'),
            'average_length': field_data.get('average_length', 'N/A'),
            'word_count': field_data.get('word_count', 'N/A'),
            'unique_entries': field_data.get('unique_entries', 'N/A')
        }
    
    def get_sentiment_analysis_data(self, sentiment_results: Dict) -> Dict:
        """Extract sentiment analysis data for UI consumption"""
        sentiments = ['positive', 'neutral', 'negative']
        sentiment_data = []
        
        for sentiment in sentiments:
            sentiment_data.append({
                'name': sentiment,
                'count': sentiment_results.get(f'{sentiment}_count', 0)
            })
        
        return {
            'sentiment_distribution': sentiment_data,
            'overall_sentiment': sentiment_results.get('overall_sentiment', 'neutral'),
            'confidence': sentiment_results.get('confidence', 0),
            'total_analyzed': sentiment_results.get('total_analyzed', 0)
        }
    
    def get_theme_analysis_data(self, themes: List[Dict]) -> List[Dict]:
        """Extract theme analysis data for UI consumption"""
        theme_data = []
        
        for i, theme in enumerate(themes[:5], 1):  # Show top 5 themes
            theme_data.append({
                'number': i,
                'name': theme.get('name', f'Theme {i}'),
                'frequency': theme.get('frequency', 0)
            })
        
        return theme_data
    
    def get_word_frequency_data(self, word_frequency: Dict) -> List[Dict]:
        """Extract word frequency data for UI consumption"""
        # Sort words by frequency and show top 10
        sorted_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
        
        word_data = []
        for word, frequency in sorted_words[:10]:
            word_data.append({
                'word': word,
                'frequency': frequency
            })
        
        return word_data
    
    def run_sentiment_analysis(self, project_id: str, text_fields: List[str] = None):
        """Run sentiment analysis specifically"""
        analysis_config = {
            'analysis_type': 'sentiment',
            'text_fields': text_fields or []
        }
        
        return self.run_text_analysis(project_id, analysis_config)
    
    def run_theme_analysis(self, project_id: str, text_fields: List[str] = None, num_themes: int = 5):
        """Run theme analysis specifically"""
        analysis_config = {
            'analysis_type': 'themes',
            'text_fields': text_fields or [],
            'num_themes': num_themes
        }
        
        return self.run_text_analysis(project_id, analysis_config)

    # Analytics backend methods
    def _make_analytics_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to analytics backend"""
        try:
            import requests
            base_url = "http://127.0.0.1:8001"
            url = f"{base_url}/api/v1/analytics/qualitative/{endpoint}"
            
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'DataCollect-GUI/1.0'
            })
            
            if method == 'GET':
                response = session.get(url, timeout=30)
            elif method == 'POST':
                if data:
                    response = session.post(url, json=data, timeout=60)
                else:
                    response = session.post(url, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and 'status' in result:
                    if result['status'] == 'success':
                        return result.get('data', {})
                    else:
                        return {'error': result.get('message', 'Unknown error')}
                return result
            else:
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get('detail', f'HTTP {response.status_code}')
                    return {'error': error_msg}
                except:
                    return {'error': f'HTTP {response.status_code}: {response.text}'}
                
        except Exception as e:
            return {'error': f'Request error: {str(e)}'}

    def run_text_analysis_backend(self, project_id: str, analysis_type: str = "text", 
                                target_variables: Optional[List[str]] = None) -> Dict:
        """Run text analysis using the analytics backend"""
        try:
            params = [('analysis_type', analysis_type)]
            if target_variables and isinstance(target_variables, list):
                for var in target_variables:
                    params.append(('target_variables', var))
            elif target_variables:
                params.append(('target_variables', target_variables))
            
            url = f"project/{project_id}/analyze"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Text analysis failed: {str(e)}'}

    def run_sentiment_analysis_backend(self, project_id: str, text_fields: List[str] = None) -> Dict:
        """Run sentiment analysis specifically via backend"""
        return self.run_text_analysis_backend(project_id, "text", text_fields)

    def run_theme_analysis_backend(self, project_id: str, text_fields: List[str] = None, num_themes: int = 5) -> Dict:
        """Run theme analysis specifically via backend"""
        return self.run_text_analysis_backend(project_id, "text", text_fields)

    # COMPREHENSIVE QUALITATIVE ANALYTICS METHODS
    
    def run_sentiment_analysis_full(self, project_id: str, config: Dict = None):
        """Run comprehensive sentiment analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_sentiment_analysis_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_sentiment_analysis_thread(self, project_id: str, config: Dict):
        """Background thread for sentiment analysis"""
        try:
            text_fields = config.get('text_fields') if config else None
            sentiment_method = config.get('sentiment_method', 'vader') if config else 'vader'
            
            request_data = {
                'text_fields': text_fields,
                'sentiment_method': sentiment_method
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/sentiment', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_sentiment_results(result), 0
            )
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Sentiment analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_sentiment_results(self, results):
        """Handle sentiment analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.sentiment_results = results
        self.screen.current_analysis_type = "sentiment"
        toast("Sentiment analysis completed successfully")
    
    def run_theme_analysis_full(self, project_id: str, config: Dict = None):
        """Run comprehensive theme analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_theme_analysis_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_theme_analysis_thread(self, project_id: str, config: Dict):
        """Background thread for theme analysis"""
        try:
            text_fields = config.get('text_fields') if config else None
            num_themes = config.get('num_themes', 5) if config else 5
            theme_method = config.get('theme_method', 'lda') if config else 'lda'
            
            request_data = {
                'text_fields': text_fields,
                'num_themes': num_themes,
                'theme_method': theme_method
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/themes', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_theme_results(result), 0
            )
        except Exception as e:
            print(f"Error in theme analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Theme analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_theme_results(self, results):
        """Handle theme analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.theme_results = results
        self.screen.current_analysis_type = "themes"
        toast("Theme analysis completed successfully")
    
    def run_word_frequency_analysis(self, project_id: str, config: Dict = None):
        """Run word frequency analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_word_frequency_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_word_frequency_thread(self, project_id: str, config: Dict):
        """Background thread for word frequency analysis"""
        try:
            text_fields = config.get('text_fields') if config else None
            top_n = config.get('top_n', 50) if config else 50
            min_word_length = config.get('min_word_length', 3) if config else 3
            remove_stopwords = config.get('remove_stopwords', True) if config else True
            
            request_data = {
                'text_fields': text_fields,
                'top_n': top_n,
                'min_word_length': min_word_length,
                'remove_stopwords': remove_stopwords
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/word-frequency', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_word_frequency_results(result), 0
            )
        except Exception as e:
            print(f"Error in word frequency analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Word frequency analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_word_frequency_results(self, results):
        """Handle word frequency analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.word_frequency_results = results
        self.screen.current_analysis_type = "word_frequency"
        toast("Word frequency analysis completed successfully")
    
    def run_content_analysis(self, project_id: str, config: Dict = None):
        """Run content analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_content_analysis_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_content_analysis_thread(self, project_id: str, config: Dict):
        """Background thread for content analysis"""
        try:
            text_fields = config.get('text_fields') if config else None
            analysis_framework = config.get('analysis_framework', 'inductive') if config else 'inductive'
            coding_scheme = config.get('coding_scheme') if config else None
            
            request_data = {
                'text_fields': text_fields,
                'analysis_framework': analysis_framework,
                'coding_scheme': coding_scheme
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/content-analysis', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_content_analysis_results(result), 0
            )
        except Exception as e:
            print(f"Error in content analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Content analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_content_analysis_results(self, results):
        """Handle content analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.content_analysis_results = results
        self.screen.current_analysis_type = "content_analysis"
        toast("Content analysis completed successfully")
    
    def run_qualitative_coding(self, project_id: str, config: Dict = None):
        """Run qualitative coding analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_qualitative_coding_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_qualitative_coding_thread(self, project_id: str, config: Dict):
        """Background thread for qualitative coding"""
        try:
            text_fields = config.get('text_fields') if config else None
            coding_method = config.get('coding_method', 'open') if config else 'open'
            auto_code = config.get('auto_code', True) if config else True
            
            request_data = {
                'text_fields': text_fields,
                'coding_method': coding_method,
                'auto_code': auto_code
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/qualitative-coding', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_qualitative_coding_results(result), 0
            )
        except Exception as e:
            print(f"Error in qualitative coding: {e}")
            Clock.schedule_once(
                lambda dt: toast("Qualitative coding failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_qualitative_coding_results(self, results):
        """Handle qualitative coding results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.qualitative_coding_results = results
        self.screen.current_analysis_type = "qualitative_coding"
        toast("Qualitative coding completed successfully")
    
    def run_survey_analysis(self, project_id: str, config: Dict = None):
        """Run survey analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_survey_analysis_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_survey_analysis_thread(self, project_id: str, config: Dict):
        """Background thread for survey analysis"""
        try:
            response_fields = config.get('response_fields') if config else None
            question_metadata = config.get('question_metadata') if config else None
            
            request_data = {
                'response_fields': response_fields,
                'question_metadata': question_metadata
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/survey', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_survey_analysis_results(result), 0
            )
        except Exception as e:
            print(f"Error in survey analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Survey analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_survey_analysis_results(self, results):
        """Handle survey analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.survey_analysis_results = results
        self.screen.current_analysis_type = "survey_analysis"
        toast("Survey analysis completed successfully")
    
    def run_qualitative_statistics(self, project_id: str, config: Dict = None):
        """Run qualitative statistics"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_qualitative_statistics_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_qualitative_statistics_thread(self, project_id: str, config: Dict):
        """Background thread for qualitative statistics"""
        try:
            text_fields = config.get('text_fields') if config else None
            analysis_type = config.get('analysis_type', 'general') if config else 'general'
            
            request_data = {
                'text_fields': text_fields,
                'analysis_type': analysis_type
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/qualitative-statistics', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_qualitative_statistics_results(result), 0
            )
        except Exception as e:
            print(f"Error in qualitative statistics: {e}")
            Clock.schedule_once(
                lambda dt: toast("Qualitative statistics failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_qualitative_statistics_results(self, results):
        """Handle qualitative statistics results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.qualitative_statistics_results = results
        self.screen.current_analysis_type = "qualitative_statistics"
        toast("Qualitative statistics completed successfully")
    
    def run_sentiment_trends(self, project_id: str, config: Dict = None):
        """Run sentiment trends analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_sentiment_trends_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_sentiment_trends_thread(self, project_id: str, config: Dict):
        """Background thread for sentiment trends"""
        try:
            text_fields = config.get('text_fields') if config else None
            time_field = config.get('time_field') if config else None
            category_field = config.get('category_field') if config else None
            sentiment_method = config.get('sentiment_method', 'vader') if config else 'vader'
            
            request_data = {
                'text_fields': text_fields,
                'time_field': time_field,
                'category_field': category_field,
                'sentiment_method': sentiment_method
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/sentiment-trends', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_sentiment_trends_results(result), 0
            )
        except Exception as e:
            print(f"Error in sentiment trends: {e}")
            Clock.schedule_once(
                lambda dt: toast("Sentiment trends analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_sentiment_trends_results(self, results):
        """Handle sentiment trends results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.sentiment_trends_results = results
        self.screen.current_analysis_type = "sentiment_trends"
        toast("Sentiment trends analysis completed successfully")
    
    def run_text_similarity(self, project_id: str, config: Dict = None):
        """Run text similarity analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_text_similarity_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_text_similarity_thread(self, project_id: str, config: Dict):
        """Background thread for text similarity"""
        try:
            text_fields = config.get('text_fields') if config else None
            similarity_threshold = config.get('similarity_threshold', 0.5) if config else 0.5
            max_comparisons = config.get('max_comparisons', 100) if config else 100
            
            request_data = {
                'text_fields': text_fields,
                'similarity_threshold': similarity_threshold,
                'max_comparisons': max_comparisons
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/text-similarity', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_text_similarity_results(result), 0
            )
        except Exception as e:
            print(f"Error in text similarity: {e}")
            Clock.schedule_once(
                lambda dt: toast("Text similarity analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_text_similarity_results(self, results):
        """Handle text similarity results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.text_similarity_results = results
        self.screen.current_analysis_type = "text_similarity"
        toast("Text similarity analysis completed successfully")
    
    def run_theme_evolution(self, project_id: str, config: Dict = None):
        """Run theme evolution analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_theme_evolution_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_theme_evolution_thread(self, project_id: str, config: Dict):
        """Background thread for theme evolution"""
        try:
            text_fields = config.get('text_fields') if config else None
            time_field = config.get('time_field') if config else None
            num_themes = config.get('num_themes', 5) if config else 5
            
            request_data = {
                'text_fields': text_fields,
                'time_field': time_field,
                'num_themes': num_themes
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/theme-evolution', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_theme_evolution_results(result), 0
            )
        except Exception as e:
            print(f"Error in theme evolution: {e}")
            Clock.schedule_once(
                lambda dt: toast("Theme evolution analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_theme_evolution_results(self, results):
        """Handle theme evolution results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.theme_evolution_results = results
        self.screen.current_analysis_type = "theme_evolution"
        toast("Theme evolution analysis completed successfully")
    
    def run_quote_extraction(self, project_id: str, config: Dict = None):
        """Run quote extraction analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_quote_extraction_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_quote_extraction_thread(self, project_id: str, config: Dict):
        """Background thread for quote extraction"""
        try:
            text_fields = config.get('text_fields') if config else None
            theme_keywords = config.get('theme_keywords') if config else None
            max_quotes = config.get('max_quotes', 5) if config else 5
            auto_extract_themes = config.get('auto_extract_themes', True) if config else True
            
            request_data = {
                'text_fields': text_fields,
                'theme_keywords': theme_keywords,
                'max_quotes': max_quotes,
                'auto_extract_themes': auto_extract_themes
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/extract-quotes', 
                                                method='POST', data=request_data)
            
            Clock.schedule_once(
                lambda dt: self._handle_quote_extraction_results(result), 0
            )
        except Exception as e:
            print(f"Error in quote extraction: {e}")
            Clock.schedule_once(
                lambda dt: toast("Quote extraction failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_quote_extraction_results(self, results):
        """Handle quote extraction results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.quote_extraction_results = results
        self.screen.current_analysis_type = "quote_extraction"
        toast("Quote extraction completed successfully")

    # ANALYSIS TYPE HELPERS
    def get_analysis_types(self):
        """Get available qualitative analysis types"""
        return [
            {'id': 'text', 'name': 'Text Analysis', 'icon': 'text-box'},
            {'id': 'sentiment', 'name': 'Sentiment Analysis', 'icon': 'emoticon'},
            {'id': 'themes', 'name': 'Theme Analysis', 'icon': 'lightbulb'},
            {'id': 'word_frequency', 'name': 'Word Frequency', 'icon': 'format-list-numbered'},
            {'id': 'content_analysis', 'name': 'Content Analysis', 'icon': 'file-document-outline'},
            {'id': 'qualitative_coding', 'name': 'Qualitative Coding', 'icon': 'code-tags'},
            {'id': 'survey_analysis', 'name': 'Survey Analysis', 'icon': 'poll'},
            {'id': 'qualitative_statistics', 'name': 'Qualitative Statistics', 'icon': 'chart-bar'},
            {'id': 'sentiment_trends', 'name': 'Sentiment Trends', 'icon': 'trending-up'},
            {'id': 'text_similarity', 'name': 'Text Similarity', 'icon': 'compare'},
            {'id': 'theme_evolution', 'name': 'Theme Evolution', 'icon': 'timeline'},
            {'id': 'quote_extraction', 'name': 'Quote Extraction', 'icon': 'format-quote-close'}
        ]
    
    def get_analysis_methods(self, analysis_type: str):
        """Get analysis methods for specific type"""
        methods = {
            'sentiment': ['vader', 'textblob'],
            'themes': ['lda', 'nmf', 'clustering'],
            'content_analysis': ['inductive', 'deductive', 'mixed'],
            'qualitative_coding': ['open', 'axial', 'selective'],
            'qualitative_statistics': ['survey', 'interview', 'general']
        }
        return methods.get(analysis_type, []) 