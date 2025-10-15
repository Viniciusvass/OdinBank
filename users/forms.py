from django import forms
from .models import SolicitacaoCredito

class SolicitacaoCreditoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoCredito
        fields = ['valor', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }
