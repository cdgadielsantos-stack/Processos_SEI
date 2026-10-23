# ANEEL Monitor - MVP

Um monitor simples para buscar processos no portal SEI da ANEEL, aguardando a resolução humana do CAPTCHA, e extrair informações básicas.

## Funcionalidades

- Interface gráfica simples (Tkinter)
- Navegação automática até a página de pesquisa do SEI
- Aguarda o usuário resolver o CAPTCHA manualmente
- Pesquisa por intervalo de datas
- Coleta de informações básicas dos processos (número, data, assunto, tipo, URL)
- Armazenamento em banco de dados SQLite
- Exportação dos resultados para CSV
- Logs em tempo real

## Estrutura do Projeto

```
aneel_monitor/
├── app/
│   ├── browser/          # Controle do navegador (Playwright)
│   ├── scraper/          # Extração de dados das páginas de processo
│   ├── parsers/          # Parsers para extração de texto de documentos (PDF, DOCX, HTML, OCR)
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

## Pré-requisitos

- Python 3.12+
- Conta de acesso ao portal SEI da ANEEL (não fornecida pelo sistema)
- Navegador Chromium (será instalado via Playwright)

## Instalação

1. Clone o repositório ou copie os arquivos para uma pasta.

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   python -m venv .venv
   # No Windows:
   .venv\Scripts\activate
   # No Linux/macOS:
   source .venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Instale os navegadores do Playwright:
   ```bash
   playwright install chromium
   ```

5. (Opcional) Copie `.env.example` para `.env` e ajuste as variáveis de acordo com seu ambiente:
   ```bash
   copy .env.example .env
   ```

## Como Executar

1. Certifique-se de que o ambiente virtual está ativado.

2. Execute o programa:
   ```bash
   python main.py
   ```

3. Na interface gráfica:
   - Defina a data inicial e final (formato DD/MM/AAAA).
   - Clique em "Iniciar Monitoramento".
   - O navegador será aberto na página de pesquisa do SEI.
   - **Resolva o CAPTCHA manualmente** na janela do navegador que aparecer.
   - Após resolver o CAPTCHA, o sistema continuará automaticamente, preenchendo as datas e clicando em "Pesquisar".
   - Aguarde a coleta dos processos e a exibição dos logs.
   - Quando finalizar, você pode exportar os resultados para CSV usando o botão "Exportar CSV".
   - Use o botão "Parar" para interromper o processo a qualquer momento.

## Logs

Os logs são exibidos em tempo real na interface e também gravados em `logs/app.log`.

## Banco de Dados

O banco de dados SQLite será criado automaticamente em `data/aneel_monitor.db` contendo as tabelas:
- `processos`: armazena os processos coletados.
- `documentos`: (reservado para futura implementação de download e extração de documentos).

## Exportação

Os dados podem ser exportados para CSV contendo os campos:
- ID
- Número do Processo
- Data
- Assunto
- Tipo
- URL
- Data de Coleta

## Próximos Passos (Melhorias Futuras)

- Implementar download automático de documentos associados aos processos.
- Extrair texto dos documentos (PDF, DOCX, HTML) usando os parsers incluidos.
- Armazenar o texto extraído no banco de dados.
- Melhorar a interface com mais detalhes e controles.
- Adicionar suporte a proxies e configurações avançadas do navegador.
- Implementar testes unitários.
- Empacotar como executável standalone (via PyInstaller ou similar).

## Avisos

- Este sistema **não tenta burlar ou automatizar a resolução do CAPTCHA**. Ele aguarda a intervenção humana para passar pelo CAPTCHA, respeitando as medidas de segurança do portal.
- O uso deste script deve estar em conformidade com os termos de uso do portal SEI da ANEEL e da legislação aplicável.
- O sistema é fornecido como está, sem garantias. Use por sua própria conta e risco.

## Licença

Este projeto é de uso livre e educacional. Sinta-se à vontade para modificá-lo e melhorá-lo.

---
**ANEEL Monitor MVP** - Desenvolvido com Python e Playwright.