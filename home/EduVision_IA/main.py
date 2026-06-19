print('Iniciando...')
import os # Operações com o sistema operacional
import requests # Faz requisição na API para identificar os graficos na imagem
from PIL import Image # Prepara imagens para o Gemini
import google.generativeai as genai # Uso temporáio do gemini para detecção dos valores dos gráficos
from home.EduVision_IA.graph_creator import graficoobj # Importa .py de criação de graficos 3D

# Tentar carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv # Responsável por ler chave da API do google se estiver em arquivo .env 
    load_dotenv()
except ImportError:
    pass  # python-dotenv não está instalado, usar apenas variáveis de ambiente do sistema

# URL da API
url = "https://carlosbellator-eduvision-ia-api.hf.space/detectar-grafico/"

# Configurar Autorização da API
AUTHORIZATION_API = os.getenv('AUTHORIZATION_API')
if not AUTHORIZATION_API:
    raise ValueError(
        "AUTHORIZATION_API não encontrada!\n"
        "Configure a variável de ambiente ou crie um arquivo .env\n"
        "Veja o README.md para instruções detalhadas."
    )

headers = {
    "Authorization": "Bearer " + AUTHORIZATION_API
}

# Configurar API key do Google Generative AI
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY não encontrada!\n"
        "Configure a variável de ambiente ou crie um arquivo .env\n"
        "Veja o README.md para instruções detalhadas."
    )

genai.configure(api_key=api_key)
MODEL_ID = "models/gemini-3.5-flash"
model = genai.GenerativeModel(MODEL_ID)

# Configura pasta de saída de resultados dos gráficos encontrados na imagem
output_folder = '/tmp/media/temp/results/'
# Verifica se a pasta de saída existe, caso contrário, cria
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
 # Confiura a pasta de saída de resultados dos gráficos 3D
graph3d_output_folder = '/tmp/media/Gráficos-3D'
# Verifica se a pasta de saída existe, caso contrário, cria
if not os.path.exists(graph3d_output_folder):
    os.makedirs(graph3d_output_folder)

def clear():
    # Essa função é responsável por fazer a limpiza do terminal com base no sistema eperacional
    if os.name == 'nt':  # 'nt' é para Windows
        os.system('cls')
    else:  # 'posix' é para sistemas Unix/Linux (incluindo macOS)
        os.system('clear')

def start():
    # Essa função é responsável por mostrar o Título da aplicação
    clear()
    print("""\n Bem vindo à
                 𝔼𝕕𝕦𝕍𝕚𝕤𝕚𝕠𝕟   𝕀𝔸 \n""")

def menu():
    # Essa função é responsável de mostrar a tela principal com seus elementos de título e menu
    clear()
    start()
    print('''Escolha uma opção:
             1. Análisar uma imagem
             2. Listar gráficos
             3. Criar modelo de um Gráfico da lista
             4. Imprimir gráfico
             5. Encerrar o programa
''')
    return 

def import_img(caminho=None):
    '''
    Essa função é responsável por verificar e importar a imagem para análise.
    Inputs: Caminho da imagem.
    Output: - Imagem
            - Nome_do_arquivo.
    '''
    
    if caminho is None:
        caminho = input('Digite o caminho da imagem: ').strip()

    image_path = caminho
    if (os.path.exists(image_path)):
        # Usar Pillow para carregar a imagem (compatível com servidores/headless)
        image = Image.open(image_path).convert("RGB")
        nome_arquivo = os.path.basename(image_path)  # Extrai apenas o nome do arquivo
        nome_arquivo = os.path.splitext(nome_arquivo)[0]  # Retmove a extenção do arquivo ".png"
        return image, image_path, nome_arquivo
    else:
        start()
        print('Caminho não existe! \n')
        return import_img()

