from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from datetime import date, timedelta, datetime
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
# Create your views here.
def Home(request):
    location = Location.objects.first()
    endereco = location.endereco
    link_map = location.link_map
    try:
        usuario_id = request.session['usuario']
    except:
        usuario_id = None
    servicos = Servicos.objects.all()
    if usuario_id == None:
        return redirect("realizar_cadastro")
    if usuario_id:
        user_logado = True
        usuario = Usuarios.objects.get(id=usuario_id)
        nome_usuario = usuario.nome
        e_barbeiro = usuario.e_barbeiro
        nome_barbeiro = None
        return render(request, 'home.html',{
            'nome_usuario':nome_usuario,

            'endereco':endereco,
            'ver_mapa':link_map,
            'user_logado':user_logado,
            "servicos": servicos,
            'e_barbeiro':e_barbeiro
            })
    else:
        user_logado = False

        return render(request, 'home.html',{
            'endereco':endereco,
            'ver_mapa':link_map,
            'user_logado':user_logado,
            "servicos": servicos,
            })




def agendar_servico(request):
    location = Location.objects.first()
    endereco = location.endereco
    link_map = location.link_map
    user_logado = 'usuario' in request.session
    if request.method == 'POST':
        servicos_ids = request.POST.getlist('servicos')

        if not servicos_ids:
            return HttpResponse("Selecione pelo menos um serviço.")

        servicos = Servicos.objects.filter(id__in=servicos_ids)

        tempo_total = sum(s.duracao_minutos for s in servicos)
        preco_total = sum(s.preco for s in servicos)

        nomes_servicos = ", ".join(s.titulo for s in servicos)

        # adiciona o preço na mesma string
        nomes_servicos = f"{nomes_servicos} - VALOR TOTAL: R$ {preco_total}"

        # salvar na sessão
        request.session['servicos_selecionados'] = servicos_ids
        request.session['tempo_total'] = tempo_total

    else:
        return HttpResponse("Método inválido.")

    # 🔹 localização
    

    # 🔹 usuário logado
    

    # 🔹 dias disponíveis
    hoje = date.today()
    dias = []

    dias_semana = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo',
    }

    for i in range(30):
        dia = hoje + timedelta(days=i)
        dias.append({
            'data': dia,
            'dia_semana': dias_semana[dia.strftime('%A')],
            'dia': dia.strftime('%d'),
            'mes': dia.strftime('%m'),
        })

    barbeiros = Barbeiros.objects.all()

    return render(request, 'agendamento.html', {
        'endereco': endereco,
        'ver_mapa': link_map,
        'user_logado': user_logado,
        'dias': dias,
        'barbeiros': barbeiros,
        'servico_nome': nomes_servicos,
        'servico_tempo': tempo_total,
    })



def selecionar_servicos(request):
    servicos = Servicos.objects.all()
    print("ENTROU NO SELECIONAR")
    return render(request, 'partials/box_service.html', {
        'servicos': servicos
    })
#HTMX
def lista_profissionais(request):
    barbeiros = Barbeiros.objects.all()
    return render(request, 'partials/profissionais.html', {
        'barbeiros': barbeiros
    })

def lista_servicos(request):
    servicos = Servicos.objects.all()
    user_logado = False
    try:
        usuario_id = request.session['usuario']
    except:
        usuario_id = None
    if usuario_id:
        user_logado = True
    return render(request, 'partials/servicos.html', {
        'servicos': servicos,
        'user_logado':user_logado,
    })




def teste_dia_htmx(request):
    dia = request.POST.get('dia')

    if dia:
        return HttpResponse(f"✅ Dia recebido via HTMX: {dia}")

    return HttpResponse("❌ Nenhum dia recebido")


