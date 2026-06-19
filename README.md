# 🌐 EduVision IA - Site

**Plataforma Web para Análise e Conversão de Gráficos em Objetos 3D Táteis**

Uma aplicação web desenvolvida com Django que permite aos usuários fazer upload de imagens contendo gráficos, processá-las com Inteligência Artificial e convertê-las em modelos 3D táteis (.STL) para auxiliar pessoas com deficiência visual no ensino de matemática e ciências.

## 🎯 Objetivo

O **EduVision IA - Site** é a interface web do projeto EduVision, oferecendo uma experiência amigável e intuitiva para converter gráficos em modelos 3D acessíveis, sem necessidade de instalar software localmente.

## 🔧 Funcionalidades

- **📤 Upload de Imagens**: Interface drag-and-drop para envio de imagens
- **🔍 Detecção em Tempo Real**: Processamento automático de gráficos via API remota
- **🧠 Análise com IA**: Extração de dados usando Google Gemini AI
- **📐 Geração de STL**: Download direto de modelos 3D táteis
- **👤 Sistema de Contas**: Gerenciamento de usuários e histórico de conversões
- **📊 Visualização**: Preview dos gráficos detectados antes da conversão
- **♿ Design Acessível**: Interface pensada para inclusão

## 📁 Estrutura do Projeto

```
EduVision-IA-Site/
├── manage.py                  # Gerenciador Django
├── djangorequiriments.txt     # Dependências do projeto
├── contas/                    # App de autenticação
│   ├── models.py              # Modelos de usuário
│   ├── views.py               # Views de login/registro
│   └── urls.py                # Rotas de autenticação
├── graficos/                  # App principal
│   ├── models.py              # Modelos de gráficos
│   ├── views.py               # Lógica de processamento
│   ├── graph_crator.py        # Geração de objetos 3D
│   └── urls.py                # Rotas da aplicação
├── home/                      # App da página inicial
│   ├── views.py               # Views da home
│   └── urls.py                # Rotas da home
├── setup/                     # Configurações Django
│   ├── settings.py            # Configurações gerais
│   ├── urls.py                # URLs principais
│   └── wsgi.py                # WSGI config
├── templates/                 # Templates HTML
│   ├── base.html              # Template base
│   ├── home.html              # Página inicial
│   ├── upload.html            # Upload de imagens
│   └── resultado.html         # Resultados da análise
└── media/                     # Arquivos de upload
    ├── uploads/               # Imagens enviadas
    └── results/               # STL gerados
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno

### Instalação das Dependências

```bash
# Clone o repositório
git clone https://github.com/CarlosBellator/EduVision-IA-Site.git
cd EduVision-IA-Site

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Instale as dependências
pip install -r djangorequiriments.txt
```

### Configuração da API Google

1. **Obter API Key**:
   - Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Faça login com sua conta Google
   - Clique em "Create API Key"
   - Copie a chave gerada

2. **Configurar Variável de Ambiente**:
   
   **Linux/macOS:**
   ```bash
   export GOOGLE_API_KEY="sua_chave_api_aqui"
   ```
   
   **Windows:**
   ```cmd
   set GOOGLE_API_KEY=sua_chave_api_aqui
   ```
   
   **Ou crie um arquivo `.env`:**
   ```bash
   # Na raiz do projeto
   echo "GOOGLE_API_KEY=sua_chave_api_aqui" > .env
   ```

### Configuração da API de Detecção

1. **Definir a autorização**:
   - Crie uma variável de ambiente chamada `AUTHORIZATION_API`
   - O valor deve ser o token fornecido para acesso à API de detecção

2. **Opcional: usar arquivo `.env`**:
   ```bash
   AUTHORIZATION_API=seu_token_aqui
   GOOGLE_API_KEY=sua_chave_api_aqui
   ```

3. **Endpoint usado pelo sistema**:
   ```text
   https://carlosbellator-eduvision-ia-api.hf.space/detectar-grafico/
   ```

4. **Observação**:
   - Não é necessário baixar nem treinar o modelo YOLO localmente

### Configuração do Banco de Dados

```bash
# Execute as migrações
python manage.py makemigrations
python manage.py migrate

# Crie um superusuário (opcional)
python manage.py createsuperuser
```

## 💻 Como Usar

### Executar o Servidor

```bash
python manage.py runserver
```

Acesse: `http://localhost:8000`

### Fluxo de Trabalho

