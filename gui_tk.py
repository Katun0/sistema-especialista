# - A INTERFACE SÓ RODA NO POWERSHELL SE ESTIVER USANDO VSCODE 
import os
import threading
import queue
import json
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

try:
    from embeddings.embedder import Embedder
    from semantic.search import SemanticSearch
    from inference.fact_extractor import FactExtractor
    from inference.rule_engine import RuleEngine
    from inference.inference import InferenceEngine
except ImportError as e:
    Embedder = None
    SemanticSearch = None
    FactExtractor = None
    RuleEngine = None
    InferenceEngine = None
    IMPORT_ERROR = traceback.format_exc()
else:
    IMPORT_ERROR = None

class ExpertSystemApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Especialista (JSON)")
        self.geometry("800x600")
        self.minsize(900, 600)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.kb_path = os.path.join(self.base_dir, "data", "knowledge.json")
        self.engine = None
        self.result_queue = queue.Queue()

        self._build_controls_frame()
        self._build_io_frame()
        self._build_output_frame()
        self._build_statusbar()

        if IMPORT_ERROR:
            self.append_log("ERRO AO IMPORTAR MÓDULOS DO PROJETO:\n" + IMPORT_ERROR)
        else:
            self.append_log("Inicializando sistema especialista...")
            threading.Thread(target=self._init_engine, daemon=True).start()
        self.after(200, self._poll_queue)

    def _build_controls_frame(self):
        frm = ttk.Frame(self)
        frm.pack(side="top", fill="x", padx=8, pady=6)

        ttk.Label(frm, text="Knowledge (KB):").pack(side="left")
        self.kb_label = ttk.Label(frm, text=os.path.basename(self.kb_path))
        self.kb_label.pack(side="left", padx=(6, 12))
        ttk.Button(frm, text="Escolher KB...", command=self._choose_kb).pack(side="left")

        ttk.Label(frm, text="Top K evidências:").pack(side="left", padx=(12, 6))
        self.topk_var = tk.IntVar(value=4)
        ttk.Spinbox(frm, from_=1, to=10, width=4, textvariable=self.topk_var).pack(side="left")

        ttk.Button(frm, text="Inferir", command=self._on_infer_click).pack(side="right")
        ttk.Button(frm, text="Salvar log...", command=self._save_log).pack(side="right", padx=(6, 0))

    def _build_io_frame(self):
        frm = ttk.Frame(self)
        frm.pack(side="top", fill="both", expand=False, padx=8, pady=(0,6))

        left = ttk.Frame(frm)
        left.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Descrição / Sintomas:").pack(anchor="w")
        self.input_text = ScrolledText(left, height=8)
        self.input_text.pack(fill="both", expand=True)

        # botões rápidos de exemplo
        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=4)
        ttk.Button(btns, text="Exemplo: febre + choro intenso", command=lambda: self._set_example("O bebê está com febre alta e choro intenso desde a noite.")).pack(side="left")
        ttk.Button(btns, text="Limpar", command=lambda: self.input_text.delete("1.0", "end")).pack(side="left", padx=(6,0))

        right = ttk.Frame(frm, width=320)
        right.pack(side="right", fill="y", padx=(8,0))
        ttk.Label(right, text="Logs / Mensagens:").pack(anchor="w")
        self.log_text = ScrolledText(right, height=10, state="normal")
        self.log_text.pack(fill="both", expand=True)
    
    def _build_output_frame(self):
        frm = ttk.Frame(self)
        frm.pack(side="top", fill="both", expand=True, padx=8, pady=(0,8))

        # facts
        facts_frame = ttk.Labelframe(frm, text="Fatos extraídos")
        facts_frame.pack(side="left", fill="both", expand=True, padx=(0,8))
        self.facts_text = ScrolledText(facts_frame, state="normal")
        self.facts_text.pack(fill="both", expand=True)

        # evidence + conclusions
        right = ttk.Frame(frm)
        right.pack(side="right", fill="both", expand=True)

        evid_frame = ttk.Labelframe(right, text="Evidência (top K)")
        evid_frame.pack(fill="both", expand=True, pady=(0,8))
        self.evid_tree = ttk.Treeview(evid_frame, columns=("score", "title"), show="headings", selectmode="browse", height=6)
        self.evid_tree.heading("score", text="Score")
        self.evid_tree.heading("title", text="Título / ID")
        self.evid_tree.column("score", width=80, anchor="center")
        self.evid_tree.column("title", width=300, anchor="w")
        self.evid_tree.pack(fill="both", expand=True)

        concl_frame = ttk.Labelframe(right, text="Conclusões")
        concl_frame.pack(fill="both", expand=True)
        self.concl_tree = ttk.Treeview(concl_frame, columns=("combined","overlap","title"), show="headings", selectmode="browse", height=6)
        self.concl_tree.heading("combined", text="Combined")
        self.concl_tree.heading("overlap", text="Overlap")
        self.concl_tree.heading("title", text="Diagnóstico / Título")
        self.concl_tree.column("combined", width=90, anchor="center")
        self.concl_tree.column("overlap", width=90, anchor="center")
        self.concl_tree.column("title", width=300, anchor="w")
        self.concl_tree.pack(fill="both", expand=True)
        self.concl_tree.bind("<<TreeviewSelect>>", self._on_conclusion_select)

        # detalhe da conclusão selecionada
        detail_frame = ttk.Labelframe(right, text="Detalhes da conclusão")
        detail_frame.pack(fill="both", expand=True, pady=(8,0))
        self.detail_text = ScrolledText(detail_frame, height=8)
        self.detail_text.pack(fill="both", expand=True)
    def _build_statusbar(self):
        frm = ttk.Frame(self)
        frm.pack(side="bottom", fill="x")
        self.status_var = tk.StringVar(value="Pronto.")
        self.status_label = ttk.Label(frm, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_label.pack(fill="x")

    def append_log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def _set_example(self, text):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)

    def _choose_kb(self):
        path = filedialog.askopenfilename(title="Escolher knowledge.json", filetypes=[("JSON files","*.json"),("All files","*.*")])
        if path:
            self.kb_path = path
            self.kb_label.config(text=os.path.basename(self.kb_path))
            self.append_log(f"KB alterada para: {self.kb_path}")
            # reinit engine com o novo KB
            if IMPORT_ERROR:
                messagebox.showwarning("Aviso", "Não foi possível reinicializar engine porque houve erro na importação dos módulos do projeto.")
                return
            self.append_log("Reinicializando engine com nova KB...")
            threading.Thread(target=self._init_engine, daemon=True).start()

    def _init_engine(self):
        try:
            self.status_var.set("Carregando sistema especialista...")
            embedder = Embedder()
            docs = embedder.load_kb(self.kb_path)
            embeddings = embedder.encode_documents(docs)
            sem = SemanticSearch(embeddings, docs)
            extractor = FactExtractor()
            rules = RuleEngine()
            self.engine = InferenceEngine(embedder, sem, extractor, rules)
            self.append_log("Sistema especialista carregado com sucesso.")
            self.status_var.set("Sistema pronto.")
        except Exception as e:
            self.append_log("Erro ao inicializar engine:\n" + traceback.format_exc())
            self.status_var.set("Erro na inicialização. Verifique logs.")
            self.engine = None

    def _on_infer_click(self):
        query = self.input_text.get("1.0", "end").strip()
        if not query:
            messagebox.showinfo("Input necessário", "Digite a descrição / sintomas antes de inferir.")
            return
        if self.engine is None:
            messagebox.showwarning("Engine não pronta", "O sistema especialista ainda não foi carregado ou houve erro.")
            return
        top_k = int(self.topk_var.get())
        self._clear_outputs()
        self.status_var.set("Executando inferência...")
        self.append_log("Executando inferência para: " + (query if len(query) < 200 else query[:200] + "..."))
        # executar a inferência em thread daí
        threading.Thread(target=self._run_infer_thread, args=(query, top_k), daemon=True).start()

    def _run_infer_thread(self, query, top_k):
        try:
            out = self.engine.infer(query, top_k=top_k)
            
            self.result_queue.put(("result", out))
        except Exception:
            self.result_queue.put(("error", traceback.format_exc()))

    def _poll_queue(self):
        try:
            while True:
                item = self.result_queue.get_nowait()
                typ, payload = item
                if typ == "result":
                    self._display_result(payload)
                elif typ == "error":
                    self.append_log("Erro durante inferência:\n" + payload)
                    self.status_var.set("Erro durante inferência (ver logs).")
        except queue.Empty:
            pass
        finally:
            self.after(200, self._poll_queue)

    def _clear_outputs(self):
        self.facts_text.delete("1.0", "end")
        for i in self.evid_tree.get_children():
            self.evid_tree.delete(i)
        for i in self.concl_tree.get_children():
            self.concl_tree.delete(i)
        self.detail_text.delete("1.0", "end")

    def _display_result(self, out):
        # fatos
        facts = out.get("facts", {})
        self.facts_text.insert("1.0", json.dumps(facts, indent=2, ensure_ascii=False))

        # lista de doc e score
        for ev in out.get("evidence", []):
            doc = ev.get("doc", {})
            title = f"{doc.get('id','?')} - {doc.get('title', '')}"
            score = f"{ev.get('score',0):.3f}"
            self.evid_tree.insert("", "end", values=(score, title), tags=(json.dumps(doc, ensure_ascii=False),))

        # conclusions
        for c in out.get("conclusions", []):
            combined = f"{c.get('combined_score',0):.3f}"
            overlap = f"{c.get('symptom_overlap',0):.2f}"
            title = f"{c.get('diagnostico')} - {c.get('titulo')}"
            iid = self.concl_tree.insert("", "end", values=(combined, overlap, title))
            # armazenar full payload no item (usamos uma dict em memória)
            self.concl_tree.set(iid, "_payload", json.dumps(c, ensure_ascii=False))

        self.append_log("Inferência concluída.")
        self.status_var.set("Inferência finalizada. Veja resultados.")

    def _on_conclusion_select(self, evt):
        sel = self.concl_tree.selection()
        if not sel:
            return
        iid = sel[0]
        # recupera dados da linha 
        vals = self.concl_tree.item(iid, "values")
        
        title = vals[2] if len(vals) >= 3 else ""
        
        detail = f"Título selecionado: {title}\nCombined: {vals[0]}\nOverlap: {vals[1]}\n\n"
        
        found = None
        for item in self.concl_tree.get_children():
            if item == iid:
                
                found = True
                break
        
        detail += "Detalhes adicionais (se disponíveis) aparecerão aqui, incluindo descrição completa e tratamento.\n\n"
        detail += "OBS: Se desejar ver o texto completo do documento ou tratamento, selecione um item em 'Evidência' e copie manualmente o conteúdo.\n"
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", detail)

    def _save_log(self):
        path = filedialog.asksaveasfilename(title="Salvar log", defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", "end"))
            messagebox.showinfo("Salvo", f"Log salvo em {path}")
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))

def main():
    app = ExpertSystemApp()
    app.mainloop()

if __name__ == "__main__":
    main()
