import os
import threading
import pandas as pd
import re
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import filedialog, messagebox
from pandastable import Table
import unicodedata
import string
from tkinter import messagebox

from PIL import Image
from scraper.google_scraper import GoogleImageScraper
from services.image_service import save_image_from_url, resize_images, zip_folder

load_icon = CTkImage(light_image=Image.open("icons/load.png"), size=(20, 20))
reload_icon = CTkImage(light_image=Image.open("icons/reload.png"), size=(20, 20))
save_icon = CTkImage(light_image=Image.open("icons/save.png"), size=(20, 20))
play_icon = CTkImage(light_image=Image.open("icons/play.png"), size=(20, 20))
reduce_icon = CTkImage(light_image=Image.open("icons/reduce.png"), size=(20, 20))
zip_icon = CTkImage(light_image=Image.open("icons/zip.png"), size=(20, 20))
cut_icon = CTkImage(light_image=Image.open("icons/cut.png"), size=(20, 20))
clear_icon = CTkImage(light_image=Image.open("icons/clear_char.png"), size=(20, 20))


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
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("Google Scraper V1.1")
        self.window.geometry("950x750")

        self.table = None
        self.df = None
        self.table_frame = None

        self.images_folder = os.path.join(os.path.expanduser("~"), "Desktop", "imagens")
        os.makedirs(self.images_folder, exist_ok=True)

        # --- PRIMEIRA LINHA DE BOTÕES ---
        self.file_frame = ctk.CTkFrame(self.window)
        self.file_frame.pack(pady=5, fill='x')

        # Container para alinhar os botões à direita
        file_buttons_container = ctk.CTkFrame(self.file_frame)
        file_buttons_container.pack(side='right')

        self.reset_button = ctk.CTkButton(
            file_buttons_container,
            text="Reiniciar",
            font=("Roboto", 16),
            anchor="center",
            image=reload_icon,
            compound="left",
            command=self.reset_process,
            width=160,
            height=40)
        self.reset_button.pack(side='right', padx=10, pady=5)

        self.save_button = ctk.CTkButton(
            file_buttons_container,
            text="Salvar Excel",
            font=("Roboto", 16),
            anchor="center",
            image=save_icon,
            compound="left",
            command=self.save_excel,
            state="disabled",
            width=160,
            height=40)
        self.save_button.pack(side='right', padx=10, pady=5)

        self.load_button = ctk.CTkButton(
            file_buttons_container,
            text="Carregar Excel",
            font=("Roboto", 16),
            anchor="center",
            image=load_icon,
            compound="left",
            command=self.load_excel,
            width=160,
            height=40)
        self.load_button.pack(side='right', padx=10, pady=5)

        # --- SEGUNDA LINHA DE BOTÕES ---
        self.config_frame = ctk.CTkFrame(self.window)
        self.config_frame.pack(pady=5, fill='x')
        # --- Container para alinhamento
        line1_frame = ctk.CTkFrame(self.config_frame)
        line1_frame.pack(fill='x', pady=5, anchor='w')

        self.start_button = ctk.CTkButton(
            line1_frame,
            text="Iniciar Buscas",
            font=("Roboto", 16),
            anchor="center",
            image=play_icon,
            compound="left",
            width=160,
            height=40,
            command=self.start_search,
            state="disabled"
        )
        self.start_button.pack(side='left', padx=10)

        self.zip_button = ctk.CTkButton(
            line1_frame,
            text="Compactar Imagens",
            font=("Roboto", 16),
            anchor="center",
            image=zip_icon,
            compound="left",
            command=self.zip_images,
            width=160,
            height=40)
        self.zip_button.pack(side='left', padx=10)

        # --- FRAME 3: Imagens e checkbox + limpeza (linha 3 e 4) ---
        self.actions_frame = ctk.CTkFrame(self.window)
        self.actions_frame.pack(pady=5, fill='x')

        # Linha 3: Redimensionar e Zipar Imagens
        line2_frame = ctk.CTkFrame(self.actions_frame)
        line2_frame.pack(fill='x', pady=5, anchor='w')

        self.resize_button = ctk.CTkButton(
            line2_frame,
            text="Redimensionar",
            font=("Roboto", 16),
            anchor="center",
            image=reduce_icon,
            compound="left",
            command=self.resize_images,
            width=160,
            height=40)
        self.resize_button.pack(side='left', padx=10)

        ctk.CTkLabel(
            line2_frame,
            text="Largura:",
            font=("Roboto", 16)).pack(side='left', padx=(20, 5), pady=5)

        self.width_entry = ctk.CTkEntry(line2_frame, width=60)
        self.width_entry.pack(side='left', padx=10, pady=5)

        ctk.CTkLabel(
            line2_frame,
            text="Altura:",
            font=("Roboto", 16)).pack(side='left', padx=(20, 5), pady=5)

        self.height_entry = ctk.CTkEntry(line2_frame, width=60)
        self.height_entry.pack(side='left', padx=1, pady=5)

        self.clean_button = ctk.CTkButton(
            line2_frame,
            text="Limpa Caracteres",
            font=("Roboto", 16),
            anchor="center",
            image=clear_icon,
            compound="left",
            command=self.remove_special_chars,
            width=180,
            height=40)
        self.clean_button.pack(side='right', padx=10)

        self.trim_button = ctk.CTkButton(
            line2_frame,
            text="Remove Espaços",
            font=("Roboto", 16),
            anchor="center",
            image=cut_icon,
            compound="left",
            command=self.strip_spaces_from_column,
            width=180,
            height=40)
        self.trim_button.pack(side='right', padx=10)

        # Linha 4: Checkbox + Limpar Caracteres + Remover Espaços
        line3_frame = ctk.CTkFrame(self.actions_frame)
        line3_frame.pack(fill='x', pady=5, anchor='w')

        self.include_group = ctk.BooleanVar()
        self.include_group_checkbox = ctk.CTkCheckBox(
            line3_frame,
            text="Incluir Grupo na busca",
            variable=self.include_group
        )
        self.include_group_checkbox.pack(side='left', padx=10)

        self.only_group = ctk.BooleanVar()
        self.only_group_checkbox = ctk.CTkCheckBox(
            line3_frame,
            text="Buscar somente grupo",
            variable=self.only_group
        )
        self.only_group_checkbox.pack(side='left', padx=10)



        self.progress_frame = ctk.CTkFrame(self.window)
        self.progress_frame.pack(pady=5, fill='x')

        self.progress = ctk.CTkProgressBar(self.progress_frame)
        self.progress.pack(fill='x', padx=10, pady=5)
        self.progress.set(0)

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

        if self.table_frame:
            self.table_frame.destroy()
            self.table_frame = None
            self.table = None

        self.table_frame = ctk.CTkFrame(self.window)
        self.table_frame.pack(fill='both', expand=True)

        self.table = CustomTable(self.table_frame, dataframe=self.df, editable=True)
        self.table.show()

        self.start_button.configure(state="normal")
        self.save_button.configure(state="normal")

    def start_search(self):
        def disable_buttons():
            self.start_button.configure(state="disabled")
            self.load_button.configure(state="disabled")

        def enable_buttons():
            self.start_button.configure(state="normal")
            self.load_button.configure(state="normal")

        def task():
            if self.table is None:
                messagebox.showwarning("Aviso", "Carregue a planilha antes.")
                enable_buttons()
                return

            self.df = self.table.model.df

            if 'Nome Produto' not in self.df.columns or 'Código Interno' not in self.df.columns:
                messagebox.showerror("Erro", "Colunas obrigatórias: 'Nome Produto' e 'Código Interno'.")
                enable_buttons()
                return

            try:
                resize = (int(self.width_entry.get()), int(self.height_entry.get()))
            except Exception:
                resize = None

            total = len(self.df)
            self.window.after(0, lambda: self.progress.configure(mode="determinate"))
            self.window.after(0, lambda: self.progress.set(0))

            for idx, row in self.df.iterrows():
                self.window.after(0, lambda v=(idx + 1) / total: self.progress.set(v))

                produto = row['Nome Produto']
                codigo = row['Código Interno']

                if self.df.at[idx, 'Downloaded'] is True:
                    continue
                if not isinstance(produto, str) or not produto.strip():
                    continue

                try:
                    codigo_str = str(int(float(codigo)))
                except Exception:
                    continue

                if any(f.startswith(codigo_str) for f in os.listdir(self.images_folder)):
                    self.df.at[idx, 'Downloaded'] = True
                    continue

                grupo = row.get('Grupo Produto', '').strip()

                # Aqui vem a lógica nova
                if self.only_group.get():
                    if grupo:
                        query = f"{grupo} Fundo Branco"
                    else:
                        # Se só grupo está marcado, mas não tem grupo no dado, pula a linha
                        continue
                else:
                    # comportamento antigo
                    if self.include_group.get() and grupo:
                        query = f"{grupo} {produto.strip()} Fundo Branco"
                    else:
                        query = f"{produto.strip()} Fundo Branco"

                self.window.after(0, lambda q=query: self.search_label.configure(text=f"Buscando: {q}"))

                image_url = self.scraper.fetch_first_valid_image(query)
                if image_url:
                    success = save_image_from_url(image_url, folder=self.images_folder, filename=codigo_str,
                                                  resize=resize)
                    if success:
                        self.df.at[idx, 'Downloaded'] = True

                self.window.after(0, lambda: self.table.redraw())

            self.window.after(0, lambda: messagebox.showinfo("Finalizado", "Busca concluída."))
            self.window.after(0, enable_buttons)
            self.window.after(0, lambda: self.progress.set(0))

        disable_buttons()
        threading.Thread(target=task, daemon=True).start()

    def resize_images(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite largura e altura válidas.")
            return

        count = resize_images(folder=self.images_folder, width=width, height=height)
        messagebox.showinfo("Resize", f"{count} imagens redimensionadas.")

    def zip_images(self):
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP file", "*.zip")])
        if not zip_path:
            return
        zip_folder(folder=self.images_folder, zip_path=zip_path)
        messagebox.showinfo("Concluído", "Imagens compactadas com sucesso.")

    def reset_process(self):
        if self.table_frame:
            self.table_frame.destroy()
            self.table_frame = None
            self.table = None

        self.df = None
        self.start_button.configure(state="disabled")
        self.save_button.configure(state="disabled")

    def remove_special_chars(self):
        col = self.get_selected_column()
        if not col:
            messagebox.showwarning("Aviso", "Selecione uma coluna.")
            return

        def remove_accents_and_special_chars(text):
            # Normaliza para decompor acentos
            nfkd_form = unicodedata.normalize('NFKD', text)
            # Remove os caracteres de acentuação
            without_accents = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
            # Define os caracteres permitidos: letras ascii, números e espaço
            allowed_chars = string.ascii_letters + string.digits + " "
            # Filtra só os permitidos, removendo pontuação e outros caracteres especiais
            return "".join(c for c in without_accents if c in allowed_chars)

        self.df[col] = self.df[col].astype(str).apply(remove_accents_and_special_chars)
        self.table.updateModel(self.table.model)
        self.table.redraw()
        messagebox.showinfo("Pronto", f"Caracteres especiais removidos da coluna '{col}'.")

    def strip_spaces_from_column(self):
        col = self.get_selected_column()
        if not col:
            messagebox.showwarning("Aviso", "Selecione uma coluna.")
            return

        self.df[col] = self.df[col].astype(str).str.replace(" ", "")
        self.table.updateModel(self.table.model)
        self.table.redraw()
        messagebox.showinfo("Pronto", f"Espaços removidos da coluna '{col}'.")

    def get_selected_column(self):
        if self.table and self.table.currentcol is not None:
            return self.table.model.df.columns[self.table.currentcol]
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

    def run(self):
        self.search_label = ctk.CTkLabel(self.progress_frame, text="", font=("Roboto", 14))
        self.search_label.pack(pady=(0, 10))

        self.window.mainloop()


if __name__ == "__main__":
    app = ImageScraperApp()
    app.run()
