# CapBot - Chatbot de Análise Financeira

Um chatbot inteligente com RAG (Retrieval-Augmented Generation) para consultas de folha de pagamento, desenvolvido para o processo seletivo da Capgemini.

Link da IA funcionando online:

https://python-chatbot-3.onrender.com/

!AVISO! Pela falta de tempo, o render foi o único site que eu consegui fazer a IA funcionar online, porém ele não deixa ficar online por mais de 15 minutos. Para funcionar, basta entrar no link e esperar 2 - 3 minutos para o render ligar o site.

## Sobre

O **CapBot** é uma aplicação de IA conversacional que combina:
- **Conversação geral** com LLMs (OpenAI/Groq)
- **Consultas específicas** de folha de pagamento via RAG
- **Busca na web** para informações externas
- **Interface moderna** estilo ChatGPT

## Tecnologias

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **IA:** OpenAI API, Groq API, RAG com embeddings
- **Dados:** Pandas, CSV
- **Deploy:** Railway, Docker

## Instalação Passo a Passo

### Pré-requisitos
- Python 3.8 ou superior
- Git (para clonar o repositório)

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd chatbot-rag-folha-pagamento
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

**Nota:** Se der erro, tente:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Teste se está funcionando
```bash
python main.py
```

Se aparecer algo como "Uvicorn running on http://localhost:8000", está funcionando! Pressione `Ctrl+C` para parar.

## Como Usar

### Opção 1: Mais Simples (Recomendado para iniciantes)

**Passo 1:** Execute apenas um comando:
```bash
python main.py
```

**Passo 2:** Abra seu navegador e acesse:
```
http://localhost:8000
```

**Pronto!** O chatbot já está funcionando em modo demo.

### Opção 2: Interface Separada (Para desenvolvedores)

**Terminal 1 - API:**
```bash
python main.py
```

**Terminal 2 - Frontend:**
```bash
python -m http.server 3000 --directory frontend
```

**Acesse:** http://localhost:3000

### Opção 3: Script Automático (Windows)

```bash
start_servers.bat
```

## Configuração de API Keys (Opcional)

**IMPORTANTE:** O projeto funciona perfeitamente sem configuração! As chaves são apenas para usar LLMs reais.

### Para usar LLMs reais:

**1. Obtenha uma chave gratuita do Groq:**
- Acesse: https://console.groq.com/keys
- Crie uma conta gratuita
- Gere uma nova chave

**2. Configure a chave:**
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env e adicione sua chave
GROQ_API_KEY=sua_chave_groq_aqui
```

**3. Reinicie o projeto:**
```bash
python main.py
```

### Diferenças:
- **Sem chave:** Modo demo com respostas simuladas
- **Com chave:** Respostas reais de IA

## Funcionalidades

### Consultas de Folha de Pagamento
- Salários líquidos por funcionário e período
- Descontos (INSS, IRRF)
- Bônus e benefícios
- Datas de pagamento
- Análises comparativas

### Recursos Extras
- Interface moderna com 4 temas
- Histórico de conversas
- Sidebar colapsível
- Busca na web simplificada
- Modo demo (sem API keys)

## Exemplos de Uso

```
"Quanto recebi de salário líquido em maio de 2025? (Ana Souza)"
"Qual foi o total líquido pago no primeiro trimestre de 2025?"
"Quem recebeu o maior bônus em 2025?"
"Qual a taxa Selic atual?"
```

## API Endpoints

- `POST /chat` - Enviar mensagem
- `GET /health` - Status da API
- `GET /docs` - Documentação Swagger

## Estrutura do Projeto

```
├── app/                    # Backend FastAPI
│   ├── api.py             # Endpoints principais
│   ├── config.py          # Configurações
│   ├── llm_service.py     # Integração com LLMs
│   ├── rag_system.py      # Sistema RAG
│   └── ...
├── frontend/              # Interface HTML/CSS/JS
│   ├── index.html         # Página principal
│   ├── style.css          # Estilos
│   └── script.js          # Lógica frontend
├── data/                  # Dados
│   └── payroll.csv        # Dataset de folha
└── requirements.txt       # Dependências
```

## Deploy

### Railway (Recomendado)
1. Conecte o repositório ao Railway
2. Configure as variáveis de ambiente
3. Deploy automático

### Docker
```bash
docker build -t capbot .
docker run -p 8000:8000 capbot
```

## Testes

```bash
# Testar API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, como você está?"}'

# Testar saúde da API
curl http://localhost:8000/health
```

## Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Pare outros processos na porta 8000 ou use outra porta
python main.py --port 8001
```

### Erro: "Permission denied"
```bash
# No Windows, execute como administrador
# No Linux/Mac, use sudo se necessário
```
### Limitações
1. Alucina um pouco, talvez tenha que mandar a pergunta sobre o financeiro (do desafio) 2x
2. Não está completamente responsivo, especialmente no celular
3. Normalmente precisa clicar no X duas vezes para poder excluir uma conversa

### Não consegue acessar http://localhost:8000
1. Verifique se o comando `python main.py` está rodando
2. Aguarde aparecer "Application startup complete"
3. Tente http://127.0.0.1:8000

## Autor

Lucas Monteiro - https://github.com/Lucas3079