from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from .models import VentaCafe
from .forms import FormularioVentaCafe
from usuarios.models import UsuarioRol


# Obtiene el permiso más alto del usuario para Registro de ventas.
# 0 = Sin acceso
# 1 = Solo ver
# 2 = Crear y modificar
def obtener_permiso_ventas(usuario):

    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    for usuario_rol in roles_usuario:
        rol = usuario_rol.rol

        permiso_actual = getattr(rol, 'registro_ventas_cafe', 0)

        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


# Lista principal de ventas.
@login_required
def lista_ventas(request):

    permiso = obtener_permiso_ventas(request.user)

    # Si no tiene acceso al módulo, vuelve al dashboard.
    if permiso == 0:
        return redirect('dashboard')

    ventas = VentaCafe.objects.all()

    buscar = request.GET.get('buscar', '').strip()

    if buscar:
        ventas = ventas.filter(
            Q(empresa_compradora__icontains=buscar) |
            Q(numero_ingreso__icontains=buscar)
        )

    ventas = ventas.order_by('-fecha_venta', '-fecha_registro')

    paginador = Paginator(ventas, 15)
    numero_pagina = request.GET.get('page')
    page_obj = paginador.get_page(numero_pagina)

    contexto = {
        'page_obj': page_obj,
        'buscar': buscar,
        'permiso': permiso,
    }

    return render(request, 'ventas/lista_ventas.html', contexto)


# Registra una nueva venta de café.
@login_required
def nueva_venta(request):

    permiso = obtener_permiso_ventas(request.user)

    # Solo usuarios con permiso 2 pueden registrar ventas.
    if permiso < 2:
        return redirect('dashboard')

    if request.method == 'POST':

        form = FormularioVentaCafe(request.POST)

        if form.is_valid():

            venta = form.save(commit=False)
            venta.procedencia = 'Irupana'
            venta.proveedor = 'La Avanzada'
            venta.registrado_por = request.user
            venta.save()

            return redirect('/ventas/?creado=1')

    else:
        form = FormularioVentaCafe()

    contexto = {
        'form': form,
        'titulo': 'Registrar Nueva Venta',
        'boton': 'Registrar',
        'es_edicion': False,
    }

    return render(request, 'ventas/formulario_venta.html', contexto)


# Edita una venta registrada.
@login_required
def editar_venta(request, pk):

    permiso = obtener_permiso_ventas(request.user)

    # Solo usuarios con permiso 2 pueden editar ventas.
    if permiso < 2:
        return redirect('dashboard')

    venta = get_object_or_404(VentaCafe, pk=pk)

    if request.method == 'POST':

        form = FormularioVentaCafe(request.POST, instance=venta)

        # La fecha no se edita; se mantiene la fecha original del registro.
        form.fields['fecha_venta'].disabled = True

        if form.is_valid():

            venta_editada = form.save(commit=False)
            venta_editada.editado_por = request.user
            venta_editada.save()

            return redirect('/ventas/?editado=1')

    else:
        form = FormularioVentaCafe(instance=venta)

        # La fecha se muestra, pero no se permite modificar.
        form.fields['fecha_venta'].disabled = True

    contexto = {
        'form': form,
        'venta': venta,
        'titulo': 'Editar Venta',
        'boton': 'Guardar cambios',
        'es_edicion': True,
    }

    return render(request, 'ventas/formulario_venta.html', contexto)


# Genera el comprobante PDF de la venta.
@login_required
def comprobante_venta_pdf(request, pk):

    permiso = obtener_permiso_ventas(request.user)

    # Debe tener acceso al módulo para ver comprobantes.
    if permiso == 0:
        return redirect('dashboard')

    venta = get_object_or_404(VentaCafe, pk=pk)

    # Tamaño pequeño tipo comprobante.
    ancho = 90 * mm
    alto = 135 * mm

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="comprobante_venta_{venta.numero_ingreso}.pdf"'

    pdf = canvas.Canvas(response, pagesize=(ancho, alto))

    margen_x = 8 * mm
    y = alto - 10 * mm

    # Título
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(ancho / 2, y, "COMPROBANTE")
    y -= 6 * mm

    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(ancho / 2, y, "Registro de venta de cafe")
    y -= 5 * mm

    pdf.line(margen_x, y, ancho - margen_x, y)
    y -= 6 * mm

    # Datos principales
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Nro. ingreso:")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(38 * mm, y, str(venta.numero_ingreso))
    y -= 5 * mm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Fecha:")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(38 * mm, y, venta.fecha_venta.strftime("%d/%m/%Y"))
    y -= 5 * mm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Empresa:")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(38 * mm, y, venta.empresa_compradora[:30])
    y -= 5 * mm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Tipo cafe:")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(38 * mm, y, venta.tipo_cafe)
    y -= 5 * mm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Procedencia:")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(38 * mm, y, venta.procedencia)
    y -= 5 * mm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Proveedor:")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(38 * mm, y, venta.proveedor)
    y -= 6 * mm

    pdf.line(margen_x, y, ancho - margen_x, y)
    y -= 6 * mm

    # Detalle de entrega
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Cantidad sacos:")
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(ancho - margen_x, y, str(venta.cantidad_sacos))
    y -= 5 * mm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margen_x, y, "Peso total:")
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(ancho - margen_x, y, f"{venta.peso_total_kg:.2f} kg")
    y -= 7 * mm

    pdf.line(margen_x, y, ancho - margen_x, y)
    y -= 7 * mm

    # Usuario que registró
    pdf.setFont("Helvetica", 7)

    if venta.registrado_por:
        pdf.drawCentredString(ancho / 2, y, f"Registrado por: {venta.registrado_por.username}")
        y -= 4 * mm

    pdf.drawCentredString(ancho / 2, y, "Empresa de Cafe La Avanzada")
    y -= 4 * mm
    pdf.drawCentredString(ancho / 2, y, "Comprobante digital")

    pdf.showPage()
    pdf.save()

    return response