def agenda_barbeiro_htmx(request):

    dia = request.POST.get('dia')
    barbeiro_id = request.POST.get('barbeiro')

    if not dia or not barbeiro_id:
        return HttpResponse("<p>Selecione dia e barbeiro</p>")

    data = datetime.fromisoformat(dia).date()
    dia_semana = data.weekday()

    barbeiro = Barbeiros.objects.get(id=barbeiro_id)

    try:
        expediente = Expediente.objects.get(
            dia_semana=dia_semana,
            ativo=True
        )
    except Expediente.DoesNotExist:
        return HttpResponse("<p>❌ Barbearia fechada neste dia</p>")

    intervalo = timedelta(minutes=15)

    # horário atual correto
    agora = timezone.localtime()
    limite_minimo = (agora + timedelta(minutes=30)).time()

    agendamentos = Agendamentos.objects.filter(
        barbeiro=barbeiro,
        data__date=data
    )

    horarios_ocupados = set()

    for ag in agendamentos:
        inicio = datetime.combine(data, ag.hora_inicio)
        fim = datetime.combine(data, ag.hora_fim)

        atual = inicio

        while atual < fim:
            horarios_ocupados.add(atual.time())
            atual += intervalo

    horarios_disponiveis = []

    def gerar_horarios(inicio, fim):

        if not inicio or not fim:
            return

        atual = datetime.combine(data, inicio)
        limite = datetime.combine(data, fim)

        while atual < limite:

            hora_atual = atual.time()

            if hora_atual not in horarios_ocupados:

                if data == agora.date():

                    if hora_atual >= limite_minimo:
                        horarios_disponiveis.append(hora_atual)

                else:
                    horarios_disponiveis.append(hora_atual)

            atual += intervalo

    gerar_horarios(expediente.inicio_manha, expediente.fim_manha)
    gerar_horarios(expediente.inicio_tarde, expediente.fim_tarde)

    if not horarios_disponiveis:
        return HttpResponse("<p>❌ Nenhum horário disponível</p>")

    horarios_formatados = [h.strftime('%H:%M') for h in horarios_disponiveis]

    return render(request, 'mostrar_agenda.html', {
        'horarios': horarios_formatados
    })




def confirmar_agendamento(request):
    if request.method != 'POST':
        return redirect('home')

    usuario_id = request.session.get('usuario')
    if not usuario_id:
        return redirect('login')

    usuario = Usuarios.objects.get(id=usuario_id)

    dia = request.POST.get('dia')
    horario_inicio = request.POST.get('horario_inicio')
    barbeiro_id = request.POST.get('barbeiro')

    # 🔥 agora vem direto do hidden input
    nomes_servicos = request.POST.get('servico_nome')
    duracao_total = int(request.POST.get('duracao'))

    if not nomes_servicos or not duracao_total:
        return redirect('home')

    # 🔥 converter data e hora
    data = datetime.fromisoformat(dia).date()
    hora_inicio = datetime.strptime(horario_inicio, '%H:%M').time()

    inicio_dt = datetime.combine(data, hora_inicio)
    fim_dt = inicio_dt + timedelta(minutes=duracao_total)

    Agendamentos.objects.create(
        usuario=usuario,
        servico=nomes_servicos,  # já vem concatenado
        barbeiro=Barbeiros.objects.get(id=barbeiro_id),
        data=inicio_dt,
        hora_inicio=hora_inicio,
        hora_fim=fim_dt.time()
    )

    location = Location.objects.first()

    return render(request, 'agendamento_sucesso.html', {
        'cliente': usuario.nome,
        'data': data.strftime('%d/%m/%Y'),
        'hora': horario_inicio,
        'user_logado': True,
        'endereco': location.endereco,
        'ver_mapa': location.link_map,
    })

def realizar_cadastro(request):
    location = Location.objects.first()
    endereco = location.endereco
    link_map = location.link_map
    return render(request, 'realizar_cadastro.html',{'endereco':endereco,
            'ver_mapa':link_map,})

def cadastro_usuario(request):
    if request.method == 'POST':
        print('primeiro if')
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        print(nome)
        print(telefone)
        try:
            usuario = Usuarios.objects.create(
                nome=nome,
                telefone=telefone,
                email=email,
                senha=make_password(senha)  # hash da senha
            )
            request.session['usuario'] = usuario.id
            return redirect('home')

        except IntegrityError:
            # email já cadastrado (unique=True)
            return render(request, 'realizar_cadastro.html', {
                'erro': 'Este e-mail já está cadastrado.',
                
            })

    return render(request, 'cadastro.html')


