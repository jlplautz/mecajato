import json
import re

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Carro, Cliente


def clientes(request):
    if request.method == 'GET':
        clientes_list = Cliente.objects.all()
        return render(request, 'clientes.html', {'clientes': clientes_list})
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        carros = request.POST.getlist('carro')
        placas = request.POST.getlist('placa')
        anos = request.POST.getlist('ano')

        cliente = Cliente.objects.filter(cpf=cpf)

        if cliente.exists():
            return render(
                request,
                'clientes.html',
                {
                    'nome': nome,
                    'sobrenome': sobrenome,
                    'email': email,
                    'carros': zip(carros, placas, anos),
                },
            )

        if not re.fullmatch(
            re.compile(
                r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
            ),
            email,
        ):
            return render(
                request,
                'clientes.html',
                {
                    'nome': nome,
                    'sobrenome': sobrenome,
                    'cpf': cpf,
                    'carros': zip(carros, placas, anos),
                },
            )

        cliente = Cliente(nome=nome, sobrenome=sobrenome, email=email, cpf=cpf)

        cliente.save()

        for carro, placa, ano in zip(carros, placas, anos):
            car = Carro(carro=carro, placa=placa, ano=ano, cliente=cliente)
            car.save()

        return HttpResponse('Teste')


# a função att_cliente eira funcionar como um API
def att_cliente(request):
    id_cliente = request.POST.get('id_cliente')
    cliente = Cliente.objects.filter(id=id_cliente)
    carros = Carro.objects.filter(cliente=cliente[0])

    # usando um serializador - transformando os dados do Cliente no formato json.
    cliente_json = json.loads(serializers.serialize('json', cliente))[0][
        'fields'
    ]
    # depois de capturado o cliente correto, capturar o id
    #  para retornar o id do cliente
    cliente_id = json.loads(serializers.serialize('json', cliente))[0]['pk']

    carros_json = json.loads(serializers.serialize('json', carros))
    # { key:value, key:value } for i in carros_json
    carros_json = [{'fields': i['fields'], 'id': i['pk']} for i in carros_json]
    #  para incluir o id do cliente no context
    data = {
        'cliente': cliente_json,
        'carros': carros_json,
        'cliente_id': cliente_id,
    }

    # o retorna será com jsonresponse
    return JsonResponse(data)


def excluir_carro(request, id):
    try:
        carro = Carro.objects.get(id=id)
        carro.delete()
        return redirect(
            reverse('clientes') + f'?aba=att_cliente&id_cliente={id}'
        )
    except:
        # TODO:Exibir mensagem de erro
        return redirect(
            reverse('clientes') + f'?aba=att_cliente&id_cliente={id}'
        )


@csrf_exempt
def update_carro(request, id):
    nome_carro = request.POST.get('carro')
    placa = request.POST.get('placa')
    ano = request.POST.get('ano')

    carro = Carro.objects.get(id=id)
    # na busca da placa no banco excluir a placa do proprio carro
    list_carros = Carro.objects.exclude(id=id).filter(placa=placa)

    if list_carros.exists():
        return HttpResponse('Placa já existente')

    carro.carro = nome_carro
    carro.placa = placa
    carro.ano = ano
    carro.save()

    return HttpResponse(id)


def update_cliente(request, id):
    # os dados serão envado do front no corpo da requisição
    # os dados não serão enviados no method POST
    # para transformar o request.bdy em um json
    body = json.loads(request.body)

    nome = body['nome']
    sobrenome = body['sobrenome']
    email = body['email']
    cpf = body['cpf']

    cliente = get_object_or_404(Cliente, id=id)
    # TODO: Fazer a validação dos campos antes de salvar
    try:
        cliente.nome = nome
        cliente.sobrenome = sobrenome
        cliente.email = email
        cliente.cpf = cpf
        cliente.save()
        return JsonResponse(
            {
                'status': '200',
                'nome': nome,
                'sobrenome': sobrenome,
                'email': email,
                'cpf': cpf,
            },
        )
    except:
        return JsonResponse({'status': '500'})
