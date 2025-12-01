import re
from datetime import date, timedelta

from django import forms
from django.core.exceptions import ValidationError

from .models import ClientePersona, Direccion, MetodoPago
from .utils import formatear_rut, validar_rut


class ClientePerfilForm(forms.ModelForm):
    """Formulario para editar información personal del cliente"""

    class Meta:
        model = ClientePersona
        fields = [
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "email",
            "telefono",
            "fecha_nacimiento",
        ]
        widgets = {
            "nombres": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombres",
                    "maxlength": "25",
                }
            ),
            "apellido_paterno": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Apellido Paterno",
                    "maxlength": "25",
                }
            ),
            "apellido_materno": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Apellido Materno",
                    "maxlength": "25",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "correo@ejemplo.com",
                    "maxlength": "50",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "912345678",
                    "maxlength": "10",
                }
            ),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }
        labels = {
            "nombres": "Nombres",
            "apellido_paterno": "Apellido Paterno",
            "apellido_materno": "Apellido Materno",
            "email": "Correo Electrónico",
            "telefono": "Teléfono",
            "fecha_nacimiento": "Fecha de Nacimiento",
        }

    def __init__(self, *args, **kwargs):
        self.instance_id = kwargs.pop("instance_id", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Verificar si el email ya existe para otro cliente
            qs = ClientePersona.objects.filter(email=email)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if telefono:
            # Validar que solo contenga dígitos
            if not telefono.isdigit():
                raise ValidationError("El teléfono debe contener solo números.")
            if len(telefono) < 9:
                raise ValidationError("El teléfono debe tener al menos 9 dígitos.")
        return telefono

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha:
            hoy = date.today()
            edad = (
                hoy.year
                - fecha.year
                - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
            )
            if edad < 18:
                raise ValidationError("Debes ser mayor de 18 años.")
            if fecha > hoy:
                raise ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha


class DireccionForm(forms.ModelForm):
    """Formulario para agregar/editar direcciones del cliente"""

    class Meta:
        model = Direccion
        fields = ["calle", "ciudad", "region", "codigo_postal", "telefono"]
        widgets = {
            "calle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Av. Libertador 1234, Depto 501",
                    "maxlength": "50",
                }
            ),
            "ciudad": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Santiago",
                    "maxlength": "50",
                }
            ),
            "region": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("", "Seleccione una región"),
                    ("Región de Arica y Parinacota", "Región de Arica y Parinacota"),
                    ("Región de Tarapacá", "Región de Tarapacá"),
                    ("Región de Antofagasta", "Región de Antofagasta"),
                    ("Región de Atacama", "Región de Atacama"),
                    ("Región de Coquimbo", "Región de Coquimbo"),
                    ("Región de Valparaíso", "Región de Valparaíso"),
                    ("Región Metropolitana", "Región Metropolitana"),
                    (
                        "Región del Libertador General Bernardo O'Higgins",
                        "Región del Libertador General Bernardo O'Higgins",
                    ),
                    ("Región del Maule", "Región del Maule"),
                    ("Región de Ñuble", "Región de Ñuble"),
                    ("Región del Biobío", "Región del Biobío"),
                    ("Región de La Araucanía", "Región de La Araucanía"),
                    ("Región de Los Ríos", "Región de Los Ríos"),
                    ("Región de Los Lagos", "Región de Los Lagos"),
                    ("Región de Aysén", "Región de Aysén"),
                    ("Región de Magallanes", "Región de Magallanes"),
                ],
            ),
            "codigo_postal": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: 8320000",
                    "min": "1000000",
                    "max": "9999999",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "912345678",
                    "maxlength": "10",
                }
            ),
        }
        labels = {
            "calle": "Dirección",
            "ciudad": "Ciudad",
            "region": "Región",
            "codigo_postal": "Código Postal",
            "telefono": "Teléfono de Contacto",
        }

    def clean_calle(self):
        calle = self.cleaned_data.get("calle")
        if calle and len(calle.strip()) < 5:
            raise ValidationError("La dirección debe tener al menos 5 caracteres.")
        return calle.strip() if calle else calle

    def clean_ciudad(self):
        ciudad = self.cleaned_data.get("ciudad")
        if ciudad and len(ciudad.strip()) < 3:
            raise ValidationError(
                "El nombre de la ciudad debe tener al menos 3 caracteres."
            )
        return ciudad.strip() if ciudad else ciudad

    def clean_codigo_postal(self):
        codigo = self.cleaned_data.get("codigo_postal")
        if codigo:
            if codigo < 1000000 or codigo > 9999999:
                raise ValidationError("El código postal debe tener 7 dígitos.")
        return codigo

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if telefono:
            if not telefono.isdigit():
                raise ValidationError("El teléfono debe contener solo números.")
            if len(telefono) < 9:
                raise ValidationError("El teléfono debe tener al menos 9 dígitos.")
        return telefono


