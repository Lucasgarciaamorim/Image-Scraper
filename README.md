📘 Documentação Técnica – Google Image Scraper com Interface Gráfica
📌 Visão Geral
Este projeto é uma aplicação desktop com interface gráfica (Tkinter) que permite automatizar o processo de busca e download da primeira imagem válida de um produto no Google Imagens, com base em uma planilha Excel contendo os nomes dos produtos. A aplicação também permite redimensionar imagens, compactar a pasta de imagens baixadas e exportar os dados tratados.

🎯 Objetivos
Automatizar a coleta de imagens de produtos com fundo branco.

Salvar as imagens com base no código interno fornecido na planilha.

Permitir redimensionamento e compactação das imagens.

Apresentar feedback visual e uma tabela interativa ao usuário.

🧱 Estrutura do Projeto
bash
Copiar
Editar
POSCONTROLE/
│
├── main.py                  # Ponto de entrada da aplicação
├── gui/
│   └── app.py               # Interface gráfica da aplicação
│
├── scraper/
│   └── google_scraper.py    # Lógica de scraping com Selenium
│
├── services/
│   └── image_service.py     # Funções de manipulação de imagens (download, resize, zip)
│
├── assets/
│   └── images/              # Local onde as imagens são salvas
│
├── tests/
│   ├── test_scraper.py      # Testes do scraper com mocks
│   ├── test_image_service.py# Testes de manipulação de imagem
│   └── test_app_logic.py    # Testes de integração de lógica GUI
│
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação resumida para desenvolvedores
⚙️ Funcionalidades
1. Carregamento da Planilha
Aceita arquivos .xls e .xlsx

Exige colunas: Nome Produto e Código Interno

Adiciona automaticamente a coluna Downloaded

2. Busca e Download de Imagem
Faz busca no Google Imagens com termo "{Nome Produto} fundo branco"

Salva a primeira imagem válida encontrada

Nome do arquivo = Código Interno.png

Armazena as imagens na pasta assets/images/ (ou Área de Trabalho)

3. Redimensionamento
Permite definir largura e altura

Redimensiona todas as imagens da pasta para PNG com essas dimensões

4. Compactação
Compacta todas as imagens da pasta em um .zip customizado

5. Tabela Interativa
Tabela mostra produtos e status (TRUE / FALSE) se imagem foi baixada

Atualiza dinamicamente durante a execução

🧪 Testes Automatizados
Os testes são escritos com pytest e usam unittest.mock para simular chamadas da Web e manipulação de arquivos:

test_scraper.py: testa busca de imagens e tratamento de erros

test_image_service.py: testa redimensionamento, download e zip

test_app_logic.py: valida carregamento de planilha, lógica de controle e callbacks

Para rodar os testes:

bash
Copiar
Editar
pytest tests/
💾 Requisitos
Python 3.10+

Google Chrome

ChromeDriver compatível (instalado automaticamente via webdriver-manager)

📦 Dependências
Instale com:

bash
Copiar
Editar
pip install -r requirements.txt
Conteúdo típico do requirements.txt:

txt
Copiar
Editar
pandas
selenium
webdriver-manager
Pillow
openpyxl
tk
pandastable
🚀 Execução
Execute com:

bash
Copiar
Editar
python main.py
