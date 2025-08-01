from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

# Load the KV file
# KV file loaded by main app after theme initialization


class ChartWidget(MDCard):
    """Modern chart widget using KivyMD 2.0.1 Material Design"""
    
    chart_type = StringProperty('bar')
    title = StringProperty('')
    subtitle = StringProperty('')
    data = ObjectProperty()
    
    def __init__(self, chart_type='bar', data=None, title='', subtitle='', **kwargs):
        super().__init__(**kwargs)
        self.chart_type = chart_type
        self.data = data
        self.title = title
        self.subtitle = subtitle
        
        # Setup responsive properties
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # Set matplotlib style for better appearance
        try:
            style.use('seaborn-v0_8')  # Modern seaborn style
        except:
            try:
                style.use('seaborn')  # Fallback for older versions
            except:
                pass  # Use default style
        
        # Create figure with better default settings
        self.figure = plt.figure(figsize=(10, 6), facecolor='white')
        self.canvas = FigureCanvasKivyAgg(self.figure)
        
        # Bind properties
        self.bind(title=self._update_title)
        self.bind(subtitle=self._update_subtitle)
        self.bind(data=self._update_data)
        self.bind(chart_type=self._update_chart_type)
        
        # Create chart based on type
        if data is not None:
            self.create_chart()
    
    def _on_window_resize(self, *args):
        """Handle window resize for responsive updates"""
        self.update_responsive_properties()
    
    def update_responsive_properties(self):
        """Update properties based on screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Responsive sizing based on device category
            if category == "large_tablet":
                self.height = dp(500)
                self.padding = [dp(20), dp(16)]
                self.spacing = dp(16)
            elif category == "tablet":
                self.height = dp(450)
                self.padding = [dp(16), dp(12)]
                self.spacing = dp(14)
            elif category == "small_tablet":
                self.height = dp(400)
                self.padding = [dp(14), dp(10)]
                self.spacing = dp(12)
            else:  # phone
                self.height = dp(350)
                self.padding = [dp(12), dp(8)]
                self.spacing = dp(10)
                
        except Exception as e:
            print(f"Error updating ChartWidget responsive properties: {e}")
            # Fallback to default values
            self.height = dp(350)
            self.padding = [dp(12), dp(8)]
            self.spacing = dp(10)
    
    def _update_title(self, instance, value):
        """Update title in UI"""
        if hasattr(self, 'title_label'):
            self.title_label.text = value
    
    def _update_subtitle(self, instance, value):
        """Update subtitle in UI"""
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.text = value
    
    def _update_data(self, instance, value):
        """Update data and recreate chart"""
        self.data = value
        self.create_chart()
    
    def _update_chart_type(self, instance, value):
        """Update chart type and recreate chart"""
        self.chart_type = value
        self.create_chart()
    
    def create_chart(self):
        """Create chart based on type and data."""
        if not self.data:
            return
            
        self.figure.clear()
        
        if self.chart_type == 'bar':
            self._create_bar_chart()
        elif self.chart_type == 'histogram':
            self._create_histogram()
        elif self.chart_type == 'box':
            self._create_box_plot()
        elif self.chart_type == 'scatter':
            self._create_scatter_plot()
        elif self.chart_type == 'correlation_heatmap':
            self._create_correlation_heatmap()
        elif self.chart_type == 'stats_table':
            self._create_stats_table()
        elif self.chart_type == 'pie':
            self._create_pie_chart()
        elif self.chart_type == 'line':
            self._create_line_chart()
        else:
            self._create_bar_chart()  # Default fallback
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _create_bar_chart(self):
        """Create an enhanced bar chart."""
        ax = self.figure.add_subplot(111)
        
        if isinstance(self.data, dict):
            categories = list(self.data.keys())
            values = list(self.data.values())
        else:
            categories = range(len(self.data))
            values = self.data
        
        # Create colorful bars
        colors = plt.cm.Set3(np.linspace(0, 1, len(values)))
        bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=1)
        
        # Customize appearance
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Distribution', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Rotate x-axis labels if needed
        if len(categories) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:  # Only show labels for non-zero bars
                ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + max(values) * 0.01,
                    f'{int(height)}',
                    ha='center',
                    va='bottom',
                    fontsize=10
                )
    
    def _create_histogram(self):
        """Create a histogram for continuous data."""
        ax = self.figure.add_subplot(111)
        
        # Flatten data if needed
        if isinstance(self.data, dict):
            values = []
            for v in self.data.values():
                if isinstance(v, (list, tuple, np.ndarray)):
                    values.extend(v)
                else:
                    values.append(v)
        else:
            values = self.data
        
        # Remove None values
        values = [v for v in values if v is not None and not np.isnan(v) if isinstance(v, (int, float))]
        
        if not values:
            ax.text(0.5, 0.5, 'No numeric data available', 
                   transform=ax.transAxes, ha='center', va='center')
            return
        
        n_bins = min(30, max(10, len(values) // 10))  # Adaptive bin count
        
        ax.hist(values, bins=n_bins, alpha=0.7, color='skyblue', edgecolor='navy')
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_xlabel('Value', fontsize=12)
        ax.set_title('Data Distribution', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
    
    def _create_box_plot(self):
        """Create a box plot for outlier visualization."""
        ax = self.figure.add_subplot(111)
        
        if isinstance(self.data, dict):
            plot_data = []
            labels = []
            for key, values in self.data.items():
                if isinstance(values, (list, tuple, np.ndarray)) and len(values) > 0:
                    # Remove None values
                    clean_values = [v for v in values if v is not None and not np.isnan(v) if isinstance(v, (int, float))]
                    if clean_values:
                        plot_data.append(clean_values)
                        labels.append(key)
        else:
            plot_data = [self.data] if self.data else []
            labels = ['Data']
        
        if not plot_data:
            ax.text(0.5, 0.5, 'No numeric data for box plot', 
                   transform=ax.transAxes, ha='center', va='center')
            return
        
        bp = ax.boxplot(plot_data, labels=labels, patch_artist=True)
        
        # Color the boxes
        colors = plt.cm.Set2(np.linspace(0, 1, len(plot_data)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title('Box Plot - Outlier Detection', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        if len(labels) > 3:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _create_correlation_heatmap(self):
        """Create a correlation matrix heatmap."""
        ax = self.figure.add_subplot(111)
        
        if not isinstance(self.data, dict):
            ax.text(0.5, 0.5, 'Invalid data for correlation heatmap', 
                   transform=ax.transAxes, ha='center', va='center')
            return
        
        # Convert correlation data to matrix format
        variables = list(self.data.keys())
        matrix = np.zeros((len(variables), len(variables)))
        
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                corr_value = self.data.get(var1, {}).get(var2, 0)
                if corr_value is not None:
                    matrix[i, j] = corr_value
        
        # Create heatmap
        im = ax.imshow(matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
        
        # Add colorbar
        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient', fontsize=12)
        
        # Set labels
        ax.set_xticks(range(len(variables)))
        ax.set_yticks(range(len(variables)))
        ax.set_xticklabels(variables, rotation=45, ha='right')
        ax.set_yticklabels(variables)
        
        # Add correlation values as text
        for i in range(len(variables)):
            for j in range(len(variables)):
                ax.text(j, i, f'{matrix[i, j]:.2f}', 
                       ha='center', va='center', 
                       color='white' if abs(matrix[i, j]) > 0.5 else 'black')
        
        ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
    
    def _create_stats_table(self):
        """Create a statistical summary table."""
        ax = self.figure.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        if not isinstance(self.data, dict):
            ax.text(0.5, 0.5, 'Invalid data for statistics table', 
                   transform=ax.transAxes, ha='center', va='center')
            return
        
        # Prepare table data
        table_data = []
        for stat, value in self.data.items():
            if isinstance(value, (int, float)):
                if value == int(value):
                    formatted_value = f'{int(value)}'
                else:
                    formatted_value = f'{value:.3f}'
            else:
                formatted_value = str(value)
            table_data.append([stat.replace('_', ' ').title(), formatted_value])
        
        if not table_data:
            ax.text(0.5, 0.5, 'No statistics available', 
                   transform=ax.transAxes, ha='center', va='center')
            return
        
        # Create table
        table = ax.table(
            cellText=table_data,
            colLabels=['Statistic', 'Value'],
            loc='center',
            cellLoc='center'
        )
        
        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)
        
        # Color header
        for i in range(len(table_data[0])):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, len(table_data) + 1):
            if i % 2 == 0:
                for j in range(len(table_data[0])):
                    table[(i, j)].set_facecolor('#f0f0f0')
        
        ax.set_title('Statistical Summary', fontsize=14, fontweight='bold', pad=20)
    
    def _create_pie_chart(self):
        """Create a pie chart for categorical data."""
        ax = self.figure.add_subplot(111)
        
        if isinstance(self.data, dict):
            labels = list(self.data.keys())
            sizes = list(self.data.values())
        else:
            ax.text(0.5, 0.5, 'Invalid data for pie chart', 
                   transform=ax.transAxes, ha='center', va='center')
            return
        
        # Filter out zero values
        filtered_data = [(label, size) for label, size in zip(labels, sizes) if size > 0]
        if not filtered_data:
            ax.text(0.5, 0.5, 'No data for pie chart', 
                   transform=ax.transAxes, ha='center', va='center')
            return
        
        labels, sizes = zip(*filtered_data)
        
        # Create pie chart with enhanced styling
        colors = plt.cm.Set3(np.linspace(0, 1, len(sizes)))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90,
                                         wedgeprops=dict(edgecolor='white', linewidth=2))
        
        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Distribution', fontsize=14, fontweight='bold')
    
    def _create_line_chart(self):
        """Create a line chart for time series or sequential data."""
        ax = self.figure.add_subplot(111)
        
        if isinstance(self.data, dict):
            for label, values in self.data.items():
                if isinstance(values, (list, tuple, np.ndarray)):
                    ax.plot(values, label=label, marker='o', linewidth=2, markersize=4)
                else:
                    ax.plot([values], label=label, marker='o', linewidth=2, markersize=6)
            ax.legend()
        else:
            ax.plot(self.data, marker='o', linewidth=2, markersize=4, color='#2196F3')
        
        ax.set_ylabel('Value', fontsize=12)
        ax.set_xlabel('Index', fontsize=12)
        ax.set_title('Trend Analysis', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    def update_data(self, new_data, chart_type=None):
        """Update chart with new data."""
        self.data = new_data
        if chart_type:
            self.chart_type = chart_type
        self.create_chart()
    
    def export_data(self, instance):
        """Export chart data and image."""
        try:
            # Save the figure
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chart_export_{timestamp}.png"
            
            self.figure.savefig(filename, dpi=300, bbox_inches='tight', 
                              facecolor='white', edgecolor='none')
            
            print(f"Chart exported to {filename}")
            
            # Also save data if available
            if self.data:
                import json
                data_filename = f"chart_data_{timestamp}.json"
                with open(data_filename, 'w') as f:
                    json.dump(self.data, f, indent=2, default=str)
                print(f"Data exported to {data_filename}")
            
        except Exception as e:
            print(f"Export failed: {e}")
    
    @staticmethod
    def create_analytics_chart(chart_type: str, data: Any, title: str = "", subtitle: str = ""):
        """Static method to create analytics charts."""
        return ChartWidget(
            chart_type=chart_type,
            data=data,
            title=title,
            subtitle=subtitle,
            size_hint_y=None,
            height=dp(400)
        ) 