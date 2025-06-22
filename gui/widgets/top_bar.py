from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def set_title(self, text):
        self.ids.top_title.text = text
