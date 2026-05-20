from django import forms
from django.conf import settings
import os


class UploadForm(forms.Form):
    word_file = forms.FileField(
        label='Fichier Word (.docx/.doc)',
        help_text='Fichier Word contenant les tableaux de cas de tests',
        widget=forms.ClearableFileInput(attrs={'accept': '.docx,.doc'})
    )
    excel_template = forms.FileField(
        label='Template Excel (optionnel)',
        required=False,
        help_text='Template Excel personnalisé (.xlsx)',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'})
    )

    def clean_word_file(self):
        f = self.cleaned_data['word_file']
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in settings.ALLOWED_WORD_EXTENSIONS:
            raise forms.ValidationError(
                f"Format non supporté. Formats acceptés : {', '.join(settings.ALLOWED_WORD_EXTENSIONS)}"
            )
        if f.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
            raise forms.ValidationError(f"Fichier trop volumineux. Taille maximale : {max_mb} MB")
        return f

    def clean_excel_template(self):
        f = self.cleaned_data.get('excel_template')
        if f:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in settings.ALLOWED_EXCEL_EXTENSIONS:
                raise forms.ValidationError(
                    f"Format non supporté. Formats acceptés : {', '.join(settings.ALLOWED_EXCEL_EXTENSIONS)}"
                )
        return f
