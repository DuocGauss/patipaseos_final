from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Max
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
# Create your models here.


class Propietario(AbstractUser):
    # Agregar un campo de rol
    rut = models.CharField(max_length=20, unique=True, default="")
    direccion = models.CharField(max_length=255, default="")
    imagen = models.ImageField(upload_to="imgprod", null=True, blank=True)
    es_cuidador = models.BooleanField(default=False)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    
class Cuidador(models.Model):
    ESPECIALIZACION = [
        ('Perros', 'Perros'),
        ('Perros pequeños', 'Perros pequeños'),
        ('Perros grandes', 'Perros grandes'),
        ('Gatos', 'Gatos'),
        ('Perros y Gatos', 'Perros y Gatos'),
    ]
    
    propietario = models.OneToOneField(Propietario, on_delete=models.CASCADE)
    id_cuidador = models.AutoField(primary_key=True)
    especializacion = models.CharField(max_length=50 ,default="", choices=ESPECIALIZACION)
    experiencia = models.TextField(default="", null=True, blank=True)
    disponibilidad = models.CharField(max_length=50, default="Disponible")
    
    def __str__(self):
        return f"{self.id_cuidador} - {self.propietario.username} - {self.especializacion} - {self.disponibilidad}"


class TipoServicio(models.Model):
    id_tipo_servicio = models.AutoField(primary_key=True)
    tipo_servicio = models.CharField(max_length=100)
    
    def __str__(self):
        return self.tipo_servicio    
    
class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.IntegerField(null=True, blank=True)
    es_activo = models.BooleanField(default=True)
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.id_servicio} -{self.tipo_servicio} - {self.cuidador.propietario.username}"

class Especie(models.Model):
    id_especie = models.AutoField(primary_key=True)
    especie_mascota = models.CharField(max_length=100)
    
    def __str__(self):
        return self.especie_mascota 

class Raza(models.Model):
    id_raza = models.AutoField(primary_key=True)
    raza_mascota = models.CharField(max_length=100)
    id_especie = models.ForeignKey(Especie, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.raza_mascota} - {self.id_especie}"   
    
class Mascota(models.Model):  
    PELAJE = [
        ('Duro', 'Duro'),
        ('Rizado', 'Rizado'),
        ('Corto', 'Corto'),
        ('Largo', 'Largo'),
        ('Sin pelo', 'Sin pelo'),
    ]
    
    id_mascota = models.AutoField(primary_key=True)
    nombre_mascota = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    pelaje = models.CharField(max_length=30, choices=PELAJE)
    observaciones = models.TextField(null=True, blank=True)
    es_activo = models.BooleanField(default=True)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='mascotas')
    id_raza = models.ForeignKey(Raza, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_mascota
    
    

class DetPrestacion(models.Model):
    fecha_prestacion = models.DateField(default=timezone.now)
    valor_total = models.DecimalField(max_digits=9, decimal_places=2)
    estado = models.CharField(max_length=50, default="Pendiente")
    id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    id_propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    id_cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    id_mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.fecha_prestacion} - {self.valor_total} - {self.id_servicio}"
    
    


class Mensaje(models.Model):
    user = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='sent_messages')
    sender = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='sent_messages_as_sender')
    recipient = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField(max_length=1000, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    det_prestacion = models.ForeignKey(DetPrestacion, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.sender} - {self.recipient} - {self.date}"

    @classmethod
    def send_message(cls, from_user, to_user, body, det_prestacion):
        if from_user == to_user:
            raise ValueError("El remitente y el destinatario deben ser diferentes.")

        sender_message = cls(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            body=body,
            is_read=True,
            det_prestacion=det_prestacion  # Nueva línea para asignar la DetPrestacion
        )
        sender_message.save()

        recipient_message = cls(
            user=to_user,
            sender=from_user,
            body=body,
            recipient=from_user,
            det_prestacion=det_prestacion  # Nueva línea para asignar la DetPrestacion
        )
        recipient_message.save()

        return sender_message


    @classmethod
    def get_messages(cls, user,det_prestacion=None):
        messages = (
            cls.objects
            .filter(user=user)
            .exclude(user=user, recipient=user)  # Excluir el usuario actual
            .values('recipient', 'det_prestacion')
            .annotate(last=Max('date'))
            .order_by('-last')
        )

        users = [
            {
                'user': Propietario.objects.get(pk=message['recipient']),
                'det_prestacion': message['det_prestacion'],
                'last': message['last'],
                'unread': cls.objects.filter(
                    user=user,
                    recipient__pk=message['recipient'],
                    is_read=False,
                    det_prestacion=message['det_prestacion']
                ).count()
            }
            for message in messages
        ]
        return users
    
    
    
    


class Resena(models.Model):
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE, related_name='resenas')
    autor = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    texto = models.TextField()
    calificacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.fecha_creacion} - {self.autor} - {self.calificacion}"

    