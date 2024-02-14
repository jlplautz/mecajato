import os
from io import BytesIO

from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from fpdf import FPDF

from mecajato.servicos.models import Servico, ServicoAdicional

from .forms import FormServico


# Create your views here.
def novo_servico(request):
    if request.method == 'GET':
        form = FormServico()
        return render(request, 'novo_servico.html', {'form': form})
    elif request.method == 'POST':
        form = FormServico(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponse('Salvo com Sucesso')
        else:
            return render(request, 'novo_servico,html', {'form': form})


def listar_servico(request):
    if request.method == 'GET':
        servicos = Servico.objects.all()
        return render(request, 'listar_servico.html', {'servicos': servicos})


def servico(request, identificador):
    servico = get_object_or_404(Servico, identificador=identificador)
    return render(request, 'servico.html', {'servico': servico})


def gerar_os(request, identificador):
    servico = get_object_or_404(Servico, identificador=identificador)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 12)

    pdf.set_fill_color(240, 240, 240)
    pdf.cell(35, 10, 'Cliente:', 1, 0, 'L', 1)
    pdf.cell(0, 10, f'{servico.cliente.nome}', 1, 1, 'L', 1)

    pdf.cell(35, 10, 'Manutenções:', 1, 0, 'L', 1)

    # para contar quantos serviços existe para evitar celula vazi no relatório
    categorias_manutencao = servico.categoria_manutencao.all()

    for i, manutencao in enumerate(categorias_manutencao):
        pdf.cell(0, 10, f'- {manutencao.get_titulo_display()}', 1, 1, 'L', 1)
        if not i == len(categorias_manutencao) - 1:
            pdf.cell(35, 10, '', 0, 0)
    pdf.cell(35, 10, 'Data de Início:', 1, 0, 'L', 1)
    pdf.cell(0, 10, f'{servico.data_inicio}', 1, 1, 'L', 1)
    pdf.cell(35, 10, 'Data de Entrega:', 1, 0, 'L', 1)
    pdf.cell(0, 10, f'{servico.data_entrega}', 1, 1, 'L', 1)
    pdf.cell(35, 10, 'Identificador:', 1, 0, 'L', 1)
    pdf.cell(0, 10, f'{servico.identificador}', 1, 1, 'L', 1)

    # Para salvar o pdf em memoria
    pdf_content = pdf.output(dest='S').encode('latin1')
    pdf_bytes = BytesIO(pdf_content)

    # para fazer o download inserir -> as_attachment=True
    return FileResponse(
        pdf_bytes, as_attachment=True, filename=f'os-{servico.protocolo}.pdf'
    )


def servico_adicional(request):
    print('identificador_servico')
    identificador_servico = request.POST.get('identificador_servico')
    titulo = request.POST.get('titulo')
    descricao = request.POST.get('descricao')
    preco = request.POST.get('preco')

    servico_adicional = ServicoAdicional(
        titulo=titulo, descricao=descricao, preco=preco
    )

    servico_adicional.save()

    servico = Servico.objects.get(identificador=identificador_servico)
    servico.servicos_adicionais.add(servico_adicional)
    servico.save()

    return HttpResponse('Salvo')