1. **Criar Conta**: Registre-se na plataforma ou faça login
2. **Upload**: Arraste e solte ou selecione uma imagem com gráficos
3. **Detecção**: O sistema envia a imagem para a API e recupera os gráficos detectados
4. **Análise**: Selecione o gráfico desejado para análise detalhada
5. **Download**: Baixe o modelo STL gerado para impressão 3D

### Endpoints Principais

- `/` - Página inicial
- `/contas/login/` - Login de usuário
- `/contas/registro/` - Registro de novo usuário
- `/graficos/upload/` - Upload de imagens
- `/graficos/analisar/` - Análise de gráficos
- `/graficos/download/<id>/` - Download de STL

## 🛠️ Tecnologias Utilizadas

### Backend
- **🎯 Django**: Framework web Python
- **🐍 Python**: Linguagem principal
- **👁️ OpenCV**: Processamento de imagens
- **🌐 Requests**: Comunicação com a API de detecção
- **🧠 Google Gemini AI**: Análise de gráficos
- **📐 NumPy**: Computação numérica
- **🎨 Trimesh**: Manipulação de malhas 3D

### Frontend
- **📄 HTML5**: Estrutura das páginas
- **🎨 CSS3**: Estilização
- **⚡ JavaScript**: Interatividade

## 📊 Compatibilidade

### Navegadores
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

### Sistemas Operacionais
- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+)
- ✅ macOS Big Sur+

## 🔧 Configurações Avançadas

### Configurações de Upload

Edite `setup/settings.py`:

```python
# Tamanho máximo de upload (em bytes)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Tipos de arquivo permitidos
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg']

# Diretório de media
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

### Configurações do Modelo 3D

Edite `graficos/graph_crator.py` para ajustar parâmetros:

```python
# Dimensões da base
altura_base_plataforma = 0.14
margem_base = 0.5

# Linha do gráfico
altura_linha_grafico = 0.3
largura_linha_grafico = 0.15

# Relevos táteis
diametro_relevo_linha = 0.14
altura_relevo_linha = 0.07
espacamento_relevos_linha = 0.4
```

## 📋 Requisitos do Sistema

### Mínimo
- **OS**: Windows 10/Linux/macOS
- **RAM**: 4GB
- **Python**: 3.8+
- **Espaço**: 2GB livres
- **Conexão**: Internet para API calls

### Recomendado
- **OS**: Windows 11/Ubuntu 22.04+/macOS Monterey+
- **RAM**: 8GB+
- **Python**: 3.10+
- **Espaço**: 5GB livres
- **Conexão**: Banda larga

## 🐛 Solução de Problemas

### Erros Comuns

1. **Erro ao iniciar servidor Django**:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

2. **Erro de permissão em media/**:
   ```bash
   # Linux/macOS
   chmod -R 755 media/
   ```

3. **Erro da API de detecção**:
   - Verifique se `AUTHORIZATION_API` está configurada
   - Confirme se a API remota está acessível

4. **Erro da API Google**:
   - Verifique se `GOOGLE_API_KEY` está configurada
   - Confirme se a API Gemini está habilitada

5. **Erro ao fazer upload**:
   - Verifique o tamanho do arquivo (máx. 10MB)
   - Certifique-se que é uma imagem (JPG, PNG)

## 🚀 Deploy em Produção

### Preparação

```bash
# Instale gunicorn
pip install gunicorn

# Colete arquivos estáticos
python manage.py collectstatic

# Configure o DEBUG=False em settings.py
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com']
```

### Usando Gunicorn

```bash
gunicorn setup.wsgi:application --bind 0.0.0.0:8000
```

## 🔗 Integração com EduVision-IA

Este projeto é a interface web do [EduVision-IA](https://github.com/CarlosBellator/EduVision-IA), que contém o backend de processamento. Para mais informações sobre o motor de IA, consulte o repositório principal.

## 👨‍💻 Autor

**Carlos Bellator**
- GitHub: [@CarlosBellator](https://github.com/CarlosBellator)
- Projeto Principal: [EduVision-IA](https://github.com/CarlosBellator/EduVision-IA)
- Projeto Web: [EduVision-IA-Site](https://github.com/CarlosBellator/EduVision-IA-Site)

---

<div align="center">
  <p><strong>EduVision IA - Tornando gráficos acessíveis através da tecnologia</strong></p>
  <p>Desenvolvido como Trabalho de Conclusão de Curso (TCC)</p>
  <p>🌐 Versão Web | 🤖 Powered by AI</p>
</div>
