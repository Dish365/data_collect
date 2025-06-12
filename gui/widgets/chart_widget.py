from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.metrics import dp
import matplotlib.pyplot as plt
import numpy as np

class ChartWidget(BoxLayout):
    def __init__(self, chart_type='bar', data=None, title='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # Add title
        title_label = Label(
            text=title,
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16)
        )
        self.add_widget(title_label)
        
        # Create figure
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvasKivyAgg(self.figure)
        self.add_widget(self.canvas)
        
        # Create chart based on type
        if chart_type == 'bar':
            self._create_bar_chart(data)
        elif chart_type == 'stats':
            self._create_stats_chart(data)
        
        # Add export button
        export_button = Button(
            text='Export Data',
            size_hint_y=None,
            height=dp(40),
            on_press=self.export_data
        )
        self.add_widget(export_button)
    
    def _create_bar_chart(self, data):
        # Clear figure
        self.figure.clear()
        
        # Create bar chart
        ax = self.figure.add_subplot(111)
        categories = list(data.keys())
        values = list(data.values())
        
        # Create bar chart
        bars = ax.bar(categories, values)
        
        # Customize chart
        ax.set_ylabel('Count')
        ax.set_title('Response Distribution')
        
        # Rotate x-axis labels if needed
        if len(categories) > 5:
            plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom'
            )
        
        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _create_stats_chart(self, data):
        # Clear figure
        self.figure.clear()
        
        # Create table
        ax = self.figure.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare data for table
        table_data = []
        for stat, value in data.items():
            if isinstance(value, (int, float)):
                table_data.append([stat, f'{value:.2f}'])
            else:
                table_data.append([stat, str(value)])
        
        # Create table
        table = ax.table(
            cellText=table_data,
            loc='center',
            cellLoc='center'
        )
        
        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def export_data(self, instance):
        # TODO: Implement data export functionality
        pass 