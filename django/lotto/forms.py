from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ManualTicketForm(forms.Form):
    numbers = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': '예: 1,2,3,4,5,6',
            'class': 'form-control'
        }),
        label='번호 입력 (쉼표로 구분, 6개)'
    )

    def clean_numbers(self):
        data = self.cleaned_data['numbers']
        try:
            nums = [int(n.strip()) for n in data.split(',')]
        except ValueError:
            raise forms.ValidationError('숫자만 입력하세요.')
        if len(nums) != 6:
            raise forms.ValidationError('정확히 6개의 번호를 입력하세요.')
        if len(set(nums)) != 6:
            raise forms.ValidationError('중복된 번호가 있습니다.')
        if any(n < 1 or n > 45 for n in nums):
            raise forms.ValidationError('1~45 사이의 번호를 입력하세요.')
        return ','.join(str(n) for n in sorted(nums))
    