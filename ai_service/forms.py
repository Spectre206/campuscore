from django import forms


class QuizGenerationForm(forms.Form):
    topic = forms.CharField(
        label='Topic or material',
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        required=True,
    )
    num_questions = forms.ChoiceField(
        label='Number of questions',
        choices=[(3, '3'), (5, '5'), (10, '10')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
    )
