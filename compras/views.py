from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import random
import string

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .forms import FormularioCompraCafe
from .models import CompraCafe, DetallePesajeCompra

from productores.models import Productor
from usuarios.models import UsuarioRol, Rol


# Función para obtener el permiso del usuario en Registrar compra de café.
# 0 = Sin acceso
# 1 = Solo ver
# 2 = Crear y modificar
def obtener_permiso_registrar_compras(usuario):

    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    for usuario_rol in roles_usuario:
        rol = usuario_rol.rol

        permiso_actual = getattr(rol, 'registrar_compras_cafe', 0)

        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


# Normaliza textos de nombres y apellidos.
# Ejemplo: "  juan   carlos " -> "Juan Carlos"
def normalizar_nombre(texto):

    texto = texto.strip()
    texto = " ".join(texto.split())

    return texto.title()


# Genera las iniciales de la comunidad.
# Ejemplo: "La Avanzada" -> "LA"
# Ejemplo: "Alto Villa" -> "AV"
def obtener_iniciales_comunidad(nombre_comunidad):

    palabras = nombre_comunidad.strip().split()

    if len(palabras) >= 2:
        return (palabras[0][0] + palabras[1][0]).upper()

    return nombre_comunidad[:2].upper()


# Genera el código único del productor.
# Estructura:
# 2 letras del nombre + correlativo de 3 dígitos + 2 letras de comunidad
# Ejemplo: JU001AV
def generar_codigo_productor(nombre, comunidad):

    inicial_nombre = nombre[:2].upper()
    inicial_comunidad = obtener_iniciales_comunidad(comunidad.nombre_comunidad)

    base_codigo = f"{inicial_nombre}"

    contador = 1

    while True:
        codigo = f"{base_codigo}{contador:03d}{inicial_comunidad}"

        existe_productor = Productor.objects.filter(codigo_productor=codigo).exists()

        Usuario = get_user_model()
        existe_usuario = Usuario.objects.filter(username=codigo).exists()

        if not existe_productor and not existe_usuario:
            return codigo

        contador += 1


# Genera una contraseña temporal corta, sin guiones ni signos.
# Ejemplo: AV4827K
def generar_password_temporal():

    letras = string.ascii_uppercase
    numeros = string.digits

    return (
        "AV"
        + "".join(random.choices(numeros, k=4))
        + random.choice(letras)
    )


# Procesa los pesajes enviados desde el formulario.
# Convierte los valores a Decimal y valida que sean mayores a 0.
def procesar_pesajes(request):

    pesajes_texto = request.POST.getlist('pesajes[]')

    pesajes = []

    for pesaje_texto in pesajes_texto:

        pesaje_texto = pesaje_texto.strip()

        if not pesaje_texto:
            continue

        try:
            cantidad = Decimal(pesaje_texto)
        except InvalidOperation:
            raise ValueError('Uno de los pesajes no es válido.')

        if cantidad <= 0:
            raise ValueError('Los pesajes deben ser mayores a 0.')

        cantidad = cantidad.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        pesajes.append(cantidad)

    if not pesajes:
        raise ValueError('Debe registrar al menos un pesaje.')

    return pesajes


# Busca un productor existente o crea uno nuevo con su Usuario y Rol Productor.
def obtener_o_crear_productor(nombre, apellido_paterno, apellido_materno, comunidad, usuario_creador):

    productor = Productor.objects.filter(
        nombre__iexact=nombre,
        apellido_paterno__iexact=apellido_paterno,
        apellido_materno__iexact=apellido_materno,
        comunidad=comunidad
    ).first()

    if productor:
        return productor, False, None

    Usuario = get_user_model()

    codigo_productor = generar_codigo_productor(nombre, comunidad)
    password_temporal = generar_password_temporal()

    usuario = Usuario.objects.create_user(
        username=codigo_productor,
        password=password_temporal,
        first_name=nombre,
        last_name=f"{apellido_paterno} {apellido_materno}".strip(),
        is_active=True
    )

    rol_productor = Rol.objects.get(nombre_rol='Productor')

    UsuarioRol.objects.create(
        usuario=usuario,
        rol=rol_productor
    )

    productor = Productor.objects.create(
        codigo_productor=codigo_productor,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        comunidad=comunidad,
        usuario=usuario,
        estado='Activo',
        creado_por=usuario_creador
    )

    return productor, True, password_temporal


