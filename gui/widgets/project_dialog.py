from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

Builder.load_file("kv/project_dialog.kv")

class ProjectDialog(MDBoxLayout):
    def get_data(self):
        return {
            "name": self.ids.name_field.text.strip(),
            "description": self.ids.desc_field.text.strip()
        }

    def set_data(self, name="", description="", **kwargs):
        self.ids.name_field.text = name
        self.ids.desc_field.text = description

    def reset(self):
        self.set_data()
