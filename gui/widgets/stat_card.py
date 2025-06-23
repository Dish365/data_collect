from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior

Builder.load_file("kv/stat_card.kv")

class StatCard(MDCard, RectangularRippleBehavior, ButtonBehavior):
    title = StringProperty("")
    value = StringProperty("")
    icon = StringProperty("information")
    note = StringProperty("")
