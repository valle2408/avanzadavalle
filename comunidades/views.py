from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required # para el login , osea si esta logeuado permitir realizar acciones de aqui
from django.contrib import messages # mpara mensajes
from django.core.paginator import Paginator # para paginar las listas

from .models import Comunidad # importamos los dartos de comunidad
from .forms import FormularioComunidad # del dormulario de comunidad

from usuarios.models import UsuarioRol # y datos de los usuarios para utilizarlo en la logica

# para la generacion de PDF
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os

# mas importaciones para utilizar en el pdf
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.staticfiles import finders
import os
#--------------------------------------------------

#era
# 0 sin acceso
# 1 solo ver
# 2 crear y modificar en base a eso aremos la logica de lo demas mas el autenticado para eso
def obtener_permiso_comunidades(usuario):

    #buscmos los roles
    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    # Roles del usuario
    for usuario_rol in roles_usuario:

        # Obtenemos el rol
        rol = usuario_rol.rol
        permiso_actual = getattr(rol, 'comunidades', 0)
        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


# listar comunidades y buscar por ombre
@login_required # seguridad y login requeido para entrar
def lista_comunidades(request):

    permiso = obtener_permiso_comunidades(request.user)
    if permiso == 0:
        return redirect('dashboard') # si no esta permitido vuelve al dashboard osea atras
    
    comunidades = Comunidad.objects.all().order_by('nombre_comunidad')# listamos las comunidades

    nombre_comunidad = request.GET.get('nombre_comunidad') # buscador busca

    if nombre_comunidad:
        comunidades = comunidades.filter(nombre_comunidad__icontains=nombre_comunidad) #filtra

            # Paginación:
    # Mostramos 10 comunidades por página.
    
    paginator = Paginator(comunidades, 15)

    # Obtenemos el número de página desde la URL.
    # Ejemplo: /comunidades/?page=2
    page_number = request.GET.get('page')

    # Obtenemos la página actual.
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
        'permiso': permiso,
    }



    return render(request, 'comunidades/lista_comunidades.html', contexto)


# para crar
@login_required # login
def crear_comunidad(request):

    permiso = obtener_permiso_comunidades(request.user)

    # acceso mas de 2 para crear y modfiicar
    if permiso < 2:
        return redirect('comunidades:lista_comunidades')

    if request.method == 'POST':
        form = FormularioComunidad(request.POST)

        if form.is_valid():
            comunidad = form.save(commit=False)

            # Guardamos con el usuari que creo osea user
            comunidad.creado_por = request.user
            comunidad.save()

            messages.success(request, 'Comunidad creada correctamente.')
            return redirect('comunidades:lista_comunidades')

    else:
        form = FormularioComunidad()

    contexto = {
        'form': form,
    }

    return render(request, 'comunidades/formulario_comunidad.html', contexto)


# para editar
@login_required # login , seguridad requerida es bueno esto
def editar_comunidad(request, pk):

    permiso = obtener_permiso_comunidades(request.user)

# acceso mas de dos para eidtar
    if permiso < 2:
        return redirect('comunidades:lista_comunidades')

    # Buscamos la comundad
    comunidad = get_object_or_404(Comunidad, pk=pk)

    if request.method == 'POST':
        form = FormularioComunidad(request.POST, instance=comunidad)

        if form.is_valid():
            comunidad = form.save(commit=False)

            # Guardamos la edicion por user
            comunidad.editado_por = request.user
            comunidad.save()

            messages.success(request, 'Comunidad editada correctamente.')
            return redirect('comunidades:lista_comunidades')

    else:
        form = FormularioComunidad(instance=comunidad)

    contexto = {
        'form': form,
        'comunidad': comunidad,
    }

    return render(request, 'comunidades/formulario_comunidad.html', contexto)


#para eliminar pero comentaremos si es necesario opcional
@login_required # login
def eliminar_comunidad(request, pk):

    permiso = obtener_permiso_comunidades(request.user)

# mas de 2 para eliminar 
    if permiso < 2:
        return redirect('comunidades:lista_comunidades')

    comunidad = get_object_or_404(Comunidad, pk=pk)
    if request.method == 'POST':
        comunidad.delete()

        messages.success(request, 'Comunidad eliminada correctamente.')
        return redirect('comunidades:lista_comunidades')

    return redirect('comunidades:lista_comunidades')

#geneacion de pdf
@login_required
def exportar_comunidades_pdf(request):

    permiso = obtener_permiso_comunidades(request.user)

    # Si no tiene permiso 
    if permiso == 0:
        return redirect('dashboard')

    # agarramos las comunidades
    comunidades = Comunidad.objects.all().order_by('nombre_comunidad')

    # descargamos por filtro 
    nombre_comunidad = request.GET.get('nombre_comunidad')

    if nombre_comunidad:
        comunidades = comunidades.filter(nombre_comunidad__icontains=nombre_comunidad)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_comunidades.pdf"'

    # Creamos el documento PDF.
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    elementos = []
    estilos = getSampleStyleSheet()

    # Buscamos el logo desde static.
    logo_path = finders.find('img/logoavanzada2.jpg')

    # Título del reporte.
    titulo = Paragraph("<b>Reporte de Comunidades del Municipio de Irupana -GAMI.</b>", estilos['Title'])
    subtitulo = Paragraph("Empresa de Café La Avanzada", estilos['Normal'])

    elementos.append(titulo)
    elementos.append(subtitulo)
    elementos.append(Spacer(1, 0.5 * cm))

    # Datos visibles del PDF.
    data = [
        ['N°', 'Nombre de la comunidad']
    ]

    for numero, comunidad in enumerate(comunidades, start=1):
        data.append([
            numero,
            comunidad.nombre_comunidad,
            #datos que podemos utilizar descomentar si queremos
            # comunidad.estado,
            # comunidad.creado_por.username if comunidad.creado_por else 'Sin usuario',
            # comunidad.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            # comunidad.editado_por.username if comunidad.editado_por else 'Sin edición',
            # comunidad.fecha_edicion.strftime('%d/%m/%Y %H:%M'),
        ])

    tabla = Table(data, colWidths=[2 * cm, 13 * cm], repeatRows=1)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#233b6e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elementos.append(tabla)

    # Función para dibujar logo y pie de página en cada hoja.
    def agregar_encabezado_pie(canvas, doc):
        width, height = letter

        # Logo
        if logo_path and os.path.exists(logo_path):
            canvas.drawImage(
                logo_path,
                2 * cm,
                height - 2.6 * cm,
                width=1.5 * cm,
                height=1.5 * cm,
                preserveAspectRatio=True,
                mask='auto'
            )

        # Pie de página
        canvas.setFont("Helvetica", 8)
        canvas.drawString(2 * cm, 1 * cm, "Reporte para uso de conocimiento -  La Avanzada.")
        canvas.drawRightString(width - 2 * cm, 1 * cm, f"Página {doc.page}")

    # Construimos el PDF.
    doc.build(
        elementos,
        onFirstPage=agregar_encabezado_pie,
        onLaterPages=agregar_encabezado_pie
    )

    return response
