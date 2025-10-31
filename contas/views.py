from multiprocessing import context
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from contas.forms import CadastroForm, LoginForm, AlterarSenhaForm
from django.contrib import auth , messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os

from contas.models import userProfile

import json
# Create your views here.
@csrf_exempt
def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form['email'].value()
            password = form['password'].value()
            print(f'Email: {email} - Senha: {password}')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
            if user is None:
                print('Usuário não encontrado')
                messages.error(request, 'Usuário não encontrado')
                return redirect('login')
            else:
                usuario = auth.authenticate(
                request,
                username=email,
                password=password)
                if usuario is not None:
                    auth.login(request, usuario)
                    print('Usuário logado com sucesso')
                    messages.success(request, f'Bem vindo {email}!')
                    return redirect('home')
                else:
                    print('Senha incorreta')
                    messages.error(request, 'Senha incorreta')
                    return redirect('login')
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone'])
    if is_mobile:
        return render(request, 'contas/login-mobile.html', {'form': form})
    else:
        return render(request, 'contas/login-desktop.html', {'form': form})

def logout(request):
    auth.logout(request)
     # Limpa todas as mensagens pendentes
    list(messages.get_messages(request))
    return redirect('login')

def cadastro(request):
    form = CadastroForm()
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            auth.login(request, usuario)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone'])
    if is_mobile:
        return render(request, 'contas/cadastro-mobile.html', {'form': form})
    else:
        return render(request, 'contas/cadastro-desktop.html', {'form': form})

@login_required
def conta(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone'])
    try:
        user_profile = userProfile.objects.get(user_id=request.user.id)
        user_name = request.user.first_name
        print(user_name)
    except userProfile.DoesNotExist:
        user_profile = None
    context = {
            'name': user_name,
            'user_profile': user_profile
        }
    print(context)
    if is_mobile:
        return render(request, 'contas/conta-mobile.html', context)
    else:
        return render(request, 'contas/conta-desktop.html', context)
        
@login_required
def atualizar_nome(request):
    print
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        novo_nome = data.get('nome')
        if novo_nome:
            # Atualiza o nome do usuário
            request.user.first_name = novo_nome
            request.user.save()
            return JsonResponse({'success': True, 'message': 'Nome atualizado'})
        
        return JsonResponse({'success': False, 'message': 'Nome inválido'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def upload_foto_perfil(request):
    print(f"Método recebido: {request.method}")
    print(f"Usuário autenticado: {request.user.is_authenticated}")
    print(f"Arquivos recebidos: {list(request.FILES.keys())}")
    
    if request.method == 'POST':
        try:
            # Verificar se um arquivo foi enviado
            if 'foto_perfil' not in request.FILES:
                print("Nenhum arquivo 'foto_perfil' encontrado")
                
                return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado'})
            
            foto = request.FILES['foto_perfil']
            print(f"Arquivo recebido: {foto.name}, Tamanho: {foto.size}, Tipo: {foto.content_type}")
            
            # Verificar se é uma imagem
            if not foto.content_type.startswith('image/'):
                messages.error(request, 'Arquivo deve ser uma imagem')
                return JsonResponse({'success': False, 'message': 'Arquivo deve ser uma imagem'})
            
            # Verificar tamanho do arquivo (max 5MB)
            if foto.size > 5 * 1024 * 1024:
                messages.error(request, 'Arquivo deve ter no máximo 5MB')
                print(f"Arquivo muito grande: {foto.size} bytes")
                return JsonResponse({'success': False, 'message': 'Arquivo deve ter no máximo 5MB'})
            
            # Obter ou criar o perfil do usuário
            try:
                user_profile = userProfile.objects.get(user=request.user)
                print(f"Perfil encontrado: {user_profile}")
            except userProfile.DoesNotExist:
                user_profile = userProfile.objects.create(user=request.user)
                print(f"Perfil criado: {user_profile}")
            
            # Remover a foto antiga se não for a padrão
            if user_profile.foto_perfil and 'default.jpg' not in user_profile.foto_perfil.name:
                try:
                    old_image_path = user_profile.foto_perfil.path
                    print(f"Removendo imagem antiga: {old_image_path}")
                    user_profile.foto_perfil.delete(save=False)
                except Exception as e:
                    print(f"Erro ao deletar imagem antiga: {e}")
            
            # Salvar a nova foto
            user_profile.foto_perfil = foto
            user_profile.save()
            print(f"Nova foto salva: {user_profile.foto_perfil.url}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Foto atualizada com sucesso',
                'new_image_url': user_profile.foto_perfil.url
            })
            
        except Exception as e:
            print(f"Erro interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Erro interno: {str(e)}'})
    
    print(f"Método não permitido: {request.method}")
    return render(request, 'contas/popup-enviar-foto.html')

@login_required
def alterar_senha(request):
    """
    View para alterar a senha do usuário logado.
    Aceita requisições POST (JSON ou form) e GET (renderiza formulário).
    """
    print(f"Método recebido: {request.method}")
    print(f"Usuário autenticado: {request.user.is_authenticated}")
    
    if request.method == 'POST':
        # Verifica se é uma requisição AJAX (JSON)
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                form = AlterarSenhaForm(user=request.user, data=data)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'message': 'Dados JSON inválidos.'})
        else:
            # Requisição de formulário normal
            form = AlterarSenhaForm(user=request.user, data=request.POST)
        
        print(f"Dados do formulário: {form.data}")
        
        if form.is_valid():
            try:
                # Salva a nova senha
                form.save()
                
                # Re-autentica o usuário com a nova senha para manter a sessão ativa
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                
                print("Senha alterada com sucesso")
                messages.success(request, 'Senha alterada com sucesso!')
                
                # Retorna resposta JSON ou redireciona dependendo do tipo de requisição
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': True, 
                        'message': 'Senha alterada com sucesso!'
                    })
                else:
                    return redirect('conta')
                    
            except Exception as e:
                print(f"Erro ao alterar senha: {str(e)}")
                error_message = 'Erro interno do servidor. Tente novamente.'
                
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': False, 
                        'message': error_message
                    })
                else:
                    messages.error(request, error_message)
        else:
            # Formulário inválido - retorna os erros
            print(f"Erros do formulário: {form.errors}")
            
            # Coleta todos os erros em uma mensagem
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{error}")
            
            error_message = ' '.join(error_messages)
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False, 
                    'message': error_message,
                    'errors': form.errors
                })
            else:
                messages.error(request, error_message)
    else:
        # Requisição GET - cria formulário vazio
        form = AlterarSenhaForm(user=request.user)
    
    # Para requisições GET ou POST com formulário inválido, renderiza a página
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone'])
    
    context = {
        'form': form,
        'user': request.user
    }
    
    # Se for mobile, você pode criar um template específico
    if is_mobile:
        return render(request, 'contas/alterar-senha-mobile.html', context)
    else:
        return render(request, 'contas/alterar-senha-desktop.html', context)

@login_required    
def conta_alterar_senha_mobile(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone'])
    if is_mobile:
        return render(request, 'contas/alterar-senha-mobile.html')
    else:
        return redirect('conta')