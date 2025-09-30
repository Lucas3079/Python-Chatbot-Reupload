# Deploy da CapBot

## Configuração para Railway

### 1. Variáveis de Ambiente Necessárias

Configure as seguintes variáveis de ambiente no Railway (NÃO coloque no GitHub):

```
GROQ_API_KEY=sua_chave_groq_aqui
WEB_SEARCH_ENABLED=True
RAILWAY_ENVIRONMENT=production
ALLOWED_ORIGINS=*
```

**IMPORTANTE**: 
- Nunca coloque chaves de API no código ou no GitHub
- Configure as variáveis diretamente no Railway
- Use a chave Groq que você já tem configurada localmente

### 2. Arquivos de Configuração

O projeto já inclui:
- `Procfile` - Configuração para Railway
- `railway.json` - Configurações específicas do Railway
- `requirements.txt` - Dependências Python

### 3. Estrutura do Projeto

```
├── app/                 # Backend FastAPI
├── frontend/           # Frontend HTML/CSS/JS
├── data/              # Dados de folha de pagamento
├── main.py            # Arquivo principal
├── requirements.txt   # Dependências
├── Procfile          # Configuração Railway
└── railway.json      # Configurações Railway
```

### 4. Deploy

1. Conecte o repositório ao Railway
2. Configure as variáveis de ambiente
3. O deploy será automático

### 5. URLs

- **API**: `https://seu-projeto.railway.app/`
- **Frontend**: `https://seu-projeto.railway.app/` (mesmo domínio)
- **Health Check**: `https://seu-projeto.railway.app/health`
- **Docs**: `https://seu-projeto.railway.app/docs`

### 6. Funcionalidades

✅ Chat com IA (Groq)
✅ RAG para consultas de folha de pagamento
✅ Busca na web
✅ Interface moderna com temas
✅ Histórico de conversas
✅ Sidebar colapsável
✅ Responsivo

### 7. Próximos Passos

Após o deploy bem-sucedido:
1. Testar todas as funcionalidades
2. Implementar sistema de login
3. Adicionar mais funcionalidades
