from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import QuoteRequest, QuoteProduct, CardJobOrder


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


class CardJobOrderClientForm(forms.ModelForm):
    class Meta:
        model = CardJobOrder
        fields = [
            'requester_name', 'requester_email', 'requester_phone', 'requester_cuit',
            'job_description', 'op_anterior', 'version', 'front_colors',
            'front_special_colors', 'front_observations', 'back_colors',
            'back_special_colors', 'back_observations', 'attached_file', 'general_notes'
        ]

    def clean_attached_file(self):
        file = self.cleaned_data.get('attached_file')
        if not file:
            return file
        max_size_mb = 10
        if file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"El archivo sobrepasa el límite máximo de {max_size_mb} MB.")
        allowed_mime_types = ['application/pdf', 'image/jpeg', 'image/png']
        if hasattr(file, 'content_type'):
            if file.content_type not in allowed_mime_types:
                raise ValidationError("Solo se permiten archivos PDF, JPG o PNG.")
        return file


class CardJobOrderStaffForm(forms.ModelForm):
    class Meta:
        model = CardJobOrder
        fields = [
            'uv', 'uv_type', 'uv_size', 'uv_front', 'uv_back',
            'antenna_inlay', 'magnetic_band', 'magnetic_band_type',
            'magnetic_band_size', 'magnetic_band_back', 'lamination',
            'lamination_type', 'lamination_front', 'lamination_back',
            'signature_panel', 'hologram', 'stamping', 'chip', 'pre_perso',
            'variable_data', 'review_result', 'approved_by', 'approval_date',
            'order_number', 'bin_number', 'pif_rpp', 'ica_number', 'status',
            'assigned_to'
        ]
        widgets = {
            'approval_date': forms.DateInput(attrs={'type': 'date'}),
        }