def cut_image(image, image_path, nome_arquivo):
    '''
    Essa função é responsável por buscar os elementos(Enuniados e Gráficos) na imagem e fazer o recorte dos gráficos.
    Inputs: - Imagem
            - Nome da imagem.
    Output: Salva os recortes dos gráficos.
    '''
    print('Buscando gráficos na imagem... \n')
    graph_list = [] # Lista para armazenar os gráficos encontrados
    response = None
    try:
        with open(image_path, "rb") as image_file:
            files = {"file": image_file}
            response = requests.post(url, headers=headers, files=files)
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return graph_list

    if response is None:
        return graph_list

    response_data = None
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
    else:
        print(f"Erro {response.status_code}: {response.text}")

    detections = []
    if isinstance(response_data, dict):
        detections = (
            response_data.get("results")
            or response_data.get("boxes")
            or response_data.get("detections")
            or response_data.get("predictions")
            or []
        )
    elif isinstance(response_data, list):
        detections = response_data
    else:
        print(f"Formato de resposta não suportado: {type(response_data).__name__}")

    if not detections:
        print("Nenhuma detecção retornada pela API.")
        return graph_list

    # Faz o recorte dos gráficos usando Pillow
    for i, box in enumerate(detections):
        if isinstance(box, dict):
            bbox = box.get("box", box.get("bbox", box))
            x1 = int(bbox.get("x1", 0))
            y1 = int(bbox.get("y1", 0))
            x2 = int(bbox.get("x2", 0))
            y2 = int(bbox.get("y2", 0))
        else:
            print(f"Formato de detecção não suportado: {box}")
            continue

        # Ajusta coordenadas para os limites da imagem
        width, height = image.size
        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:
            print(f"Coordenadas inválidas para caixa: {bbox}")
            continue

        cropped = image.crop((x1, y1, x2, y2))
        output_path = os.path.join(output_folder, f"{nome_arquivo}-Grafico_{i+1}.jpg")
        try:
            cropped.save(output_path, format="JPEG")
            graph_list.append(output_path)
        except Exception as e:
            print(f"Erro ao salvar recorte: {e}")
    print(f"* {len(graph_list)} gráficos foram encontrados e salvos em {output_folder}")
    return graph_list

def deletar_grafico():
    start()
    listar_graficos()
    excluir = input('Deseja excluir algum gráfico? (s/n):').lower()
    if  excluir == 's' or excluir == 'sim':
        grafico_path, _ = selecionar_grafico()
        if grafico_path != None:
            os.remove(grafico_path)
            print('Gráfico removido com sucesso.')
        return deletar_grafico()
    elif excluir == 'n' or excluir =='não':
        main()
    else:
        input('Opção inválida, pressione enter para tente novamente')
        return deletar_grafico()
    
        
def listar_graficos():
    '''
    Essa função é responsável por mostrar a lista de imagens de gráficos e deletar se necessário.
    Inputs: - 'deseja apagar algum gráfico?'
            - gráfico para ser deletado.
    Output: - Deleta o gráfico solicitado
    '''

    print('Gráficos:\n')
    graficos = os.listdir(output_folder)
    graficos.sort()
    count = 0
    for i in graficos:
        count = count+1
        print(f'{count}. {i}')
    if not count:
        print(f"*{'Nenhum gráfico na lista :c'.center(30)}*\n")
        input('Pressione enter para voltar para o menu principal...')
        main()
    print()
def selecionar_grafico():
    '''
    Essa função é responsável por fazer a seleção do gráfico, pode ser usado em qualquer circunstancia.
    Input: - gráfico que para selecionar
    Output: - Retorna o caminho da imagem selecionada.
    '''
    #Conta a quantidade de imagens de gráficos na pasta de saida
    graficos = os.listdir(output_folder)
    graficos.sort()
    quantidade = 0
    for i in graficos:
        quantidade = quantidade+1
    try:    
        grafico = int(input('Digite o número do gráfico para selecionar: '))
        if grafico >0 and grafico <= quantidade:
            clear()
            print(f'Gráfico {grafico} selecionado')
        else:
            input('Gráfico não encontrado, pressione enter para tentar novamente')
            return None, None
    except:
        input('Digite o número do gráfico desejado, pressione enter para tentar novamente')
        return None, None
        
    graficos = os.listdir(output_folder)
    graficos.sort()
    grafico_path = os.path.join(output_folder, graficos[grafico-1])
    # Extrai o nome do arquivo
    nome_arquivo = os.path.basename(grafico_path)  # Extrai apenas o nome do arquivo
    nome_arquivo = os.path.splitext(nome_arquivo)[0]  # Retmove a extenção do arquivo ".png"
    return grafico_path, nome_arquivo

def analise_grafico(grafico_path):
    '''
    Essa função é responsável por fazer a análise do gráfico com o gemini(temporáriamente)
    Input: - Caminho do gráfico para análise
    Output: - Retornar os dados do gráfico enviado
    '''
    img = Image.open(grafico_path)

    prompt = """Analise o gráfico e me retorne apenas suas medidas no formato de código Python.
    
    IMPORTANTE: Sua resposta deve estar OBRIGATORIAMENTE dentro de um bloco de código Markdown usando três acentos graves (```).
    
    Formato de resposta:
    ```
    x_data = [0, 1, 2, 3, 4, 5]
    y_data = [3, 3, 3, 2, 1, 0]
    x_axis_label_text = "v (m/s)"
    y_axis_label_text = "t (s)"
    ```
    
    Se houver alguma incógnita, estime o valor dela.
    Certifique-se de incluir os três acentos graves (```) no início e no final do código."""
    
    response = model.generate_content(
        contents=[prompt,img]
    )
    return response.text
    
