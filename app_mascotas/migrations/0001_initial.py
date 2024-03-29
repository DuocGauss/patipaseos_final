# Generated by Django 4.2.9 on 2024-02-13 06:28

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Propietario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('rut', models.CharField(default='', max_length=20, unique=True)),
                ('direccion', models.CharField(default='', max_length=255)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='imgprod')),
                ('es_cuidador', models.BooleanField(default=False)),
                ('telefono', models.CharField(blank=True, max_length=15, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cuidador',
            fields=[
                ('id_cuidador', models.AutoField(primary_key=True, serialize=False)),
                ('especializacion', models.CharField(choices=[('Perros', 'Perros'), ('Perros pequeños', 'Perros pequeños'), ('Perros grandes', 'Perros grandes'), ('Gatos', 'Gatos'), ('Perros y Gatos', 'Perros y Gatos')], default='', max_length=50)),
                ('experiencia', models.TextField(blank=True, default='', null=True)),
                ('disponibilidad', models.CharField(default='Disponible', max_length=50)),
                ('propietario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DetPrestacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_prestacion', models.DateField(default=django.utils.timezone.now)),
                ('valor_total', models.DecimalField(decimal_places=2, max_digits=9)),
                ('estado', models.CharField(default='Pendiente', max_length=50)),
                ('id_cuidador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.cuidador')),
            ],
        ),
        migrations.CreateModel(
            name='Especie',
            fields=[
                ('id_especie', models.AutoField(primary_key=True, serialize=False)),
                ('especie_mascota', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TipoServicio',
            fields=[
                ('id_tipo_servicio', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_servicio', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id_servicio', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('precio', models.IntegerField(blank=True, null=True)),
                ('es_activo', models.BooleanField(default=True)),
                ('cuidador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.cuidador')),
                ('tipo_servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.tiposervicio')),
            ],
        ),
        migrations.CreateModel(
            name='Resena',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('calificacion', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fue_editada', models.BooleanField(default=False)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('cuidador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resenas', to='app_mascotas.cuidador')),
            ],
        ),
        migrations.CreateModel(
            name='Raza',
            fields=[
                ('id_raza', models.AutoField(primary_key=True, serialize=False)),
                ('raza_mascota', models.CharField(max_length=100)),
                ('id_especie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.especie')),
            ],
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(blank=True, max_length=1000, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('det_prestacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.detprestacion')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages_as_sender', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mascota',
            fields=[
                ('id_mascota', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_mascota', models.CharField(max_length=100)),
                ('peso', models.DecimalField(decimal_places=2, max_digits=5)),
                ('pelaje', models.CharField(choices=[('Duro', 'Duro'), ('Rizado', 'Rizado'), ('Corto', 'Corto'), ('Largo', 'Largo'), ('Sin pelo', 'Sin pelo')], max_length=30)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('es_activo', models.BooleanField(default=True)),
                ('id_raza', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.raza')),
                ('propietario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mascotas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='detprestacion',
            name='id_mascota',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.mascota'),
        ),
        migrations.AddField(
            model_name='detprestacion',
            name='id_propietario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='detprestacion',
            name='id_servicio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_mascotas.servicio'),
        ),
    ]