def ver_agendamentos(request):
    location = Location.objects.first()
    endereco = location.endereco
    link_map = location.link_map
    usuario_id = request.session.get('usuario')
    user_logado = True

    if not usuario_id:
        return redirect('cadastro')

    usuario = Usuarios.objects.get(id=usuario_id)

    # 👉 SE FOR BARBEIRO
    if usuario.e_barbeiro:
        print("IF É BARBEIRO")
        barbeiro = usuario.nome_barbeiro

        try:
            print("TRY É BARBEIRO")
            agendamentos = Agendamentos.objects.filter(
                barbeiro=barbeiro,
                data__gte=date.today()   # 👈 aqui
            ).order_by('data', 'hora_inicio')

            return render(request, 'meus_agendamentos.html', {
                'usuario': usuario,
                'barbeiro': barbeiro,
                'agendamentos': agendamentos,
                'e_barbeiro': True,
                'user_logado': user_logado,
                'endereco': endereco,
                'ver_mapa': link_map,
            })

        except:
            print("EXEPT É BARBEIRO")
            return render(request, 'meus_agendamentos.html', {
                'usuario': usuario,
                'barbeiro': barbeiro,
                'agendamentos': "<p>❌ Barbearia fechada neste dia</p>",
                'e_barbeiro': True,
                'user_logado': user_logado,
                'endereco': endereco,
                'ver_mapa': link_map,
            })

    agendamentos = Agendamentos.objects.filter(
        usuario=usuario,
        data__gte=date.today()   # 👈 aqui também
    ).order_by('data', 'hora_inicio')

    return render(request, 'meus_agendamentos.html', {
        'agendamentos': agendamentos,
        'usuario': usuario,
        'user_logado': user_logado,
        'endereco': endereco,
        'ver_mapa': link_map,
        'meus_agendamentos': True
    })


def cancelar_agendamento(request, agendamento_id):
    usuario_id = request.session.get('usuario')
    print("CANCELAR AGENDAMENTO")
    if not usuario_id:
        return redirect('cadastro')
    
    agendamento = get_object_or_404(
        Agendamentos,
        id=agendamento_id,
        usuario_id=usuario_id
    )
    print(agendamento)
    if request.method == 'POST':
        agendamento.delete()
    user_logado = True
    return redirect('meus_agendamentos')


def login_usuario(request):
    location = Location.objects.first()
    endereco = location.endereco
    link_map = location.link_map
    if request.method == 'POST':
        print('estamos na view login')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        print(email)
        print(senha)
        try:
            usuario = Usuarios.objects.get(email=email)
            print(usuario)
            if check_password(senha, usuario.senha):
                # salva sessão
                print("dentro do if")
                request.session['usuario'] = usuario.id
                return redirect('home')
            else:
                print("dentro do else")
                return render(request, 'login.html', {
                    'erro': 'Senha incorreta.',
                    'endereco':endereco,
                    'ver_mapa':link_map,
                })

        except Usuarios.DoesNotExist:
            return render(request, 'login.html', {
                'erro': 'Usuário não encontrado.'
            })

    return render(request, 'login.html', {
                    'endereco':endereco,
                    'ver_mapa':link_map,
    })


def recuperar_senha(request):
    return render(request, 'recuperar_senha.html')

def redefinir_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        usuario = Usuarios.objects.filter(email=email).first()
        if usuario:
            codigo = random.randint(1000, 9999)
            usuario.codigo_redf = codigo
            usuario.save()
            dominio = request.POST.get('dominio')
            print(dominio)
            if dominio:
                # montar link
                link_redef = f"{dominio}/nova_senha/{codigo}"

                nome = usuario.nome

                # enviar email
                send_mail(
                    'Redefinir senha',
                    f'Olá {nome},\n\nClique nesse link para redefinir sua senha:\n{link_redef}',
                    None,  # usa DEFAULT_FROM_EMAIL
                    [email],
                    fail_silently=False
                )
                return HttpResponse(f"{nome}, um email foi enviado com as instruções para redefinir sua senha. Vá até seu email e siga os passos.")
            else:
                return render(request, 'redefinir_senha.html', {
            'erro': 'Algo de estranho aconteceu, contate o administrador.'
            })
        else: 
            return render(request, 'redefinir_senha.html', {
            'erro': 'E-mail não encontrado'
        })

def nova_senha(request, codigo):
    print(codigo)  # aqui vem os 4 dígitos
    usuario = Usuarios.objects.filter(codigo_redf=codigo).first()
    if usuario:
        return render(request, 'nova_senha.html', {'usuario':usuario})
    else:
        return HttpResponse("Algo deu errado, contate o administrador")
    
def config_nova_senha(request):
    if request.method == 'POST':
        id_usuario = request.POST.get('id_usuario')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar')
        print(id_usuario)
        try:
            usuario = Usuarios.objects.get(id=id_usuario)
        except Usuarios.DoesNotExist:
            return render(request, 'nova_senha.html', {
                'erro': 'Usuário não encontrado'
            })

        # validação de senha
        if senha != confirmar:
            return render(request, 'nova_senha.html', {
                'usuario': usuario,
                'erro': 'As senhas devem ser iguais'
            })

        # salvar senha com hash
        usuario.senha = make_password(senha)

        # limpar código de redefinição
        usuario.codigo_redf = 0
        
        usuario.save()
        request.session['usuario'] = id_usuario
        return render(request, 'senha_sucesso.html')

    return redirect('redefinir_senha')
