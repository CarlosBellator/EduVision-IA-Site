# 📊 EduVision IA

**Sistema de Análise e Conversão de Gráficos para Objetos 3D Táteis**

Um projeto de TCC que envia imagens para uma API de detecção, extrai os gráficos encontrados, analisa seus dados com IA e converte o resultado em objetos 3D táteis (.STL) para auxiliar pessoas com deficiência visual no ensino de matemática e ciências.

## 🎯 Objetivo

O **EduVision IA** tem como objetivo tornar gráficos acessíveis para pessoas com deficiência visual, convertendo-os automaticamente em modelos 3D táteis que podem ser impressos em 3D.

## 🔧 Funcionalidades

- **🔍 Detecção Automática**: Envia a imagem para uma API remota e recupera os gráficos detectados
- **🧠 Análise Inteligente**: Emprega Google Gemini AI para extrair dados dos gráficos
- **📐 Conversão 3D**: Gera modelos STL táteis com:
  - Linhas do gráfico em relevo
  - Grade de referência
  - Eixos principais
  - Pontos de dados em Braille
  - Rótulos dos eixos em Braille
- **♿ Acessibilidade**: Focado em tornar conteúdo visual acessível

## 📁 Estrutura do Projeto

```
application/
├── main.py                # Arquivo principal
├── graph_crator.py        # Geração de objetos 3D
├── requirements.txt       # Dependências
├── results/               # Gráficos extraídos
└── image/                 # Imagens de exemplo
```

## 🔌 API de Detecção

O sistema usa a API remota abaixo para identificar gráficos nas imagens enviadas:

```text
https://carlosbellator-eduvision-ia-api.hf.space/detectar-grafico/
```

Ela exige uma chave de autorização enviada no cabeçalho `Authorization` no formato `Bearer <token>`.

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- GPU NVIDIA (opcional, mas recomendado para melhor performance)

### Instalação das Dependências

```bash
# Clone o repositório
git clone https://github.com/CarlosBellator/EduVision-IA.git
cd EduVision-IA/application

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
#venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
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
   # Copie o arquivo de exemplo
   cp .env.example .env
   
   # Edite o arquivo .env e adicione sua chave
   GOOGLE_API_KEY=sua_chave_api_aqui
   ```

3. **Instalar python-dotenv (se usar arquivo .env)**:
   ```bash
   pip install python-dotenv
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

3. **Verifique o endpoint remoto**:
   - O arquivo `main.py` já aponta para a URL da API de detecção
   - Não é necessário baixar nem treinar o modelo YOLO localmente

## 💻 Como Usar

### Execução Básica

```bash
python main.py
```

### Fluxo de Trabalho

1. **Importar Imagem**: Forneça o caminho da imagem contendo gráficos
2. **Detecção Remota**: A imagem é enviada para a API e os gráficos detectados são salvos em disco
3. **Seleção**: Escolha qual gráfico analisar
4. **Análise**: A IA extrai dados do gráfico selecionado
5. **Conversão**: Gera modelo 3D tátil em formato STL

## 🛠️ Tecnologias Utilizadas

- **🐍 Python**: Linguagem principal
- **👁️ OpenCV**: Processamento de imagens
- **🌐 Requests**: Comunicação com a API de detecção
- **🧠 Google Gemini AI**: Análise de gráficos
- **📐 NumPy**: Computação numérica
- **🔺 Shapely**: Geometria computacional
- **🎨 Trimesh**: Manipulação de malhas 3D
- **🔻 Triangle**: Triangulação

## 📊 Compatibilidade

### Sistemas Operacionais
- ✅ Windows
- ✅ Linux
- ✅ macOS

### Hardware
- ✅ **CPU**: Funciona em qualquer processador moderno
- ✅ **GPU**: Acelera processamento (NVIDIA CUDA recomendado)
- ✅ **RAM**: Mínimo 4GB, recomendado 8GB+

## 🔧 Configurações Avançadas

### Parâmetros do Modelo 3D

O arquivo `graficosobj.py` permite ajustar:

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

# Grade de referência
espessura_grade = 0.05
altura_grade = 0.15
espacamento_grade_x = 1.0
espacamento_grade_y = 1.0
```

## 📋 Requisitos do Sistema

### Mínimo
- **OS**: Windows 10/Linux/macOS
- **RAM**: 4GB
- **Python**: 3.8+
- **Espaço**: 2GB livres

### Recomendado
- **OS**: Windows 11/Ubuntu 20.04+/macOS Big Sur+
- **RAM**: 8GB+
- **GPU**: NVIDIA GTX 1060 ou superior
- **Python**: 3.10+
- **Espaço**: 5GB livres

## 🐛 Solução de Problemas

### Erros Comuns

1. **Erro de importação do OpenCV**:
   ```bash
   pip install opencv-python --upgrade
   ```

2. **Modelo YOLO não encontrado**:
   - Verifique se a API de detecção está disponível
   - Confirme se `AUTHORIZATION_API` está definido corretamente

3. **Erro da API Google**:
   - Verifique se a chave da API está correta
   - Confirme se a API está habilitada

4. **Erro de autorização na API de detecção**:
   - Verifique se `AUTHORIZATION_API` está correta
   - Confirme se o token ainda é válido

## 👨‍💻 Autor

**Carlos Bellator**
- GitHub: [@CarlosBellator](https://github.com/CarlosBellator)
- Projeto: [EduVision-IA](https://github.com/CarlosBellator/EduVision-IA)

---


<div align="center">
  <p><strong>EduVision IA - Tornando gráficos acessíveis através da tecnologia</strong></p>
  <p>Desenvolvido como Trabalho de Conclusão de Curso (TCC)</p>
</div>
