from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder

Builder.load_file("kv/activity_item.kv")

class ActivityItem(MDCard):
    activity_text = StringProperty("")
    activity_time = StringProperty("")
    activity_icon = StringProperty("information")
    is_team_activity = BooleanProperty(False)
    activity_type = StringProperty("")
    
    def __init__(self, activity_text="", activity_time="", activity_icon="information", activity_type="", **kwargs):
        super().__init__(**kwargs)
        self.activity_text = activity_text
        self.activity_time = activity_time
        self.activity_icon = activity_icon
        self.activity_type = activity_type
        self.is_team_activity = activity_type == 'team_member' 