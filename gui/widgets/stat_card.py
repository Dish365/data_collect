from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp

class StatCard(MDCard):
    def __init__(self, title="", value="0", icon="information", note="", **kwargs):
        super().__init__(**kwargs)
        print("StatCard initialized with title:", title, "value:", value, "icon:", icon, "note:", note)
        self.size_hint_y = None
        self.height = dp(120)
        self.radius = [12, 12, 12, 12]
        self.elevation = 0.5
        self.padding = dp(10)
        self.title = title

        layout = MDBoxLayout(orientation="horizontal", spacing=10)

        self.icon_btn = MDIconButton(
            icon=icon,
            theme_icon_color="Custom",
            icon_color=(0.1, 0.4, 0.8, 1),
            user_font_size="32sp"
        )

        text_col = MDBoxLayout(orientation="vertical", spacing=2)
        self.value_label = MDLabel(text=value, font_style="H5", bold=True, theme_text_color="Custom", text_color=(0, 0, 0, 1))
        self.title_label = MDLabel(text=title, font_style="Caption", theme_text_color="Secondary")
        self.note_label = MDLabel(text=note, font_style="Caption", theme_text_color="Hint")

        text_col.add_widget(self.value_label)
        text_col.add_widget(self.title_label)
        text_col.add_widget(self.note_label)

        layout.add_widget(self.icon_btn)
        layout.add_widget(text_col)
        self.add_widget(layout)

    @property
    def value(self):
        return self.value_label.text

    @value.setter
    def value(self, val):
        self.value_label.text = val
