from django import forms
from .models import Propietario, Cuidador, Servicio, Mascota, DetPrestacion, Resena, Raza, Especie, TipoServicio
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
 



class frmRegistro(UserCreationForm):
    class Meta:
        model = Propietario
        fields = ['rut','username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'direccion', 'telefono']
        
        
class frmLogin(AuthenticationForm):
    class Meta:
        model = Propietario  # Reemplaza 'CustomUser' con el nombre de tu modelo de usuario personalizado
        fields = ['username', 'password'] 
        
        
class frmCuidador(forms.ModelForm):
    class Meta:
        model = Cuidador
        exclude = ['disponibilidad']
        fields = ['especializacion', 'experiencia']
        
        
class frmEdit(UserChangeForm):
    class Meta:
        model=Propietario
        fields=["username","first_name","last_name","email","direccion","telefono","imagen"] 

class frmTipoServicio(forms.ModelForm):
    class Meta:
        model=TipoServicio
        fields=["tipo_servicio"]        
        
class frmServicio(forms.ModelForm):
    class Meta:
        model=Servicio
        fields=["tipo_servicio","descripcion","precio"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.fields['precio'].label = 'Valor por hora'

class frmEspecie(forms.ModelForm):
    class Meta:
        model=Especie
        fields=["especie_mascota"]
        
class frmRaza(forms.ModelForm):
    class Meta:
        model=Raza
        fields=["id_especie","raza_mascota"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.fields['id_especie'].label = 'Especie'       
        
class frmMascota(forms.ModelForm):
    class Meta:
        model=Mascota
        fields=["id_raza","nombre_mascota","peso","pelaje","observaciones"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar'))
        self.fields['id_raza'].label = 'Raza'
        self.fields['peso'].label = 'Peso en kilogramos'
        
        
        

class frmDetPrestacion(forms.ModelForm):
    class Meta:
        model = DetPrestacion
        fields = '__all__'
        exclude = ['id_servicio', 'id_propietario', 'id_cuidador']
        widgets = {
            'fecha_prestacion': forms.DateInput(attrs={'type': 'date'}),
            'estado': forms.HiddenInput(),  # Ocultar el campo estado
        }   
    valor_total = forms.DecimalField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    def __init__(self, user, servicio_precio=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar las mascotas del usuario actual
        self.fields['id_mascota'].queryset = Mascota.objects.filter(propietario=user)
        self.fields['valor_total'].label = 'Valor por hora'
        self.fields['id_mascota'].label = 'Mascota'

        # Asignar el precio del servicio al valor_total
        if servicio_precio is not None:
            self.fields['valor_total'].initial = servicio_precio

    def clean(self):
        cleaned_data = super().clean()
        # Establecer el estado como "Activo" al guardar
        cleaned_data['estado'] = 'Pendiente'
        return cleaned_data

        
    

class frmResena(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['texto', 'calificacion']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3}),
            'calificacion': forms.HiddenInput(),  # Campo oculto para almacenar la calificación
        }