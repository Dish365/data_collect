from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/stat_card.kv")

class StatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("")
    icon = StringProperty("information")
    note = StringProperty("")
