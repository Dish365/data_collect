from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.selectioncontrol import MDCheckbox



class QuestionBlock(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(12)
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        self.md_bg_color = (0.98, 0.98, 0.98, 1)
        self.elevation = 0.8

        self.options_widgets = []
        self.allow_multiple = False

        # Question Input
        self.question_input = MDTextField(
            hint_text="Enter your question",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )

        # Dropdown menu
        self.answer_type = "Short Answer"
        self.menu_items = [
            {"text": "Short Answer", "on_release": lambda x="Short Answer": self.set_answer_type(x)},
            {"text": "Long Answer", "on_release": lambda x="Long Answer": self.set_answer_type(x)},
            {"text": "Multiple Choice", "on_release": lambda x="Multiple Choice": self.set_answer_type(x)},
        ]

        self.menu = MDDropdownMenu(
            caller=None,
            items=self.menu_items,
            width_mult=4
        )

        self.type_button = MDRaisedButton(
            text=self.answer_type,
            on_release=self.open_menu,
            size_hint=(None, None),
            size=(dp(160), dp(36))
        )

        # Top row: question + type
        top_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48)
        )
        top_row.add_widget(self.question_input)
        top_row.add_widget(self.type_button)

        # Answer area (dynamic content)
        self.answer_area = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )
        self.answer_area.bind(minimum_height=self.answer_area.setter("height"))

        # Footer row: delete button right aligned
        footer = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40)
        )
        footer.add_widget(Widget())  # spacer
        footer.add_widget(MDRaisedButton(
            text="Delete Question",
            md_bg_color=(1, 0.3, 0.3, 1),
            on_release=lambda x: self.parent.remove_widget(self),
            size_hint=(None, None),
            size=(dp(160), dp(36))
        ))

        # Assemble card
        self.add_widget(top_row)
        self.add_widget(self.answer_area)
        self.add_widget(footer)

        self.set_answer_type(self.answer_type)

    def open_menu(self, instance):
        self.menu.caller = instance
        self.menu.open()

    def set_answer_type(self, answer_type):
        self.answer_type = answer_type
        self.type_button.text = answer_type
        self.answer_area.clear_widgets()

        if answer_type == "Short Answer":
            self.answer_area.add_widget(MDTextField(hint_text="Short answer preview", mode="rectangle"))

        elif answer_type == "Long Answer":
            self.answer_area.add_widget(MDTextField(hint_text="Long answer preview", multiline=True, mode="rectangle"))

        elif answer_type == "Multiple Choice":
            self.options_widgets = []
            self.options_box = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
            self.options_box.bind(minimum_height=self.options_box.setter("height"))
            self.options_box.size_hint_y = None
            self.options_box.bind(minimum_height=self.options_box.setter("height"))
            self.add_option()
            self.add_option()

            add_option_btn = MDRaisedButton(
                text="Add Option",
                size_hint=(None, None),
                size=(dp(120), dp(36)),
                on_release=self.add_option
            )

            toggle_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(40)
            )
            toggle_label = MDLabel(
                text="Allow multiple answers",
                size_hint_x=None,
                width=dp(200)
            )
            self.toggle_switch = MDSwitch(
                active=False,
                on_active=self.toggle_multiple
            )
            toggle_layout.add_widget(toggle_label)
            toggle_layout.add_widget(self.toggle_switch)

            self.answer_area.add_widget(self.options_box)
            self.answer_area.add_widget(add_option_btn)
            self.answer_area.add_widget(toggle_layout)

    def toggle_multiple(self, instance, value):
        self.allow_multiple = value

    def add_option(self, *args):
        box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        option_input = MDTextField(hint_text="Option", mode="rectangle")
        delete_btn = MDIconButton(
            icon="close",
            on_release=lambda x: self.remove_option(box)
        )
        box.add_widget(option_input)
        box.add_widget(delete_btn)
        self.options_widgets.append(option_input)
        self.options_box.add_widget(box)
        self.options_box.height = self.options_box.minimum_height

    def remove_option(self, widget):
        self.options_box.remove_widget(widget)
        self.options_widgets = [w for w in self.options_widgets if w != widget]

    def to_dict(self):
        return {
            "question": self.question_input.text.strip(),
            "type": self.answer_type,
            "options": [w.text.strip() for w in self.options_widgets] if self.answer_type == "Multiple Choice" else [],
            "allow_multiple": bool(self.allow_multiple)
        }

    def render_preview(self):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.label import MDLabel

        preview = MDBoxLayout(orientation="vertical", spacing=dp(8))
        preview.add_widget(MDLabel(text=self.question_input.text, font_style="Subtitle1"))

        if self.answer_type == "Short Answer":
            preview.add_widget(MDTextField(hint_text="Short answer", mode="rectangle"))

        elif self.answer_type == "Long Answer":
            preview.add_widget(MDTextField(hint_text="Long answer", multiline=True, mode="rectangle"))

        elif self.answer_type == "Multiple Choice":
            option_class = MDCheckbox 
            for opt in self.options_widgets:
                row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(40))
                row.add_widget(option_class(size_hint=(None, None), size=(dp(36), dp(36))))
                row.add_widget(MDLabel(text=opt.text))
                preview.add_widget(row)

        return preview
