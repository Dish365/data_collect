from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

class StatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("")
    icon = StringProperty("information")
    note = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(120)
        self.radius = [12, 12, 12, 12]
        self.elevation = 0.5
        self.padding = dp(10)

        self.layout = MDBoxLayout(orientation="horizontal", spacing=10)

        self.icon_btn = MDIconButton(
            icon=self.icon,
            theme_icon_color="Custom",
            icon_color=(0.1, 0.4, 0.8, 1),
            user_font_size="32sp"
        )

        text_col = MDBoxLayout(orientation="vertical", spacing=2)
        self.value_label = MDLabel(text=self.value, font_style="H5", bold=True, theme_text_color="Custom", text_color=(0, 0, 0, 1))
        self.title_label = MDLabel(text=self.title, font_style="Caption", theme_text_color="Secondary")
        self.note_label = MDLabel(text=self.note, font_style="Caption", theme_text_color="Hint")

        text_col.add_widget(self.value_label)
        text_col.add_widget(self.title_label)
        text_col.add_widget(self.note_label)

        self.layout.add_widget(self.icon_btn)
        self.layout.add_widget(text_col)
        self.add_widget(self.layout)

        # Bind properties
        self.bind(value=self.update_value)
        self.bind(title=self.update_title)
        self.bind(note=self.update_note)
        self.bind(icon=self.update_icon)

    def update_value(self, instance, value):
        self.value_label.text = value

    def update_title(self, instance, title):
        self.title_label.text = title

    def update_note(self, instance, note):
        self.note_label.text = note

    def update_icon(self, instance, icon):
        self.icon_btn.icon = icon
