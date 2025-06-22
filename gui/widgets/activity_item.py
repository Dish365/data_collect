from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/activity_item.kv")

class ActivityItem(MDCard):
    activity_text = StringProperty("")
    activity_time = StringProperty("")
    activity_icon = StringProperty("information") 