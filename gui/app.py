import os
import threading
from tkinter import Tk, Button, Label, messagebox, filedialog, DISABLED, NORMAL, Entry, Frame, BooleanVar, Checkbutton
from tkinter.ttk import Progressbar
from pandastable import Table
import pandas as pd
import re

from scraper.google_scraper import GoogleImageScraper
from services.image_service import save_image_from_url, resize_images, zip_folder


class CustomTable(Table):
    def formatCell(self, row, colname):

        try:
            value = self.model.df.at[row, colname]
            if colname == 'Downloaded':
                return 'V' if value else 'X'
            return str(value)
        except Exception:
            return ""



class ImageScraperApp:
    def __init__(self):
        self.scraper = GoogleImageScraper()
        self.window = Tk()

        self.window.title("Google Scraper V1.1")
        self.window.geometry("900x700")

        # FRAME: Ações com arquivo Excel
        file_frame = Frame(self.window)
        file_frame.pack(pady=5)

        self.load_button = Button(file_frame, text="Carregar Excel", command=self.load_excel)
        self.load_button.grid(row=0, column=0, padx=5)

        self.save_button = Button(file_frame, text="Salvar Excel", command=self.save_excel, state=DISABLED)
        self.save_button.grid(row=0, column=1, padx=5)

        self.reset_button = Button(file_frame, text="Reiniciar", command=self.reset_process)
        self.reset_button.grid(row=0, column=2, padx=5)

        # FRAME: Ações de busca
        search_frame = Frame(self.window)
        search_frame.pack(pady=5)

        self.start_button = Button(search_frame, text="Iniciar Buscas", command=self.start_search, state=DISABLED)
        self.start_button.grid(row=0, column=0, padx=5)

        Label(search_frame, text="Largura").grid(row=0, column=1)
        self.width_entry = Entry(search_frame, width=5)
        self.width_entry.grid(row=0, column=2)

        Label(search_frame, text="Altura").grid(row=0, column=3)
        self.height_entry = Entry(search_frame, width=5)
        self.height_entry.grid(row=0, column=4)



        self.resize_button = Button(search_frame, text="Redimensionar Imagens", command=self.resize_images)
        self.resize_button.grid(row=0, column=5, padx=5)

        self.zip_button = Button(search_frame, text="Zipar Imagens", command=self.zip_images)

        self.zip_button.grid(row=0, column=6, padx=5)
        # Checkbox: Incluir Grupo produto na busca
        self.include_group = BooleanVar()
        self.include_group_checkbox = Checkbutton(
            search_frame,
            text="Incluir 'Grupo produto' na busca",
            variable=self.include_group
        )
        self.include_group_checkbox.grid(row=0, column=7, padx=5)

        # FRAME: Manipulação de dados
        clean_frame = Frame(self.window)
        clean_frame.pack(pady=5)

        self.clean_button = Button(clean_frame, text="Limpar Caracteres", command=self.remove_special_chars)
        self.clean_button.grid(row=0, column=0, padx=5)

        self.trim_button = Button(clean_frame, text="Remover Espaços", command=self.strip_spaces_from_column)
        self.trim_button.grid(row=0, column=1, padx=5)

        # Barra de progresso
        self.progress = Progressbar(self.window, length=600, mode='determinate')
        self.progress.pack(pady=10)

        # Logs
        self.log_label = Label(self.window, text="", anchor='w', justify='left')
        self.log_label.pack(fill='x', padx=10, pady=5)

        # Área da tabela (criada depois do load_excel)
        self.table = None
        self.df = None
        self.table_frame = None

        self.images_folder = os.path.join(os.path.expanduser("~"), "Desktop", "imagens")
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)

    def log(self, message):
        self.log_label.config(text=message)
        self.window.update_idletasks()

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls *.xlsx")])
        if not file_path:
            return
        try:
            self.df = pd.read_excel(file_path, dtype={"Código Interno": str})
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar Excel:\n{e}")
            return

        if 'Downloaded' not in self.df.columns:
            self.df['Downloaded'] = False

        # Destroi o frame anterior se existir
        if self.table_frame:
            self.table_frame.destroy()
            self.table_frame = None
            self.table = None

        # Cria novo frame para a tabela
        self.table_frame = Frame(self.window)
        self.table_frame.pack(fill='both', expand=True)

        self.table = CustomTable(self.table_frame, dataframe=self.df, editable=True)
        self.table.show()

        self.start_button.config(state=NORMAL)
        self.save_button.config(state=NORMAL)

    def start_search(self):
        def disable_buttons():
            self.start_button.config(state=DISABLED)
            self.load_button.config(state=DISABLED)

        def enable_buttons():
            self.start_button.config(state=NORMAL)
            self.load_button.config(state=NORMAL)

        def task():
            if self.table is None:
                messagebox.showwarning("Warning", "Carregue a planilha antes de inciar as buscas.")
                self.window.after(0, enable_buttons)
                return

            self.df = self.table.model.df

            if 'Nome Produto' not in self.df.columns or 'Código Interno' not in self.df.columns:
                messagebox.showerror("Error", "Planilha deve conter as colunas: 'Nome Produto' and 'Código Interno'.")
                self.window.after(0, enable_buttons)
                return

            resize = None
            try:
                w, h = int(self.width_entry.get()), int(self.height_entry.get())
                resize = (w, h)
            except Exception:
                pass

            total = len(self.df)
            self.window.after(0, lambda: self.progress.config(maximum=total, value=0))

            for idx, row in self.df.iterrows():
                self.window.after(0, lambda v=idx + 1: self.progress.config(value=v))
                produto = row['Nome Produto']
                codigo = row['Código Interno']

                if self.df.at[idx, 'Downloaded'] == True:
                    continue
                if not isinstance(produto, str) or not produto.strip():
                    continue
                try:
                    codigo_str = str(int(float(codigo)))
                except Exception:
                    continue


                if any(f.startswith(codigo_str) for f in os.listdir(self.images_folder) if os.path.isfile(os.path.join(self.images_folder, f))):
                    self.df.at[idx, 'Downloaded'] = True
                    continue

                grupo = row.get('Grupo Produto', '')
                if self.include_group.get() and isinstance(grupo, str) and grupo.strip():
                    query = f"{grupo.strip()} {produto.strip()} Fundo Branco"
                else:
                    query = f"{produto.strip()} Fundo Branco"

                image_url = self.scraper.fetch_first_valid_image(query)
                if image_url:
                    success = save_image_from_url(image_url, folder=self.images_folder, filename=codigo_str, resize=resize)
                    if success:
                        self.df.at[idx, 'Downloaded'] = True

                self.window.after(0, lambda: self.table.redraw())

            self.window.after(0, lambda: messagebox.showinfo("Finished", "Finalizado!."))
            self.window.after(0, enable_buttons)
            self.window.after(0, lambda: self.progress.config(value=0))

        disable_buttons()
        threading.Thread(target=task, daemon=True).start()

    def resize_images(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Digite largura e altura válidos.")
            return

        count = resize_images(folder=self.images_folder, width=width, height=height)

        messagebox.showinfo("Resize Complete", f"{count} imagens convertidas e transformadas em  PNG.")

    def zip_images(self):
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP file", "*.zip")])

        messagebox.showinfo("Complete", f"Arquivo ZIP Criado")
        if not zip_path:
            return
        zip_folder(folder=self.images_folder, zip_path=zip_path)

    def run(self):
        self.window.mainloop()
        self.scraper.close()

    def reset_process(self):
        # Destrói o frame da tabela completamente se ele existir
        if self.table_frame:
            self.table_frame.destroy()
            self.table_frame = None
            self.table = None

        # Reseta o DataFrame
        self.df = None

        # Desativa botões
        self.start_button.config(state=DISABLED)
        self.save_button.config(state=DISABLED)

        # Limpa seleção
        self.selected_column = None

    def remove_special_chars(self):
        col = self.get_selected_column()
        if not col:
            messagebox.showwarning("Aviso", "Selecione uma coluna na tabela.")
            return

        self.df[col] = self.df[col].astype(str).apply(lambda x: re.sub(r'[^\w\s]', '', x))
        self.table.updateModel(self.table.model)
        self.table.redraw()
        messagebox.showinfo("Pronto", f"Caracteres especiais removidos da coluna '{col}'.")

    def strip_spaces_from_column(self):
        col = self.get_selected_column()
        if not col:
            messagebox.showwarning("Aviso", "Selecione uma coluna na tabela.")
            return

        self.df[col] = self.df[col].astype(str).str.replace(" ", "")
        self.table.updateModel(self.table.model)
        self.table.redraw()
        messagebox.showinfo("Pronto", f"Espaços removidos da coluna '{col}'.")

    def get_selected_column(self):
        try:
            col_index = self.table.getSelectedColumn()
            return self.df.columns[col_index]
        except Exception:
            return None


    def save_excel(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Nenhuma planilha carregada.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return

        try:
            df_to_save = self.df.drop(columns=["Downloaded"], errors="ignore")
            df_to_save.to_excel(path, index=False)
            messagebox.showinfo("Sucesso", f"Planilha salva em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{e}")



