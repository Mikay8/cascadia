"""Forms for the login and MFA views."""

from django import forms


class TOTPTokenForm(forms.Form):
    """A single 6-digit code from the user's authenticator app."""

    token = forms.CharField(
        label="Authenticator code",
        max_length=8,
        strip=True,
        widget=forms.TextInput(attrs={"autocomplete": "one-time-code", "inputmode": "numeric"}),
    )

    def clean_token(self) -> str:
        token = self.cleaned_data["token"].replace(" ", "")
        if not token.isdigit():
            raise forms.ValidationError("Enter the 6-digit code from your authenticator app.")
        return token
