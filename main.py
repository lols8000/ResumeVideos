import tkinter as tk
from tkinter import ttk
import threading
import speech_recognition as sr
from bardapi import Bard
import os


class TranscricaoFalaGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Transcrição de Fala")
        self.master.geometry("950x700")

        # Frame para conter os botões
        self.frame_botoes = tk.Frame(master)
        self.frame_botoes.pack()

        self.botao_iniciar = tk.Button(self.frame_botoes, text="Iniciar Transcrição", command=self.iniciar_transcricao)
        self.botao_iniciar.pack(side="left", padx=5, pady=10)

        self.botao_parar = tk.Button(self.frame_botoes, text="Parar", command=self.parar_transcricao, state="disabled")
        self.botao_parar.pack(side="left", padx=5, pady=10)

        self.botao_gerar_resumo = tk.Button(self.frame_botoes, text="Gerar Resumo", command=self.gerar_resumo,
                                            state="disabled")
        self.botao_gerar_resumo.pack(side="left", padx=5, pady=10)

        self.opcoes_idioma = ttk.Combobox(master, values=["Inglês", "Português", "Espanhol"])
        self.opcoes_idioma.current(1)  # Define o idioma padrão como Português
        self.opcoes_idioma.pack(pady=5)

        self.label_status = tk.Label(master, text="Texto transcrito: ")
        self.label_status.pack(pady=5)

        self.texto_transcrito = tk.Text(master, wrap="word", height=15, width=100)
        self.texto_transcrito.pack(pady=10)

        self.label_resume = tk.Label(master, text="Resumo do texto: ")
        self.label_resume.pack(pady=5)

        self.texto_resumido = tk.Text(master, wrap="word", height=15, width=100)
        self.texto_resumido.pack(pady=10)

        self.thread_transcricao = None
        self.transcricao_ativa = False
        self.resumo_ativo = False

    def iniciar_transcricao(self):
        self.transcricao_ativa = True
        self.botao_iniciar.config(state="disabled")
        self.botao_parar.config(state="normal")
        self.botao_gerar_resumo.config(state="normal")
        self.opcoes_idioma.config(state="disabled")
        self.label_status.config(text="Transcrição em andamento...")

        idioma = self.obter_idioma_selecionado()

        self.thread_transcricao = threading.Thread(target=self.reconhecer_fala_thread, args=(idioma,))
        self.thread_transcricao.start()
        self.atualizar_interface()

    def parar_transcricao(self):
        self.transcricao_ativa = False
        self.botao_iniciar.config(state="normal")
        self.botao_parar.config(state="disabled")
        self.opcoes_idioma.config(state="normal")
        self.label_status.config(text="Finalizando transcrição...")

    def gerar_resumo(self):
        self.resumo_ativo = True
        self.botao_iniciar.config(state="normal")
        self.botao_parar.config(state="disabled")
        self.botao_gerar_resumo.config(state="disabled")
        self.opcoes_idioma.config(state="normal")
        self.label_status.config(text="Gerando resumo...")

        resumo_bard = self.response_bard()
        self.texto_resumido.delete(1.0, tk.END)  # Limpar o texto existente na caixa de texto
        self.texto_resumido.insert(tk.END, resumo_bard)

    def reconhecer_fala_thread(self, idioma):
        microfone = sr.Recognizer()

        with sr.Microphone() as source:
            threading.Thread(target=microfone.adjust_for_ambient_noise, args=(source,)).start()
            self.label_status.config(text="Diga alguma coisa: ")

            while self.transcricao_ativa:
                audio = microfone.listen(source, phrase_time_limit=5.6)
                threading.Thread(target=self.processar_audio, args=(microfone, audio, idioma)).start()

    def processar_audio(self, microfone, audio, idioma):
        try:
            match idioma:
                case "Inglês":
                    frase = microfone.recognize_google(audio, language='en-US')
                case "Português":
                    frase = microfone.recognize_google(audio, language='pt-BR')
                case "Espanhol":
                    frase = microfone.recognize_google(audio, language='es-ES')

            self.texto_transcrito.insert(tk.END, frase + "\n")  # Exibe a transcrição em tempo real
            self.texto_transcrito.see(tk.END)  # Rola para a parte inferior do texto

        except sr.UnknownValueError:
            self.label_status.config(text="Não entendi o que você disse!")

        except sr.RequestError as e:
            self.label_status.config(text="Erro no serviço de reconhecimento de fala; {0}".format(e))

    def response_bard(self):
        texto_completo = self.texto_transcrito.get("1.0", "end-1c")
        os.environ[
            '_BARD_API_KEY'] = "g.a000gAiuqBZedmtBpVzoUolrfrKZpMvzKpxTbXeuxU0mmRPt61PKl5VLp9eoPVHshMC8gESASAACgYKAZESAQASFQHGX2MiIbJQq3tM-NiOOSXAxL_pHRoVAUF8yKom8dznQMdnaQv96R1h9vCQ0076"
        texto_dividido = [texto_completo[i:i + 2048] for i in range(0, len(texto_completo), 2048)]

        bard_output = ""

        for parte_texto in texto_dividido:
            parte_output = Bard().get_answer(f"Gere um resumo detalhado do texto a seguir: {parte_texto}")['content']
            bard_output += parte_output + "\n"

        return bard_output

    def atualizar_interface(self):
        if self.transcricao_ativa:
            self.texto_transcrito.after(1, self.atualizar_interface)  # Agendar próxima atualização
            self.master.update()  # Atualizar a interface

    def obter_idioma_selecionado(self):
        return self.opcoes_idioma.get()


def iniciar_aplicacao():
    root = tk.Tk()
    app = TranscricaoFalaGUI(root)
    root.mainloop()


def main():
    threading.Thread(target=iniciar_aplicacao).start()


if __name__ == "__main__":
    main()
