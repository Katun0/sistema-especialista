import tkinter as tk
from tkinter import scrolledtext
from motor import Motor

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Especialista - Chat de Diagnóstico Infantil")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

        # Área de conversa (somente leitura)
        self.chat_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Segoe UI", 10),
            bg="#ffffff",
            relief="flat",
            borderwidth=8
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        # Criação das tags de estilo
        self.chat_area.tag_configure("user", foreground="#004aad", spacing1=5, spacing3=5)
        self.chat_area.tag_configure("system", foreground="#333333", background="#eaeaea", spacing1=5, spacing3=5, font=("Consolas", 10))
        self.chat_area.tag_configure("diagnosis", foreground="#007f00", font=("Segoe UI", 10, "bold"), spacing1=5, spacing3=5)

        # Área inferior com entrada e botão
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.entry = tk.Entry(bottom_frame, font=("Segoe UI", 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda event: self.on_send())

        send_btn = tk.Button(bottom_frame, text="Enviar", command=self.on_send, bg="#004aad", fg="white", relief="flat", padx=15, pady=3)
        send_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Inicializa o motor
        try:
            self.motor = Motor("dados.json")
            self.spacy_ok = self.motor.nlp is not None
        except Exception as e:
            self.motor = None
            self.spacy_ok = False
            self._append_system(
                "Erro ao carregar o motor do sistema. Verifique o arquivo dados.json.\n" + str(e)
            )

        # Mensagem inicial
        self._append_system(
            "Olá! Sou o sistema especialista. Descreva o que o bebê está apresentando e direi os possíveis diagnósticos."
        )
        if not self.spacy_ok:
            self._append_system(
                "⚠️ Aviso: processamento semântico (spaCy) indisponível no momento. A análise será apenas por correspondência exata."
            )

    def _append(self, speaker, message, tag=None):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{speaker}: ", tag)
        self.chat_area.insert(tk.END, f"{message}\n\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area.configure(state=tk.DISABLED)

    def _append_user(self, message):
        self._append("Você", message, "user")

    def _append_system(self, message):
        self._append("Sistema", message, "system")

    def _append_diagnosis(self, message):
        self._append("Diagnóstico", message, "diagnosis")

    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._append_user(text)

        if self.motor is None:
            self._append_system("O motor não pôde ser carregado. Não consigo processar sua mensagem.")
            return

        sintomas_detectados = self.motor.extrair_sintoma(text)
        if not sintomas_detectados:
            self._append_system("Não reconheci sintomas na mensagem. Tente descrever com outras palavras.")
            return

        sintomas_fmt = ", ".join(sorted(s.replace("_", " ") for s in sintomas_detectados))
        self._append_system(f"Sintomas reconhecidos: {sintomas_fmt}")

        hipoteses = self.motor.backward(sintomas_detectados)
        if not hipoteses:
            self._append_system("Nenhum diagnóstico compatível encontrado até o momento.")
            return

        top = hipoteses[:3]
        linhas = []
        for diag, score in top:
            linhas.append(f"- {diag.capitalize()} ({score * 100:.0f}% de correspondência)")
        resposta = "Possíveis diagnósticos:\n" + "\n".join(linhas)
        self._append_diagnosis(resposta)

        self._append_diagnosis(f"✅ Diagnóstico mais provável: {top[0][0].capitalize()}")

def main():
    root = tk.Tk()
    ChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