class MetodoPagoForm(forms.ModelForm):
    """Formulario para agregar/editar métodos de pago del cliente"""

    numero_tarjeta = forms.CharField(
        max_length=19,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "1234 5678 9012 3456",
                "maxlength": "19",
            }
        ),
        label="Número de Tarjeta",
        required=True,
    )

    cvv = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "CVV", "maxlength": "4"}
        ),
        label="CVV",
        required=True,
    )

    class Meta:
        model = MetodoPago
        fields = ["tipo_metodo", "nombre_titular", "fecha_vencimiento"]
        widgets = {
            "tipo_metodo": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("", "Seleccione tipo de tarjeta"),
                    ("credito", "Tarjeta de Crédito"),
                    ("debito", "Tarjeta de Débito"),
                ],
            ),
            "nombre_titular": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre como aparece en la tarjeta",
                    "maxlength": "50",
                }
            ),
            "fecha_vencimiento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "month",
                    "placeholder": "MM/AAAA",
                }
            ),
        }
        labels = {
            "tipo_metodo": "Tipo de Tarjeta",
            "nombre_titular": "Nombre del Titular",
            "fecha_vencimiento": "Fecha de Vencimiento",
        }

    def clean_numero_tarjeta(self):
        numero = self.cleaned_data.get("numero_tarjeta", "").replace(" ", "")

        # Validar que solo contenga dígitos
        if not numero.isdigit():
            raise ValidationError("El número de tarjeta debe contener solo dígitos.")

        # Validar longitud (13-19 dígitos según estándar)
        if len(numero) < 13 or len(numero) > 19:
            raise ValidationError(
                "El número de tarjeta debe tener entre 13 y 19 dígitos."
            )

        # Algoritmo de Luhn para validar número de tarjeta
        def luhn_check(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10 == 0

        if not luhn_check(numero):
            raise ValidationError("El número de tarjeta no es válido.")

        return numero

    def clean_cvv(self):
        cvv = self.cleaned_data.get("cvv")
        if cvv:
            if not cvv.isdigit():
                raise ValidationError("El CVV debe contener solo números.")
            if len(cvv) < 3 or len(cvv) > 4:
                raise ValidationError("El CVV debe tener 3 o 4 dígitos.")
        return cvv

    def clean_nombre_titular(self):
        nombre = self.cleaned_data.get("nombre_titular", "")
        if nombre:
            nombre = nombre.strip().upper()
            # Validar que contenga solo letras y espacios
            if not re.match(r"^[A-ZÁÉÍÓÚÑ\s]+$", nombre):
                raise ValidationError(
                    "El nombre del titular debe contener solo letras."
                )
            if len(nombre) < 5:
                raise ValidationError(
                    "El nombre del titular debe tener al menos 5 caracteres."
                )
        return nombre

    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get("fecha_vencimiento")
        if fecha:
            hoy = date.today()
            # Validar que la tarjeta no esté vencida
            if fecha < hoy:
                raise ValidationError("La tarjeta está vencida.")
            # Validar que la fecha no sea muy lejana (más de 10 años)
            fecha_maxima = hoy + timedelta(days=365 * 10)
            if fecha > fecha_maxima:
                raise ValidationError(
                    "La fecha de vencimiento no puede ser mayor a 10 años."
                )
        return fecha

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Obtener número de tarjeta limpio
        numero_tarjeta = self.cleaned_data.get("numero_tarjeta", "").replace(" ", "")

        # Guardar últimos 4 dígitos
        instance.ultimos_4_digitos = numero_tarjeta[-4:]

        # Generar token seguro (hash del número de tarjeta + cvv)
        import hashlib

        cvv = self.cleaned_data.get("cvv", "")
        token_data = f"{numero_tarjeta}{cvv}"
        instance.token_seguro = hashlib.sha256(token_data.encode()).hexdigest()[:50]

        # Estado por defecto
        instance.estado = "activo"

        if commit:
            instance.save()
        return instance


class CambiarContrasenaForm(forms.Form):
    """Formulario para cambiar contraseña del cliente"""

    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Contraseña actual"}
        ),
        label="Contraseña Actual",
        required=True,
    )

    contrasena_nueva = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nueva contraseña"}
        ),
        label="Nueva Contraseña",
        required=True,
        min_length=6,
    )

    contrasena_confirmacion = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirmar nueva contraseña"}
        ),
        label="Confirmar Nueva Contraseña",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.cliente = kwargs.pop("cliente", None)
        super().__init__(*args, **kwargs)

    def clean_contrasena_actual(self):
        contrasena = self.cleaned_data.get("contrasena_actual")
        if self.cliente:
            import hashlib

            password_hash = hashlib.sha256(contrasena.encode()).hexdigest()
            if password_hash != self.cliente.password:
                raise ValidationError("La contraseña actual es incorrecta.")
        return contrasena

    def clean_contrasena_nueva(self):
        contrasena = self.cleaned_data.get("contrasena_nueva")
        if contrasena:
            if len(contrasena) < 6:
                raise ValidationError("La contraseña debe tener al menos 6 caracteres.")
            # Validar que tenga al menos una letra y un número
            if not re.search(r"[a-zA-Z]", contrasena) or not re.search(
                r"[0-9]", contrasena
            ):
                raise ValidationError(
                    "La contraseña debe contener al menos una letra y un número."
                )
        return contrasena

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get("contrasena_nueva")
        confirmacion = cleaned_data.get("contrasena_confirmacion")

        if nueva and confirmacion:
            if nueva != confirmacion:
                raise ValidationError("Las contraseñas nuevas no coinciden.")

        return cleaned_data
