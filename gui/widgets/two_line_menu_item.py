from kivymd.uix.list import MDListItem
from kivy.properties import StringProperty


class TwoLineMenuItem(MDListItem):
    """Custom two-line menu item for dropdown menus"""
    
    headline = StringProperty("")
    supporting = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 