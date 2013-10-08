from django import forms
import models


class CheckForm(forms.ModelForm):
    class Meta:
        model = models.Check
        exclude = ("uuid", )


class ReportForm(forms.ModelForm):
    class Meta:
        model = models.Report
        exclude = ("uuid", )