# Vista principal para registrar una nueva compra de café.
@login_required
def nueva_compra(request):

    permiso = obtener_permiso_registrar_compras(request.user)

    # Solo usuarios con permiso 2 pueden registrar compras.
    if permiso < 2:
        return redirect('dashboard')

    credenciales_nuevo_productor = None
    mensaje_error = None
    compra_registrada = None

    if request.method == 'POST':

        form = FormularioCompraCafe(request.POST)

        if form.is_valid():

            try:
                with transaction.atomic():

                    comunidad = form.cleaned_data['comunidad']
                    nombre = form.cleaned_data['nombre']
                    apellido_paterno = form.cleaned_data['apellido_paterno']
                    apellido_materno = form.cleaned_data['apellido_materno']
                    fecha_compra = form.cleaned_data['fecha_compra']
                    precio_compra = form.cleaned_data['precio_compra']

                    # Procesamos los pesajes enviados desde el formulario.
                    pesajes = procesar_pesajes(request)

                    # Sumamos todas las libras con Decimal.
                    total_libras = sum(pesajes, Decimal('0.00'))
                    total_libras = total_libras.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                    # Calculamos el total pagado.
                    total_pagado = total_libras * precio_compra
                    total_pagado = total_pagado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                    # Buscamos o creamos el productor.
                    productor, es_nuevo, password_temporal = obtener_o_crear_productor(
                        nombre=nombre,
                        apellido_paterno=apellido_paterno,
                        apellido_materno=apellido_materno,
                        comunidad=comunidad,
                        usuario_creador=request.user
                    )

                    # Registramos la compra general.
                    compra = CompraCafe.objects.create(
                        productor=productor,
                        comunidad=comunidad,
                        fecha_compra=fecha_compra,
                        precio_compra=precio_compra,
                        total_libras=total_libras,
                        total_pagado=total_pagado,
                        productor_nombre_recibo=productor.nombre_completo(),
                        comunidad_nombre_recibo=comunidad.nombre_comunidad,
                        codigo_productor_recibo=productor.codigo_productor,
                        creado_por=request.user
                    )

                    # Registramos cada pesaje.
                    for cantidad in pesajes:
                        DetallePesajeCompra.objects.create(
                            compra=compra,
                            cantidad_libras=cantidad
                        )

                    compra_registrada = compra

                    # Si el productor fue creado por primera vez, preparamos sus credenciales.
                    if es_nuevo:
                        credenciales_nuevo_productor = {
                            'nombre_completo': productor.nombre_completo(),
                            'comunidad': comunidad.nombre_comunidad,
                            'usuario': productor.codigo_productor,
                            'password': password_temporal,
                        }

                    # Limpiamos el formulario después de guardar correctamente.
                    form = FormularioCompraCafe()

            except Rol.DoesNotExist:
                mensaje_error = 'No existe un rol llamado Productor. Debe crearlo exactamente con ese nombre en Django Admin.'

            except ValueError as error:
                mensaje_error = str(error)

        else:
            mensaje_error = 'Revise los datos del formulario.'

    else:
        form = FormularioCompraCafe()

    contexto = {
        'form': form,
        'credenciales_nuevo_productor': credenciales_nuevo_productor,
        'mensaje_error': mensaje_error,
        'compra_registrada': compra_registrada,
        'fecha_hoy': timezone.localdate(),
    }

    return render(request, 'compras/nueva_compra.html', contexto)
