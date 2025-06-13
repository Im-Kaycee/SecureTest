from django import forms
from .models import ExamQuestion

class ExamQuestionForm(forms.ModelForm):
    question_text = forms.CharField()
    option_a = forms.CharField()
    option_b = forms.CharField()
    option_c = forms.CharField()
    option_d = forms.CharField()
    correct_option = forms.CharField()

    class Meta:
        model = ExamQuestion
        fields = ['exam', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['question_text'].initial = self.instance.question_text
            self.fields['option_a'].initial = self.instance.option_a
            self.fields['option_b'].initial = self.instance.option_b
            self.fields['option_c'].initial = self.instance.option_c
            self.fields['option_d'].initial = self.instance.option_d
            self.fields['correct_option'].initial = self.instance.correct_option

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.question_text = self.cleaned_data['question_text']
        instance.option_a = self.cleaned_data['option_a']
        instance.option_b = self.cleaned_data['option_b']
        instance.option_c = self.cleaned_data['option_c']
        instance.option_d = self.cleaned_data['option_d']
        instance.correct_option = self.cleaned_data['correct_option']
        if commit:
            instance.save()
        return instance