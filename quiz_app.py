import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import json

class QuizApp:
    def __init__(self, root):
        # Configuração inicial da janela
        self.root = root
        self.root.title("Aventura de Quiz")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        # Paleta de cores ajustada
        self.colors = {
            'dark_green': '#2E7D32',    # Verde escuro para acertos
            'light_green': '#A5D6A7',   # Fundo suave
            'dark_purple': '#6A1B9A',   # Roxo para erros
            'light_purple': '#E1BEE7',  # Roxo mais claro para a caixa de texto
            'white': '#FFFFFF',         # Branco para fundos
            'button_bg': '#4CAF50',     # Verde vibrante para botões
            'button_text': '#000000',   # Preto para texto dos botões
            'button_active': '#7B1FA2'  # Roxo ativo
        }

        # Variáveis principais
        self.questions = []
        self.current_question = 0
        self.correct_answers = 0
        self.total_questions = 0
        self.stats = {"correct": [], "wrong": []}
        self.pdf_files = []
        self.attempts = self.load_previous_attempts()
        self.current_mode = None  # 'open' para resposta aberta, 'multiple' para múltipla escolha
        self.current_difficulty = None  # 'Iniciante', 'Estudado', 'Pronto para a Prova'
        self.selected_answer = tk.StringVar()  # Para armazenar a escolha no modo de múltipla escolha
        self.showing_stats = False  # Controle para alternar entre menu e estatísticas
        self.showing_mode = False  # Controle para alternar entre menu e seleção de modo
        self.showing_difficulty = False  # Controle para alternar entre menu e seleção de dificuldade
        self.showing_quiz_selection = False  # Controle para alternar entre menu e seleção de quiz

        # Carregar perguntas do arquivo JSON
        self.load_questions_from_json()

        # Configuração da grade
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Estilização
        self.style = ttk.Style()
        self.configure_styles()

        # Tela inicial
        self.show_initial_screen()
        self.root.bind('<Configure>', self.on_resize)

    def load_questions_from_json(self):
        """Carrega perguntas e respostas do arquivo JSON."""
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                self.all_questions = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'questions.json' não encontrado!")
            self.all_questions = {}
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao ler o arquivo 'questions.json'. Verifique o formato!")
            self.all_questions = {}

    # Configuração da interface
    def configure_styles(self):
        """Define os estilos visuais da aplicação."""
        self.root.configure(bg=self.colors['light_green'])
        self.style.configure('TFrame', background=self.colors['light_green'])
        self.style.configure('TLabel', background=self.colors['light_green'], 
                           foreground=self.colors['dark_purple'])
        self.style.configure('TButton', background=self.colors['button_bg'], 
                           foreground=self.colors['button_text'])
        self.style.map('TButton', background=[('active', self.colors['button_active'])],
                      foreground=[('active', self.colors['white'])])
        self.style.configure('TEntry', fieldbackground=self.colors['white'])
        self.style.configure('TRadiobutton', background=self.colors['light_green'],
                           foreground=self.colors['dark_purple'])

    def update_sizes(self):
        """Ajusta tamanhos de texto e elementos dinamicamente."""
        width = self.root.winfo_width()
        base_font_size = max(10, min(16, int(width / 50)))
        question_font_size = max(16, min(24, int(width / 30)))
        wrap_length = int(width * 0.7)

        self.style.configure('TLabel', font=('Arial', base_font_size))
        self.style.configure('TButton', font=('Arial', base_font_size-1, 'bold'))
        self.style.configure('TRadiobutton', font=('Arial', base_font_size))

        # Verifica se os widgets existem antes de configurá-los
        if hasattr(self, 'title_label') and self.title_label.winfo_exists():
            self.title_label.configure(font=('Arial', base_font_size, 'bold'), wraplength=wrap_length)
        if hasattr(self, 'welcome_label') and self.welcome_label.winfo_exists():
            self.welcome_label.configure(font=('Arial', base_font_size, 'bold'), wraplength=wrap_length)
        if hasattr(self, 'question_label') and self.question_label.winfo_exists():
            self.question_label.configure(font=('Arial', question_font_size), wraplength=wrap_length)
        if hasattr(self, 'result_label') and self.result_label.winfo_exists():
            self.result_label.configure(font=('Arial', base_font_size, 'italic'), wraplength=wrap_length)
        if hasattr(self, 'progress_label') and self.progress_label.winfo_exists():
            self.progress_label.configure(font=('Arial', base_font_size), wraplength=wrap_length)
        if hasattr(self, 'stats_text_label') and self.stats_text_label.winfo_exists():
            self.stats_text_label.configure(font=('Arial', base_font_size), wraplength=wrap_length)

    def on_resize(self, event):
        """Atualiza tamanhos ao redimensionar a janela."""
        self.update_sizes()

    # Telas da aplicação
    def show_initial_screen(self):
        """Tela inicial com opções principais."""
        self.clear_frame()
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ttk.Label(self.main_frame, text="Bem-vindo à Aventura de Quiz!",
                                   anchor='center')
        self.title_label.grid(row=0, column=0, pady=20, sticky=(tk.W, tk.E))

        btn_frame = ttk.Frame(self.main_frame, padding="20")
        btn_frame.grid(row=1, column=0, sticky=(tk.N, tk.S))
        
        btn_width = 20
        ttk.Button(btn_frame, text="🎮 Jogar Quiz", command=self.show_difficulty_selection,
                  width=btn_width).grid(row=0, column=0, pady=10)
        ttk.Button(btn_frame, text="📖 Ler Materiais", command=self.show_pdf_list,
                  width=btn_width).grid(row=1, column=0, pady=10)
        ttk.Button(btn_frame, text="📈 Ver Estatísticas", command=self.show_stats,
                  width=btn_width).grid(row=2, column=0, pady=10)
        ttk.Button(btn_frame, text="🚪 Sair", command=self.confirm_exit,
                  width=btn_width).grid(row=3, column=0, pady=10)

        self.update_sizes()
        self.showing_stats = False
        self.showing_mode = False
        self.showing_difficulty = False
        self.showing_quiz_selection = False

    def confirm_exit(self):
        """Exibe confirmação antes de sair do aplicativo."""
        if messagebox.askyesno("Confirmação", "Deseja realmente sair do aplicativo?"):
            self.root.quit()

    def show_difficulty_selection(self):
        """Exibe as opções de dificuldade na mesma janela."""
        if not self.showing_difficulty:
            self.clear_frame()
            self.main_frame = ttk.Frame(self.root, padding="20")
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.main_frame.grid_rowconfigure(0, weight=1)
            self.main_frame.grid_rowconfigure(1, weight=2)
            self.main_frame.grid_rowconfigure(2, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)

            self.title_label = ttk.Label(self.main_frame, text="Selecione o Nível de Dificuldade",
                                       anchor='center')
            self.title_label.grid(row=0, column=0, pady=20, sticky=(tk.W, tk.E))

            difficulty_frame = ttk.Frame(self.main_frame, padding="20")
            difficulty_frame.grid(row=1, column=0, sticky=(tk.N, tk.S))

            ttk.Button(difficulty_frame, text="Iniciante",
                      command=lambda: self.set_difficulty('Iniciante'),
                      width=25).grid(row=0, column=0, pady=10)
            ttk.Button(difficulty_frame, text="Estudado",
                      command=lambda: self.set_difficulty('Estudado'),
                      width=25).grid(row=1, column=0, pady=10)
            ttk.Button(difficulty_frame, text="Pronto para a Prova",
                      command=lambda: self.set_difficulty('Pronto para a Prova'),
                      width=25).grid(row=2, column=0, pady=10)

            self.back_btn = ttk.Button(self.main_frame, text="Voltar ao Menu", 
                                     command=self.show_initial_screen, width=15)
            self.back_btn.grid(row=2, column=0, pady=10)

            self.update_sizes()
            self.showing_difficulty = True
        else:
            self.show_initial_screen()
            self.showing_difficulty = False

    def set_difficulty(self, difficulty):
        """Define a dificuldade selecionada e avança para a seleção de modo."""
        self.current_difficulty = difficulty
        self.show_mode_selection()

    def show_mode_selection(self):
        """Exibe as opções de modo de jogo na mesma janela."""
        if not self.showing_mode:
            self.clear_frame()
            self.main_frame = ttk.Frame(self.root, padding="20")
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.main_frame.grid_rowconfigure(0, weight=1)
            self.main_frame.grid_rowconfigure(1, weight=2)
            self.main_frame.grid_rowconfigure(2, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)

            self.title_label = ttk.Label(self.main_frame, text="Selecione o Modo de Jogo",
                                       anchor='center')
            self.title_label.grid(row=0, column=0, pady=20, sticky=(tk.W, tk.E))

            mode_frame = ttk.Frame(self.main_frame, padding="20")
            mode_frame.grid(row=1, column=0, sticky=(tk.N, tk.S))

            ttk.Button(mode_frame, text="Resposta Aberta",
                      command=lambda: self.show_quiz_selection('open'),
                      width=25).grid(row=0, column=0, pady=10)
            ttk.Button(mode_frame, text="Múltipla Escolha",
                      command=lambda: self.show_quiz_selection('multiple'),
                      width=25).grid(row=1, column=0, pady=10)

            self.back_btn = ttk.Button(self.main_frame, text="Voltar", 
                                     command=self.show_difficulty_selection, width=15)
            self.back_btn.grid(row=2, column=0, pady=10)

            self.update_sizes()
            self.showing_mode = True
        else:
            self.show_difficulty_selection()
            self.showing_mode = False

    def show_quiz_selection(self, mode):
        """Exibe as opções de tópicos na mesma janela."""
        self.current_mode = mode
        if not self.showing_quiz_selection:
            self.clear_frame()
            self.main_frame = ttk.Frame(self.root, padding="20")
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.main_frame.grid_rowconfigure(0, weight=1)
            self.main_frame.grid_rowconfigure(1, weight=2)
            self.main_frame.grid_rowconfigure(2, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)

            self.title_label = ttk.Label(self.main_frame, text="Selecione o Tópico do Quiz",
                                       anchor='center')
            self.title_label.grid(row=0, column=0, pady=20, sticky=(tk.W, tk.E))

            quiz_frame = ttk.Frame(self.main_frame, padding="20")
            quiz_frame.grid(row=1, column=0, sticky=(tk.N, tk.S))

            # Obtém os temas disponíveis para a dificuldade selecionada
            if self.current_difficulty in self.all_questions:
                quizzes = self.all_questions[self.current_difficulty]
                for i, quiz_name in enumerate(quizzes.keys()):
                    ttk.Button(quiz_frame, text=quiz_name,
                              command=lambda name=quiz_name: self.start_selected_quiz(name),
                              width=25).grid(row=i, column=0, pady=10)
            else:
                ttk.Label(quiz_frame, text="Nenhum tópico disponível para esta dificuldade!").grid(row=0, column=0, pady=10)

            self.back_btn = ttk.Button(self.main_frame, text="Voltar", 
                                     command=self.show_mode_selection, width=15)
            self.back_btn.grid(row=2, column=0, pady=10)

            self.update_sizes()
            self.showing_quiz_selection = True
        else:
            self.show_mode_selection()
            self.showing_quiz_selection = False

    def start_selected_quiz(self, quiz_name):
        """Inicia o quiz selecionado."""
        if (self.current_difficulty in self.all_questions and 
            quiz_name in self.all_questions[self.current_difficulty]):
            quizzes = self.all_questions[self.current_difficulty][quiz_name]
            question_type = 'open' if self.current_mode == 'open' else 'multiple'
            self.questions = quizzes[question_type].copy()  # Cria uma cópia para evitar modificar o original
            random.shuffle(self.questions)  # Embaralha as perguntas
            self.total_questions = len(self.questions)
            self.start_quiz()
        else:
            messagebox.showerror("Erro", "Nenhum quiz disponível para esta dificuldade e modo!")
            self.show_quiz_selection(self.current_mode)

    def create_quiz_frame(self):
        """Tela do quiz com perguntas e respostas."""
        self.clear_frame()
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        for i in range(6):
            self.main_frame.grid_rowconfigure(i, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.welcome_label = ttk.Label(self.main_frame, text="Vamos começar o Quiz!",
                                     anchor='center')
        self.welcome_label.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))

        # Usando Label para exibir perguntas
        self.question_label = ttk.Label(self.main_frame, 
                                      background=self.colors['light_purple'], 
                                      foreground=self.colors['dark_purple'],
                                      anchor='center', text="")
        self.question_label.grid(row=1, column=0, pady=20, sticky=(tk.W, tk.E))

        # Área para respostas
        self.answer_frame = ttk.Frame(self.main_frame, padding="10")
        self.answer_frame.grid(row=2, column=0, pady=10)

        if self.current_mode == 'open':
            # Modo de Resposta Aberta
            ttk.Label(self.answer_frame, text="Sua Resposta:").grid(row=0, column=0, padx=5)
            self.answer_var = tk.StringVar()
            self.answer_entry = ttk.Entry(self.answer_frame, textvariable=self.answer_var, width=40)
            self.answer_entry.grid(row=0, column=1, padx=5)
            self.answer_entry.bind('<Return>', lambda event: self.check_answer())
        else:
            # Modo de Múltipla Escolha
            self.selected_answer.set("")  # Inicializa a variável de seleção
            for i, (option, value) in enumerate(self.questions[self.current_question]['options'].items()):
                ttk.Radiobutton(self.answer_frame, text=f"{option} {value}", 
                               value=option, variable=self.selected_answer).grid(row=i, column=0, sticky='w', pady=5)

        self.btn_frame = ttk.Frame(self.main_frame, padding="10")
        self.btn_frame.grid(row=3, column=0, pady=20)
        self.submit_btn = ttk.Button(self.btn_frame, text="Enviar Resposta", 
                                   command=self.check_answer, width=15)
        self.submit_btn.grid(row=0, column=0, padx=10)
        self.next_btn = ttk.Button(self.btn_frame, text="Próxima", 
                                 command=self.next_question, width=15)
        self.next_btn.grid(row=0, column=1, padx=10)
        self.next_btn.state(['disabled'])

        self.result_label = ttk.Label(self.main_frame, text="", anchor='center')
        self.result_label.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))

        self.progress_label = ttk.Label(self.main_frame, text="", anchor='center')
        self.progress_label.grid(row=5, column=0, pady=10, sticky=(tk.W, tk.E))

        self.update_sizes()
        # Força a atualização e chama show_question com atraso
        self.root.update_idletasks()
        if self.questions:
            self.root.after(50, self.show_question)
        else:
            messagebox.showerror("Erro", "Nenhuma pergunta carregada! Verifique o arquivo.")
            self.show_initial_screen()

    def clear_frame(self):
        """Remove todos os widgets da tela."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # Lógica do Quiz
    def start_quiz(self):
        """Inicia o quiz."""
        self.current_question = 0
        self.correct_answers = 0
        self.stats = {"correct": [], "wrong": []}
        self.create_quiz_frame()

    def show_question(self):
        """Exibe a pergunta atual na caixa de texto."""
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            self.question_label.config(text=f"Pergunta {self.current_question + 1}: {q['question']}")
            
            # Limpa e atualiza a área de respostas
            for widget in self.answer_frame.winfo_children():
                widget.destroy()

            if self.current_mode == 'open':
                ttk.Label(self.answer_frame, text="Sua Resposta:").grid(row=0, column=0, padx=5)
                self.answer_var = tk.StringVar()
                self.answer_entry = ttk.Entry(self.answer_frame, textvariable=self.answer_var, width=40)
                self.answer_entry.grid(row=0, column=1, padx=5)
                self.answer_entry.bind('<Return>', lambda event: self.check_answer())
            else:
                self.selected_answer.set("")
                for i, (option, value) in enumerate(q['options'].items()):
                    ttk.Radiobutton(self.answer_frame, text=f"{option} {value}", 
                                   value=option, variable=self.selected_answer).grid(row=i, column=0, sticky='w', pady=5)

            self.result_label.config(text="")
            self.progress_label.config(text=f"Progresso: {self.current_question + 1}/{self.total_questions}")
            if self.current_mode == 'open':
                self.answer_entry.focus()
            self.next_btn.state(['disabled'])
            self.root.update_idletasks()
        else:
            self.save_attempt()
            self.show_final_results()

    def check_answer(self):
        """Verifica a resposta do usuário."""
        if self.current_question < len(self.questions):
            if self.current_mode == 'open':
                user_answer = self.answer_var.get().strip().lower()
                correct_answer = self.questions[self.current_question]['answer'].lower()
            else:
                user_answer = self.selected_answer.get()
                correct_answer = self.questions[self.current_question]['answer']

            if user_answer == correct_answer:
                self.correct_answers += 1
                self.result_label.config(text="Parabéns! Acertou! 🌟", 
                                      foreground=self.colors['dark_green'])
                self.stats["correct"].append(self.current_question)
                self.root.after(1000, self.next_question)  # Avança automaticamente após acerto
            else:
                correct_text = (f"Ops! Era: {self.questions[self.current_question]['answer']}" if self.current_mode == 'open'
                              else f"Ops! Era: {self.questions[self.current_question]['answer']}")
                self.result_label.config(text=correct_text, 
                                      foreground=self.colors['dark_purple'])
                self.stats["wrong"].append(self.current_question)
                self.next_btn.state(['!disabled'])  # Habilita "Próxima" manualmente após erro

    def next_question(self):
        """Vai para a próxima pergunta."""
        if self.current_question < len(self.questions):
            self.current_question += 1
            self.show_question()

    def show_final_results(self):
        """Mostra os resultados finais com botão 'Voltar ao Menu'."""
        percentage = (self.correct_answers / self.total_questions) * 100
        result_text = f"Quiz concluído!\nPontuação: {self.correct_answers}/{self.total_questions} ({percentage:.1f}%)"
        self.question_label.config(text=result_text)
        self.welcome_label.config(text="Obrigado por jogar!")
        self.answer_frame.grid_remove()
        self.btn_frame.grid_remove()
        self.result_label.config(text="")
        self.progress_label.config(text="")

        self.back_btn = ttk.Button(self.main_frame, text="Voltar ao Menu", 
                                 command=self.show_initial_screen, width=15)
        self.back_btn.grid(row=5, column=0, pady=10)

    # Estatísticas e Armazenamento
    def save_attempt(self):
        """Salva a tentativa atual em um único arquivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        percentage = (self.correct_answers / self.total_questions) * 100
        self.attempts.append((timestamp, percentage))
        
        with open("quiz_attempts.txt", "a") as f:
            f.write(f"Data: {timestamp}\n")
            f.write(f"Pontuação: {self.correct_answers}/{self.total_questions}\n")
            f.write(f"Porcentagem: {percentage:.1f}%\n")
            f.write(f"Corretas: {len(self.stats['correct'])}\n")
            f.write(f"Erradas: {len(self.stats['wrong'])}\n")
            f.write("---\n")

    def load_previous_attempts(self):
        """Carrega tentativas anteriores de um único arquivo."""
        attempts = []
        if os.path.exists("quiz_attempts.txt"):
            try:
                with open("quiz_attempts.txt", "r") as f:
                    lines = f.read().split("---\n")
                    for attempt in lines:
                        if attempt.strip():
                            data = attempt.split("\n")
                            timestamp = data[0].split(": ")[1].strip()
                            percentage = float(data[2].split(": ")[1].strip().rstrip("%"))
                            attempts.append((timestamp, percentage))
            except Exception as e:
                messagebox.showerror("Erro!", f"Erro ao carregar tentativas: {e}")
        return sorted(attempts, key=lambda x: x[0])

    def show_stats(self):
        """Exibe estatísticas dentro da janela principal."""
        self.clear_frame()
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ttk.Label(self.main_frame, text="Suas Estatísticas 📊",
                                   anchor='center')
        self.title_label.grid(row=0, column=0, pady=20, sticky=(tk.W, tk.E))

        frame = ttk.Frame(self.main_frame, padding="10")
        frame.grid(row=1, column=0, sticky=(tk.N, tk.S))

        num_attempts = len(self.attempts)
        avg_score = sum(score for _, score in self.attempts) / num_attempts if num_attempts > 0 else 0
        stats_text = f"📊 Suas Estatísticas 📊\n\n"
        stats_text += f"Tentativas: {num_attempts}\n"
        stats_text += f"Pontuação Média: {avg_score:.1f}%\n"
        if self.total_questions > 0:
            current_percentage = (self.correct_answers / self.total_questions) * 100
            stats_text += f"Última Pontuação: {self.correct_answers}/{self.total_questions} ({current_percentage:.1f}%)"
        
        self.stats_text_label = ttk.Label(frame, text=stats_text, justify="center")
        self.stats_text_label.grid(row=0, column=0, pady=10)

        if self.attempts:
            fig, ax = plt.subplots(figsize=(5, 3))
            dates, scores = zip(*self.attempts)
            ax.plot(range(len(scores)), scores, 'o-', color=self.colors['dark_purple'], 
                   linewidth=2, markersize=8)
            ax.set_title("Seu Progresso")
            ax.set_xlabel("Tentativa")
            ax.set_ylabel("Pontuação (%)")
            ax.set_ylim(0, 100)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=0, pady=20, sticky=(tk.W, tk.E))
        else:
            ttk.Label(frame, text="Nenhuma tentativa ainda!", justify="center").grid(row=1, column=0, pady=20)

        self.back_btn = ttk.Button(self.main_frame, text="Voltar ao Menu", 
                                 command=self.show_initial_screen, width=15)
        self.back_btn.grid(row=2, column=0, pady=10)

        self.update_sizes()
        self.showing_stats = True

    # Leitura de PDFs
    def show_pdf_list(self):
        """Lista PDFs disponíveis."""
        # Sugere uma pasta padrão (ex.: onde o script está)
        default_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_folder = filedialog.askdirectory(initialdir=default_dir, title="Escolha a pasta dos materiais")
        if not pdf_folder:
            return

        self.pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        if not self.pdf_files:
            messagebox.showinfo("Ops!", "Nenhum PDF encontrado! Certifique-se de que 'PSIGOLOGIA MEDICA.pdf' está na pasta.")
            return

        pdf_window = tk.Toplevel(self.root, bg=self.colors['light_green'])
        pdf_window.title("Materiais de Estudo")
        pdf_window.geometry("400x400")
        pdf_window.grid_rowconfigure(0, weight=1)
        pdf_window.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(pdf_window, bg=self.colors['light_green'])
        scrollbar = ttk.Scrollbar(pdf_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for pdf in self.pdf_files:
            pdf_path = os.path.join(pdf_folder, pdf)
            btn = ttk.Button(scrollable_frame, text=f"📕 {pdf}", 
                           command=lambda p=pdf_path: self.open_pdf(p), width=30)
            btn.pack(pady=5)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def open_pdf(self, pdf_path):
        """Abre um PDF no visualizador padrão."""
        try:
            if os.name == 'nt':
                os.startfile(pdf_path)
            elif os.name == 'posix':
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, pdf_path])
        except Exception as e:
            messagebox.showerror("Erro!", f"Não consegui abrir o PDF: {e}. Verifique se o arquivo existe ou se está corrompido.")

def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
