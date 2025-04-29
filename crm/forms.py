from django import forms

from .models import Lead, OpenHouse, OpenHouseSignIn, PropertyVisit


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "name",
            "phone_number",
            "email",
            "address",
            "lead_type",
            "source",
            "status",
            "last_contacted",
            "image",
            "notes",
        ]
        widgets = {
            "last_contacted": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == "image":
                field.widget.attrs.update({"class": "form-control-file"})
            else:
                field.widget.attrs.update({"class": "form-control"})


from django import forms

from .models import PropertyVisit


class PropertyVisitForm(forms.ModelForm):
    class Meta:
        model = PropertyVisit
        fields = ["address", "visit_date", "notes", "image", "status"]
        widgets = {
            "visit_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class OpenHouseSignInForm(forms.ModelForm):
    class Meta:
        model = OpenHouseSignIn
        fields = ["name", "phone_number", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class OpenHouseForm(forms.ModelForm):
    class Meta:
        model = OpenHouse
        fields = ["title", "address", "date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.input_type = "datetime-local"
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
