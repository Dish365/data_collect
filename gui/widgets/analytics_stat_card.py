from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.lang import Builder

Builder.load_file("kv/analytics_stat_card.kv")

class AnalyticsStatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("0")
    icon = StringProperty("chart-line")
    note = StringProperty("")

    def __init__(self, title="", value="0", icon="chart-line", note="", **kwargs):
        self.title = title
        self.value = value
        self.icon = icon
        self.note = note
        super().__init__(**kwargs) 