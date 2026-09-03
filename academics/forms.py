from django import forms
from django.forms import modelformset_factory

from .models import Assessment, AttendanceRecord, AttendanceSession


class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['date', 'title']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Optional title'}
            ),
        }


AttendanceRecordFormSet = modelformset_factory(
    AttendanceRecord,
    fields=['status', 'remarks'],
    extra=0,
    widgets={
        'status': forms.Select(attrs={'class': 'form-select'}),
        'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
    },
)


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['name', 'type', 'total_marks', 'date']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'e.g., Midterm Exam'}
            ),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
