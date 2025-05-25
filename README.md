# Google Image Scraper GUI

Uma aplicação desktop com interface gráfica para automatizar a busca e o download de imagens do Google com base em uma planilha Excel contendo produtos. Ideal para catálogos, e-commerces ou profissionais que precisam buscar imagens de forma padronizada (ex: fundo branco).



---

## 🔧 Funcionalidades

- 📥 Leitura de arquivos Excel (`.xls` ou `.xlsx`)
- 🔍 Busca automatizada de imagens no Google (com Selenium)
- 💾 Download e salvamento automático na Área de Trabalho do usuário
- 📐 Redimensionamento em lote (com conversão para PNG)
- 🗜️ Compactação das imagens em um `.zip`
- 📊 Tabela interativa com status de download (✅ ou ❌)

---

## 🖥️ Tecnologias Utilizadas

- Python 3.10+
- Selenium
- Tkinter (Interface Gráfica)
- Pandas / Pandastable
- Pillow
- WebDriver Manager

---

## 📦 Instalação

### 1. Clone o projeto

```bash
git clone https://github.com/seu-usuario/google-image-scraper.git
cd google-image-scraper
```

### 2. Crie um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### Como Usar
1.Execute o programa com:
```bash
python main.py
```
2. Clique em "Carregar Excel" e selecione uma planilha contendo as colunas:

```Nome Produto``` – Nome para busca no Google

```Código Interno``` – Nome do arquivo a ser salvo

Clique em <strong>"iniciar Buscas"</strong> para iniciar.

Utilize as opções de redimensionamento e zip conforme necessidade.

## 📌 Observações
As imagens são salvas automaticamente no diretório ```Desktop``` do Usuário Administrador, dentro da pasta ```Imagens```.

```C:\Users\<Seu Usuário\Desktop\Imagens```

Evite nomes duplicados de código interno.

O scraping pode falhar se o Google bloquear temporariamente o navegador. Tente de novo após alguns minutos.


📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.


## 👨‍💻 Autor
Desenvolvido por Lucas Garcia – LinkedIn : <link> https://www.linkedin.com/in/lucasgarciaamorim/ <link/>



                
