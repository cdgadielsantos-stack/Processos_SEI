#!/usr/bin/env python3
"""
ANEEL Monitor - MVP
Main entry point.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
from datetime import datetime
from pathlib import Path
import sys

# Add app to path
sys.path.append(str(Path(__file__).parent))

from app.browser.browser import ANEELBrowser
from app.scraper.scraper import ProcessScraper
from app.database.db import init_db, get_session
from app.models.models import Processo
from app.utils.utils import setup_logger
from config import DATABASE_URL, LOG_LEVEL, DOWNLOAD_DIR, DATA_DIR, LOGS_DIR, EXPORTS_DIR

# Setup logger
logger = setup_logger(__name__, LOG_LEVEL, LOGS_DIR / "app.log")

class ANEELMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ANEEL Monitor - MVP")
        self.root.geometry("800x600")

        # Queue for thread-safe logging
        self.log_queue = queue.Queue()

        # Browser and scraper instances (will be created on start)
        self.browser = None
        self.scraper = None
        self.is_running = False

        # Build UI
        self._build_ui()

        # Start log consumer
        self._consume_log_queue()

        # Initialize database
        init_db(DATABASE_URL)
        self.log("Database initialized.")

    def _build_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Date inputs
        date_frame = ttk.LabelFrame(main_frame, text="Período de Pesquisa", padding="10")
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="Data inicial (DD/MM/AAAA):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.date_inicial = ttk.Entry(date_frame, width=12)
        self.date_inicial.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.date_inicial.insert(0, (datetime.now()).strftime("%d/%m/%Y"))  # default today

        ttk.Label(date_frame, text="Data final (DD/MM/AAAA):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.date_final = ttk.Entry(date_frame, width=12)
        self.date_final.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.date_final.insert(0, (datetime.now()).strftime("%d/%m/%Y"))  # default today

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(button_frame, text="Iniciar Monitoramento", command=self._start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Parar", command=self._stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(button_frame, text="Exportar CSV", command=self._export_csv)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED)

    def log(self, message):
        """Thread-safe logging to UI."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}\n")

    def _consume_log_queue(self):
        """Consume log queue and update UI."""
        try:
            while True:
                line = self.log_queue.get_nowait()
                self.log_area.config(state=tk.NORMAL)
                self.log_area.insert(tk.END, line)
                self.log_area.see(tk.END)
                self.log_area.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.root.after(100, self._consume_log_queue)

    def _start_monitoring(self):
        """Start the monitoring process in a separate thread."""
        if self.is_running:
            return

        # Validate dates
        try:
            data_inicial = datetime.strptime(self.date_inicial.get(), "%d/%m/%Y")
            data_final = datetime.strptime(self.date_final.get(), "%d/%m/%Y")
            if data_inicial > data_final:
                messagebox.showerror("Erro", "Data inicial não pode ser maior que data final.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log("Iniciando monitoramento...")

        # Start worker thread
        self.worker_thread = threading.Thread(
            target=self._monitoring_worker,
            args=(data_inicial, data_final),
            daemon=True
        )
        self.worker_thread.start()

    def _stop_monitoring(self):
        """Request stop of monitoring."""
        self.is_running = False
        self.log("Solicitando parada...")
        self.stop_btn.config(state=tk.DISABLED)
        # Note: actual stop will be checked in worker loop

    def _monitoring_worker(self, data_inicial, data_final):
        """Worker thread that performs the monitoring tasks."""
        try:
            # Initialize browser
            self.log("Inicializando navegador...")
            self.browser = ANEELBrowser(headless=False)  # visible for CAPTCHA
            self.browser.launch()

            # Navigate to SEI search page
            sei_url = ("https://sei.aneel.gov.br/sei/modulos/pesquisa/md_pesq_processo_pesquisar.php"
                       "?acao_externa=protocolo_pesquisar&acao_origem_externa=protocolo_pesquisar"
                       "&id_orgao_acesso_externo=0")
            self.log(f"Navegando para: {sei_url}")
            self.browser.navigate_to(sei_url)

            # Fill date fields primeiro
            self.log(f"Preenchendo campos de data: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")
            self.browser.fill_date_fields(
                data_inicial.strftime("%d/%m/%Y"),
                data_final.strftime("%d/%m/%Y")
            )

            # Agora o usuário resolve o CAPTCHA e clica em Pesquisar
            self.log("Resolva o CAPTCHA, clique em Pesquisar e depois pressione ENTER no terminal.")
            self.browser.wait_for_human_captcha()
            self.log("Pesquisa concluída. Continuando...")


            # Scrape process links
            self.log("Coletando links de processos...")
            links = self.browser.collect_process_links()
            self.log(f"Encontrados {len(links)} processos.")

            # Initialize scraper and DB session
            self.scraper = ProcessScraper()
            session = get_session(DATABASE_URL)

            # Process each link
            for i, link in enumerate(links, start=1):
                if not self.is_running:
                    self.log("Monitoramento parado pelo usuário.")
                    break

                self.log(f"Processando {i}/{len(links)}: {link}")
                try:
                    # Scrape process details from link (opens in same tab or new?)
                    processo_data = self.scraper.scrape_process_from_link(self.browser.page, link)
                    if processo_data:
                        # Save to DB
                        processo = Processo(
                            numero_processo=processo_data.get('numero', ''),
                            data_processo=processo_data.get('data'),
                            assunto=processo_data.get('assunto', ''),
                            tipo_processo=processo_data.get('tipo', ''),
                            url=link,
                            data_coleta=datetime.now()
                        )
                        session.add(processo)
                        session.commit()
                        self.log(f"  Salvo: {processo_data.get('numero', 'N/A')} - {processo_data.get('assunto', '')[:50]}")
                    else:
                        self.log("  Não foi possível extrair dados do processo.")
                except Exception as e:
                    self.log(f"  Erro ao processar {link}: {e}")
                    session.rollback()

                # Small delay to be gentle
                self.browser.page.wait_for_timeout(500)

            session.close()
            self.log("Monitoramento concluído.")

        except Exception as e:
            self.log(f"Erro durante o monitoramento: {e}")
            logger.exception("Erro no worker")
        finally:
            # Cleanup
            if self.browser:
                self.browser.close()
                self.browser = None
            self.is_running = False
            # Update UI buttons (must be done in main thread)
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))

    def _export_csv(self):
        """Export processes to CSV."""
        try:
            import pandas as pd
            from app.database.db import get_session
            from app.models.models import Processo

            session = get_session(DATABASE_URL)
            processos = session.query(Processo).all()
            session.close()

            if not processos:
                messagebox.showinfo("Exportar CSV", "Nenhum processo encontrado para exportar.")
                return

            data = [{
                'ID': p.id,
                'Número do Processo': p.numero_processo,
                'Data': p.data_processo.strftime('%Y-%m-%d') if p.data_processo else '',
                'Assunto': p.assunto,
                'Tipo': p.tipo_processo,
                'URL': p.url,
                'Data de Coleta': p.data_coleta.strftime('%Y-%m-%d %H:%M:%S')
            } for p in processos]

            df = pd.DataFrame(data)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialdir=EXPORTS_DIR,
                title="Salvar CSV como"
            )
            if file_path:
                df.to_csv(file_path, index=False)
                self.log(f"Exportado {len(processos)} processos para {file_path}")
                messagebox.showinfo("Exportar CSV", f"Exportado com sucesso!\n{file_path}")
        except Exception as e:
            self.log(f"Erro ao exportar CSV: {e}")
            messagebox.showerror("Exportar CSV", f"Erro: {e}")

def main():
    root = tk.Tk()
    app = ANEELMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()