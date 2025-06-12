from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import StringProperty

class StatCard(BoxLayout):
    title = StringProperty('')
    value = StringProperty('0')
    icon = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(100)
        
        # Icon and title
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30)
        )
        
        icon_label = Label(
            text=self.icon,
            size_hint_x=None,
            width=dp(30),
            font_size=dp(20)
        )
        header.add_widget(icon_label)
        
        title_label = Label(
            text=self.title,
            size_hint_x=None,
            width=dp(120),
            font_size=dp(16)
        )
        header.add_widget(title_label)
        
        self.add_widget(header)
        
        # Value
        value_label = Label(
            text=self.value,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(24)
        )
        self.add_widget(value_label)
        
        # Bind properties
        self.bind(value=value_label.setter('text'))
        self.bind(title=title_label.setter('text'))
        self.bind(icon=icon_label.setter('text')) 