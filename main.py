from motor import Motor

print("=== Sistema Especialista - Diagnóstico Infantil (Backward Chaining) ===\n")

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
