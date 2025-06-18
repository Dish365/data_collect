from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.boxlayout import BoxLayout 
from kivy.metrics import dp


class ShortTextField(MDCard):
    question_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 10
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.height = dp(120)
        self.md_bg_color = (0.98, 0.98, 0.98, 1)

        self.label = MDLabel(
            text=self.question_text,
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=30
        )

        self.text_input = MDTextField(
            hint_text="Short text answer",
            mode="rectangle",
            size_hint_y=None,
            height=48
        )

        self.add_widget(self.label)
        self.add_widget(self.text_input)


class MultipleChoiceField(MDCard):
    question_text = StringProperty("")
    options = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 10
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.height = dp(120)
        self.md_bg_color = (0.98, 0.98, 0.98, 1)

        self.label = MDLabel(
            text=self.question_text,
            theme_text_color="Primary",
            font_style="Subtitle1",
            size_hint_y=None,
            height=30
        )

        self.add_widget(self.label)

        for option in self.options:
            row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
            checkbox = MDCheckbox(size_hint=(None, None), size=("24dp", "24dp"))
            label = MDLabel(text=option, halign="left", theme_text_color="Primary")
            row.add_widget(checkbox)
            row.add_widget(label)
            self.add_widget(row)

class LongTextField(MDCard):
    question_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 10
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.height = dp(120)
        self.md_bg_color = (0.98, 0.98, 0.98, 1)

        self.label = MDLabel(
            text=self.question_text,
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        self.text_input = MDTextField(
            hint_text="Long text answer",
            multiline=True,
            mode="rectangle",
            height=100,
            size_hint_y=None
        )

        self.add_widget(self.label)
        self.add_widget(self.text_input)


class DateField(MDCard):
    question_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 10
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.height = dp(120)
        self.md_bg_color = (0.98, 0.98, 0.98, 1)

        self.label = MDLabel(
            text=self.question_text,
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        self.date_input = MDTextField(
            hint_text="Select date",
            mode="rectangle",
            on_focus=self.show_date_picker
        )

        self.add_widget(self.label)
        self.add_widget(self.date_input)


    def set_date(self, instance, date_obj, *_):
        self.date_input.text = str(date_obj)

class LocationPickerField(MDCard):
    question_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 10
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.height = dp(120)
        self.md_bg_color = (0.98, 0.98, 0.98, 1)

        self.label = MDLabel(
            text=self.question_text,
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        self.input = MDTextField(
            hint_text="Tap to pick location",
            mode="rectangle"
        )

        self.add_widget(self.label)
        self.add_widget(self.input)


from kivymd.uix.button import MDRaisedButton

class PhotoUploadField(MDCard):
    question_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 10
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.height = dp(120)
        self.md_bg_color = (0.98, 0.98, 0.98, 1)

        self.label = MDLabel(
            text=self.question_text,
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        self.upload_button = MDRaisedButton(
            text="Upload Photo",
            on_release=self.pick_image
        )

        self.add_widget(self.label)
        self.add_widget(self.upload_button)

    def pick_image(self, instance):
        # implement using plyer.filechooser or camera for mobile
        print("Photo picker triggered")


class RatingScaleField(MDCard):
    question_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 10
        self.radius = [12, 12, 12, 12]
        self.size_hint_y = None
        self.height = self.minimum_height
        self.md_bg_color = (0.98, 0.98, 0.98, 1)

        self.label = MDLabel(
            text=self.question_text,
            theme_text_color="Primary",
            font_style="Subtitle1"
        )

        self.rating_row = BoxLayout(orientation='horizontal', spacing=8)
        for i in range(5):
            self.rating_row.add_widget(MDCheckbox(group="rating"))

        self.add_widget(self.label)
        self.add_widget(self.rating_row)
