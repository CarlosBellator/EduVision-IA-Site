import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files import File
from django.core.files.base import ContentFile
import json
import os
import shutil
import mimetypes
import base64
import urllib.parse
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError

from contas.models import userProfile
from home.EduVision_IA.main import import_img, cut_image, analise_grafico, recortarVariaveis
from home.EduVision_IA.graph_creator import graficoobj
from home.models import grafico, valores_grafico


# Create your views here.
@login_required
def index(request):
    # Detecta user agent para mobile
    try:
        user_profile = userProfile.objects.get(user_id=request.user.id)
    except userProfile.DoesNotExist:
        user_profile = None
    context = {
        'user_profile': user_profile,
        'graph_history': grafico.objects.filter(user=request.user).order_by('-data_criacao')
    }
    print(f'context: {context}')
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone'])
    if is_mobile:
        return render(request, 'home/index-mobile.html',context)
    else:
        return render(request, 'home/index-desktop.html',context)


def process_graph(graph_path):
    graph_values = analise_grafico(graph_path)
    graph_values_dict = recortarVariaveis(graph_values)
    return graph_values_dict

@login_required
@require_http_methods(["POST"])
def upload_file(request):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum arquivo foi enviado'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        # Verificar se é uma imagem
        if not uploaded_file.content_type.startswith('image/'):
            return JsonResponse({
                'success': False,
                'error': 'Apenas arquivos de imagem são permitidos'
            }, status=400)
        
        # Verificar tamanho do arquivo (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return JsonResponse({
                'success': False,
                'error': 'Arquivo muito grande. Máximo permitido: 10MB'
            }, status=400)
        
        # Criar diretório de uploads se não existir
        upload_dir = os.path.join('/tmp','media', 'temp', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Gerar nome único para o arquivo
        import uuid
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Salvar arquivo
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        image, image_path, nome_arquivo = import_img(file_path)
        list_graphs = cut_image(image, image_path, nome_arquivo)
        graph_counter = len(list_graphs)
        print(f'graph_counter: {graph_counter}')
        if graph_counter == 0:
            return JsonResponse({'success': False, 'error': 'Nenhum gráfico foi detectado...'}, status=422)
        elif graph_counter == 1:
            graph_values_dict = process_graph(list_graphs[0])
            try:
                with open(list_graphs[0], "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    file_base64 = f"data:image/jpeg;base64,{encoded_string}"
            except Exception as e:
                print(f"Erro ao converter imagem: {e}")
                file_base64 = ""
            return JsonResponse({
                'success': True,
                'message': 'Apenas um gráfico detectado...',
                'file_path': file_base64,
                'variaveis': graph_values_dict,
            })
            
        graphs_base64 = []
        for path in list_graphs:
            try:
                with open(path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    # Adiciona o prefixo necessário para o HTML entender que é uma imagem
                    graphs_base64.append(f"data:image/jpeg;base64,{encoded_string}")
            except Exception as e:
                print(f"Erro ao converter imagem: {e}")
        # -----------------------------------------------------
                
        return JsonResponse({
            'success': True,
            'message': 'Arquivo enviado com sucesso',
            'file_name': uploaded_file.name,
            'file_size': uploaded_file.size,
            'graphs_list': list_graphs, # Mantém a lista original para usar depois
            'graphs_base64': graphs_base64, # Nova lista com as imagens convertidas
            'graph_counter': graph_counter
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }, status=500)    




@login_required
@require_http_methods(["POST"])    
def process_graph_request(request):
    try:
        data = json.loads(request.body)
        graph_path = data.get('graph_path')
        if not graph_path or not os.path.exists(graph_path):
            return JsonResponse({
                'success': False,
                'error': 'Caminho do gráfico inválido'
            }, status=400)
        graph_values_dict = process_graph(graph_path)
        
        # Verifica se a extração das variáveis foi bem-sucedida
        if graph_values_dict is None:
            return JsonResponse({
                'success': False,
                'error': 'Não foi possível extrair as variáveis do gráfico. O formato da resposta do Gemini pode estar incorreto.'
            }, status=422)

        return JsonResponse({
            'success': True,
            'message': 'Gráfico processado com sucesso',
            'variaveis': graph_values_dict
             
        })
    except ResourceExhausted as e:
        # Captura especificamente o limite de cota / excesso de requisições do Gemini
        return JsonResponse({
            'success': False,
            'error': 'Estamos com muitas requisições. Nos ajude informando os valores manualmente ou tente novamente em alguns instantes.'
        }, status=429)
        
    except GoogleAPIError as e:
        # Captura outros erros de comunicação com a API do Google
        return JsonResponse({
            'success': False,
            'error': 'Houve um erro na comunicação com a Inteligência Artificial. Tente novamente.'
        }, status=502)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def generate_graph(request):
    try:
        data = json.loads(request.body)
        graph_values = {
            'x_data': data.get('x_values'),
            'y_data': data.get('y_values'),
            'x_axis_label_text': data.get('x_unit'),
            'y_axis_label_text': data.get('y_unit')
        }
        graph_image_path = data.get('graph_image_base64')
        print(f'Caminho da imagem recebido: {graph_image_path}')
        graph_name = data.get('graph_name', 'Gráfico sem nome')
        graph_description = data.get('graph_description', '')
        print(f'Valores do gráfico recebidos: {graph_values}')
        x_values = graph_values.get('x_data')
        y_values = graph_values.get('y_data')
        x_axis_label_text = graph_values.get('x_axis_label_text')
        y_axis_label_text = graph_values.get('y_axis_label_text')

        if not x_values or not y_values:
            return JsonResponse({
                'success': False,
                'error': 'Valores de X e Y são obrigatórios'
            }, status=400)

        # Converter valores para float
        try:
            x_values_float = [float(x) for x in x_values]
            y_values_float = [float(y) for y in y_values]
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': f'Valores inválidos: certifique-se de que todos os valores são números. Erro: {str(e)}'
            }, status=400)

        # Atualizar graph_values com valores convertidos
        graph_values['x_data'] = x_values_float
        graph_values['y_data'] = y_values_float

        # Gerar o gráfico 3D
        unique_graph_name = f"{graph_name}_{uuid.uuid4()}"
        graph_3d_path = graficoobj(graph_values, unique_graph_name, '/tmp/media/Gráficos-3D/')
        
        # Criar a estrutura do gráfico no banco de dados (ainda sem os arquivos)
        novo_grafico = grafico(
            user=request.user,
            name=graph_name,
            descricao=graph_description,
            x_axis_label=x_axis_label_text,
            y_axis_label=y_axis_label_text,
        )

        # 1. Salvar e enviar a imagem para o Supabase Storage
        if graph_image_path and ';base64,' in graph_image_path:
            # Separa o cabeçalho (data:image/jpeg) da imagem real em si
            formato, imgstr = graph_image_path.split(';base64,')
            # Extrai a extensão da imagem
            extensao = formato.split('/')[-1]
            final_filename = f"{unique_graph_name}.{extensao}"
            
            # Descodifica o texto Base64 de volta para dados binários de imagem
            imagem_decodificada = base64.b64decode(imgstr)
            
            # Utiliza o ContentFile para criar um "ficheiro virtual em memória" 
            # e guarda diretamente no Django Storages/Supabase
            novo_grafico.imagem.save(final_filename, ContentFile(imagem_decodificada), save=False)
            
        elif graph_image_path and os.path.exists(graph_image_path):
            # Lógica alternativa caso o frontend algum dia envie o caminho físico do ficheiro
            file_extension = os.path.splitext(graph_image_path)[1]
            final_filename = f"{unique_graph_name}{file_extension}"
            with open(graph_image_path, 'rb') as img_file:
                novo_grafico.imagem.save(final_filename, File(img_file), save=False)
        else:
            novo_grafico.imagem = 'graficos/default.png'
            
        # 2. Salvar e enviar o arquivo 3D (.obj) para o Supabase Storage
        if graph_3d_path and os.path.exists(graph_3d_path):
            obj_extension = os.path.splitext(graph_3d_path)[1]
            obj_filename = f"{unique_graph_name}{obj_extension}"
            with open(graph_3d_path, 'rb') as obj_file:
                novo_grafico.obj3d.save(obj_filename, File(obj_file), save=False)
        else:
            novo_grafico.obj3d = 'objetos3d/default.obj'

        # Salvar o objeto no banco de dados
        novo_grafico.save()
        
        # Criar registros dos valores do gráfico
        for x_val, y_val in zip(x_values_float, y_values_float):
            valores_grafico.objects.create(
                grafico=novo_grafico,
                x_data=x_val,
                y_data=y_val
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Gráfico gerado com sucesso',
            'graph_id': novo_grafico.id
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def download_graph_3d(request, graph_id):
    try:
        # Buscar o gráfico pelo ID e verificar se pertence ao usuário
        graph = grafico.objects.get(id=graph_id, user=request.user)
        
        # Verificar se o arquivo 3D existe no banco
        if not graph.obj3d:
            raise Http404("Arquivo 3D não encontrado")
        # Pega a URL pública original (com o código gigante)
        file_url = graph.obj3d.url
        
        # Descobre a extensão original do arquivo (.stl ou .obj)
        file_extension = os.path.splitext(graph.obj3d.name)[1]
        
        # Cria um nome limpo baseado apenas no nome que o utilizador escolheu
        # Substituímos espaços por underlines para evitar problemas no download
        safe_name = graph.name.replace(' ', '_')
        download_filename = f"{safe_name}{file_extension}"
        
        # Codifica o nome para garantir que acentos (ex: Gráfico_1) não quebram o link
        encoded_filename = urllib.parse.quote(download_filename)
        
        # O Supabase permite forçar um novo nome de ficheiro na hora de baixar
        # adicionando o parâmetro ?download=novo_nome no final do link
        if '?' in file_url:
            final_url = f"{file_url}&download={encoded_filename}"
        else:
            final_url = f"{file_url}?download={encoded_filename}"
        
        # Com o Supabase Storage, redirecionamos direto para a URL da nuvem!
        # Isso tira o peso do Vercel e usa a velocidade do Supabase
        return redirect(final_url)
        
    except grafico.DoesNotExist:
        raise Http404("Gráfico não encontrado")
    except Exception as e:
        raise Http404(f"Erro ao acessar arquivo: {str(e)}")