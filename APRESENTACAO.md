# ANEEL Monitor - MVP
## Apresentação do Projeto

---

### Slide 1: Visão Geral
**ANEEL Monitor - MVP**
- Monitor simples para buscar processos no portal SEI da ANEEL
- Interface gráfica com Tkinter
- Automação de navegação até a página de pesquisa
- Aguarda resolução manual do CAPTCHA pelo usuário
- Extrai informações básicas dos processos
- Armazenamento em banco de dados SQLite
- Exportação para CSV

---

### Slide 2: Problema que Resolve
- O portal SEI da ANEEL requer login e CAPTCHA para pesquisa de processos
- Processo manual de consulta é repetitivo e demorado
- Necessidade de automatização da navegação e coleta de dados
- Manter a conformidade com as medidas de segurança (CAPTCHA manual)

---

### Slide 3: Funcionalidades Principais
1. **Interface Gráfica Simples** (Tkinter)
2. **Navegação Automática** até a página de pesquisa do SEI
3. **Espera por CAPTCHA** - Usuário resolve manualmente
4. **Pesquisa por Intervalo de Datas**
5. **Coleta de Informações Básicas**:
   - Número do processo
   - Data
   - Assunto
   - Tipo
   - URL
6. **Armazenamento em Banco de Dados** (SQLite)
7. **Exportação dos Resultados** para CSV
8. **Logs em Tempo Real**

---

### Slide 4: Arquitetura do Projeto
```
aneel_monitor/
├── app/
│   ├── browser/          # Controle do navegador (Playwright)
│   ├── scraper/          # Extração de dados das páginas de processo
│   ├── parsers/          # Parsers para extração de texto (PDF, DOCX, HTML, OCR)
│   ├── database/         # Camada de acesso ao banco de dados (SQLAlchemy)
│   ├── services/         # Serviços de negócio (placeholder)
│   ├── models/           # Modelos SQLAlchemy
│   ├── ui/               # Interface do usuário (Tkinter) - atualmente em main.py
│   └── utils/            # Utilitários (logger)
├── downloads/            # Pasta para downloads de documentos
├── data/                 # Banco de dados SQLite
├── logs/                 # Arquivos de log
├── exports/              # Pasta para exportação de CSV
├── tests/                # Testes (vazio)
├── requirements.txt      # Dependências do Python
├── .env.example          # Exemplo de variáveis de ambiente
├── config.py             # Carregamento de configurações
├── main.py               # Ponto de entrada da aplicação
└── README.md             # Este arquivo
```

---

### Slide 5: Tecnologias Utilizadas
- **Python 3.12+**
- **Playwright** - Automação de navegador
- **Tkinter** - Interface gráfica
- **BeautifulSoup** - Parsing de HTML
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados embarcado
- **Pandas** - Exportação para CSV

---

### Slide 6: Como Funciona (Fluxo de Trabalho)
1. Usuário define intervalo de datas na interface
2. Clica em "Iniciar Monitoramento"
3. Navegador é aberto na página de pesquisa do SEI
4. **Usuário resolve o CAPTCHA manualmente** (janela do navegador)
5. Sistema preenche automaticamente as datas e clica em "Pesquisar"
6. Coleta links dos processos encontrados
7. Para cada processo:
   - Acessa a página do processo
   - Extrai número, data, assunto, tipo
   - Salva no banco de dados SQLite
8. Usuário pode exportar resultados para CSV
9. Logs exibidos em tempo real na interface e em arquivo

---

### Slide 7: Próximos Passos (Melhorias Futuras)
- Implementar download automático de documentos associados aos processos
- Extrair texto dos documentos (PDF, DOCX, HTML) usando os parsers incluidos
- Armazenar o texto extraído no banco de dados
- Melhorar a interface com mais detalhes e controles
- Adicionar suporte a proxies e configurações avançadas do navegador
- Implementar testes unitários
- Empacotar como executável standalone (via PyInstaller ou similar)

---

### Slide 8: Considerações importantes
- **Não tenta burlar ou automatizar a resolução do CAPTCHA**
- Aguarda intervenção humana para passar pelo CAPTCHA, respeitando as medidas de segurança
- Uso deve estar em conformidade com os termos de uso do portal SEI da ANEEL
- Sistema fornecido como está, sem garantias
- Uso por conta e risco do usuário

---

### Slide 9: Licença e Contribuindo
- Projeto de uso livre e educacional
- Sinta-se à vontade para modificá-lo e melhorá-lo
- Contribuições são bem-vindas!

---

### Slide 10: Obrigado!
**ANEEL Monitor MVP** - Desenvolvido com Python e Playwright
Qualquer dúvida?