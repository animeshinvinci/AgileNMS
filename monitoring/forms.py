from django import forms
import models


class CheckForm(forms.ModelForm):
    class Meta:
        model = models.Check
        exclude = ("uuid", )


class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        exclude = ("slug", )


class ReportForm(forms.ModelForm):
    class Meta:
        model = models.Report
        exclude = ("uuid", )
