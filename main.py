import sys
from motor import Motor

titulo = "=== Sistema Especialista - Diagnóstico Infantil (Backward Chaining) ===\n"

def run_cli():
    print(titulo)
    # Inicializa motor com caminho do JSON
    motor = Motor("dados.json")

    texto_usuario = input("Descreva o que o bebê está apresentando:\n> ")

    # Extrai sintomas mencionados
    sintomas_detectados = motor.extrair_sintoma(texto_usuario)

    if not sintomas_detectados:
        print("\nNenhum sintoma reconhecido no texto.")
    else:
        print("\nSintomas reconhecidos:")
        for s in sintomas_detectados:
            print(f" - {s.replace('_', ' ')}")

        print("\nAnalisando possíveis diagnósticos...\n")
        hipoteses = motor.backward(sintomas_detectados)

        if not hipoteses:
            print("Nenhum diagnóstico compatível encontrado.")
        else:
            for diag, score in hipoteses:
                print(f"{diag.capitalize()} ({score * 100:.0f}% de correspondência)")

            print(f"\n>>> Diagnóstico mais provável: {hipoteses[0][0].capitalize()}")

def run_gui():
    try:
        from gui import main as gui_main
        gui_main()
    except Exception as e:
        print(titulo)
        print("Não foi possível iniciar a interface gráfica. Iniciando modo de linha de comando.")
        print(f"Motivo: {e}")
        run_cli()

if __name__ == "__main__":
    # Se for passado --cli ou -c, força o modo CLI. Caso contrário, abre a GUI por padrão.
    if any(arg in ("--cli", "-c") for arg in sys.argv[1:]):
        run_cli()
    else:
        run_gui()