def recortarVariaveis(data_string):
    """
    Essa função é responsável por recortar os valores do gráfico retornados pelo gemini
    Inputs: - data_string (str): A string contendo o bloco de código a ser extraído.
    Outputs: - dict: Um dicionário contendo as variáveis extraídas do bloco de código.
             - Retorna None se houver erro na extração.
    """
    # --- Extração do Bloco de Código ---
    
    # Encontra a posição inicial do bloco de código.
    start_index = data_string.find("```")
    if start_index == -1: # Verifica se o marcador inicial foi encontrado
        print("Erro: Marcador inicial de código '```' não encontrado na string.")
        print(f"Resposta recebida: {data_string[:200]}...")  # Mostra os primeiros 200 caracteres
        return None
    
    # Adicionamos 3 para pular os caracteres "```" e começar no código real.
    start_index += 3
    
    # Verifica se há um identificador de linguagem (como "python") logo após ```
    # e pula essa linha se existir
    newline_after_backticks = data_string.find('\n', start_index)
    if newline_after_backticks != -1:
        first_line = data_string[start_index:newline_after_backticks].strip().lower()
        if first_line in ['python', 'py', '']:
            start_index = newline_after_backticks + 1

    # Encontra a posição final do bloco de código.
    # Usamos rfind para garantir que pegamos o último "```".
    end_index = data_string.rfind("```")
    if end_index == -1 or end_index <= start_index: # Verifica se o marcador final foi encontrado e é válido
        print("Erro: Marcador final de código '```' não encontrado ou inválido na string.")
        print(f"Resposta recebida: {data_string[:200]}...")  # Mostra os primeiros 200 caracteres
        return None

    # Extrai a substring que contém apenas o código Python.
    # O método .strip() remove quaisquer espaços em branco extras ou quebras de linha no início e no final do bloco extraído.
    code_block = data_string[start_index:end_index].strip()
    
    print(f"Bloco de código extraído: {code_block}")  # Debug

    # --- Execução do Código e Captura das Variáveis ---

    # Criamos um dicionário vazio que será usado como o escopo local para exec().
    # Isso fará com que as variáveis definidas no code_block sejam armazenadas aqui.
    extracted_vars = {}
    try:
        # A função exec() executa a string como código Python.
        # Passamos um dicionário vazio para o escopo global (primeiro {})
        # e nosso dicionário 'extracted_vars' para o escopo local (segundo {}).
        # Isso garante que as variáveis do code_block sejam criadas dentro de extracted_vars.
        exec(code_block, {}, extracted_vars)
    except Exception as e:
        print(f"Erro ao executar o bloco de código: {e}")
        print(f"Bloco que causou erro: {code_block}")
        return None

    # Retorna o dicionário contendo todas as variáveis que foram definidas
    # no bloco de código.
    return extracted_vars

def criar_modelo3d():
    start()
    listar_graficos()
    graph_path, graph_name = selecionar_grafico()
    if graph_path != None:
        graph_values = analise_grafico(graph_path)
        graph_values_dict = recortarVariaveis(graph_values)
        graficoobj(graph_values_dict,graph_name,graph3d_output_folder)
        input('Pressione enter para voltar para o menu principal...')
        main()
    else:
        criar_modelo3d()

def main():
    opcao = menu() # Mostra o menu da aplicação
    opcao = int(input('Digite o número da opção e pressione enter: '))
    try:
        match opcao:
            case 1: # 1. Análisar uma imagem
                start()
                image, image_path, nome_arquivo = import_img()
                cut_image(image, image_path, nome_arquivo)
                
            case 2: # 2. Listar gráficos
                deletar_grafico()
            case 3: # 3. Criar modelo de um Gráfico da lista
                criar_modelo3d()
            case 4: # 4. Imprimir gráfico
                input('\nFunção em desenvolvimento...')
                return main()
            case 5: # 5. Encerrar o programa
                clear()
                print('Finalizando programa...')
                exit
            case _:
                input('Opção invalida, digite uma opção válida! Pressione enter para tentar novamente...')
                main()
    except:
        input('Opção invalida, digite um número! Pressione enter para tentar novamente...')
        main()

if __name__ == '__main__':
    main()