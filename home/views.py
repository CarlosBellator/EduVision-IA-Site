import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import shutil
import mimetypes

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
            return JsonResponse({
                'success': False,
                'error': 'Nenhum gráfico foi detectado na imagem enviada. Por favor, envie uma imagem clara de um gráfico.'
            }, status=422)
        elif graph_counter == 1:
            graph_values_dict = process_graph(list_graphs[0])
            return JsonResponse({
                'success': True,
                'message': 'Apenas um gráfico detectado e processado com sucesso.',
                'file_path': list_graphs[0],
                'variaveis': graph_values_dict,
                
            })
        return JsonResponse({
            'success': True,
            'message': 'Arquivo enviado com sucesso',
            'file_name': uploaded_file.name,
            'file_size': uploaded_file.size,
            'graphs_list': list_graphs,
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
        graph_image_path = data.get('graph_image_path')
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
        
        # Processar o caminho do arquivo 3D para o Django
        # Remover './media/' ou 'media/' do início do caminho
        if graph_3d_path:
            graph_3d_path_relative = graph_3d_path.replace('./media/', '').replace('media/', '')
            print(f'Caminho 3D processado: {graph_3d_path_relative}')
        else:
            graph_3d_path_relative = None
        
        # Processar a imagem se existir
        imagem_final = None
        if graph_image_path and os.path.exists(graph_image_path):
            print(f'Imagem encontrada em: {graph_image_path}')
            # Obter o caminho relativo a partir de 'media/'
            # Ex: media/temp/uploads/arquivo.jpg -> temp/uploads/arquivo.jpg
            relative_path = os.path.relpath(graph_image_path, 'media')
            
            # Criar diretório de graficos se não existir
            graficos_dir = os.path.join('media', 'graficos')
            os.makedirs(graficos_dir, exist_ok=True)
            
            # Copiar arquivo para o diretório final
            file_extension = os.path.splitext(graph_image_path)[1]
            final_filename = f"{unique_graph_name}{file_extension}"
            final_path = os.path.join(graficos_dir, final_filename)
            shutil.copy2(graph_image_path, final_path)
            
            # Caminho relativo para salvar no banco (sem 'media/')
            imagem_final = f'graficos/{final_filename}'
            print(f'Imagem do gráfico copiada de {graph_image_path} para: {final_path}')
        else:
            print(f'Imagem não encontrada ou caminho inválido: {graph_image_path}')
        
        print(f'Valor de imagem_final: {imagem_final}')
        
        # Criar registro do gráfico no banco de dados
        print(f'Salvando gráfico com obj3d: {graph_3d_path_relative if graph_3d_path_relative else "objetos3d/default.obj"}')
        novo_grafico = grafico.objects.create(
            user=request.user,
            name=graph_name,
            descricao=graph_description,
            x_axis_label=x_axis_label_text,
            y_axis_label=y_axis_label_text,
            imagem=imagem_final if imagem_final else 'graficos/default.png',
            obj3d=graph_3d_path_relative if graph_3d_path_relative else 'objetos3d/default.obj'
        )
        print(f'Gráfico salvo! ID: {novo_grafico.id}, obj3d salvo: {novo_grafico.obj3d}')
        
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
            'graph_3d_path': graph_3d_path,
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
        
        print(f'Gráfico encontrado: {graph.name}')
        print(f'Caminho obj3d no banco: {graph.obj3d}')
        print(f'Caminho obj3d.name: {graph.obj3d.name}')
        
        # Verificar se o arquivo 3D existe
        if not graph.obj3d:
            print('Campo obj3d está vazio')
            raise Http404("Arquivo 3D não encontrado")
        
        # Tentar obter o caminho do arquivo
        try:
            file_path = graph.obj3d.path
            print(f'Caminho completo do arquivo: {file_path}')
        except Exception as e:
            print(f'Erro ao obter path: {str(e)}')
            raise Http404("Erro ao acessar o arquivo 3D")
        
        # Verificar se o arquivo existe no sistema de arquivos
        if not os.path.exists(file_path):
            print(f'Arquivo não existe no caminho: {file_path}')
            raise Http404(f"Arquivo 3D não encontrado no servidor: {file_path}")
        
        print(f'Arquivo encontrado! Preparando download...')
        
        # Obter a extensão do arquivo
        file_extension = os.path.splitext(graph.obj3d.name)[1]
        
        # Nome do arquivo para download (nome do gráfico + extensão)
        download_filename = f"{graph.name}{file_extension}"
        
        # Abrir o arquivo
        file_handle = open(file_path, 'rb')
        print(f'File handle opened for: {file_path}')
        
        # Determinar o tipo MIME
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        print(f'Content type determined: {content_type}')
        
        # Criar resposta de arquivo
        response = FileResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        print(f'Prepared FileResponse for download: {download_filename}')
        
        return response
        
    except grafico.DoesNotExist:
        print(f'Gráfico com ID {graph_id} não encontrado para o usuário')
        raise Http404("Gráfico não encontrado")
    except Exception as e:
        print(f'Erro geral no download: {str(e)}')
        raise Http404(f"Erro ao baixar arquivo: {str(e)}")