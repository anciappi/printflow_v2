from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import QuoteRequest, QuoteProduct


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = [
            'requester_name', 'requester_email', 'requester_phone', 'requester_cuit',
            'billing_address', 'billing_city',
            'same_as_billing', 'delivery_address', 'delivery_city', 'delivery_contact', 'delivery_phone',
            'attached_file', 'general_notes'
        ]

    def clean_attached_file(self):
        file = self.cleaned_data.get('attached_file')
        if not file:
            return file

        # Limit to 10MB
        max_size_mb = 10
        if file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"El archivo sobrepasa el límite máximo de {max_size_mb} MB.")

        # Validate MIME type
        allowed_mime_types = [
            'application/pdf',
            'image/jpeg',
            'image/png'
        ]
        
        # Django uploaded files have content_type attribute
        if hasattr(file, 'content_type'):
            if file.content_type not in allowed_mime_types:
                raise ValidationError("Solo se permiten archivos PDF, JPG o PNG.")
                
        return file


QuoteProductFormSet = inlineformset_factory(
    QuoteRequest,
    QuoteProduct,
    fields=['product', 'quantity', 'notes'],
    extra=1,
    can_delete=True
)
