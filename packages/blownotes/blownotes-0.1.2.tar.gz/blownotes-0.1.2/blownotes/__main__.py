#!/bin/python3

import sys
import os
import librosa
import numpy as np

# Funções que implementam as duas abordagens
from blownotes.rms_mode import extrair_notas_rms
from blownotes.split_mode import extrair_notas_split

def ascii_intro():
    print(r"""
    
╔══════════════════════════════════════════════════════════════════╗    
║                                          ♬                       ║    
║            ♬   ♪                                ♪                ║    
║    .-.       ♫   .;                 .-.              .           ║    
║   (_) )-.       .;'                   ;  :       ...;...         ║    
║     .: __)     .;  .-.  `;     .-   .;:  : .-.    .'.-.     .    ║    
║  ♪ .:'   `.   ::  ;   ;';  ;   ;   .;' \ :;   ;'.;.;.-'   .';    ║    
║    :'      )_;;_.-`;;'  `.' `.'.:'.;    \:`;;'.;   `:::'.' .     ____ 
║ (_/  `----'                   (__.'      `.       ♫    '        |____|
║                      ♪                                          |    |
║               ♫                                 ♬   ♪         ( )  ( )
╚══════════════════════════════════════════════════════════════════╝    
 Blow Notes v0.1.0                                                        
 Detector de Notas Musicais                                             
 Autor: I. Zanoth
""")

def main():
    ascii_intro()

    if len(sys.argv) < 2:
        print("Uso: blownotes caminho/para/arquivo.wav")
        sys.exit(1)

    audio_path = sys.argv[1]

    if not os.path.isfile(audio_path):
        print(f"Erro: arquivo não encontrado: {audio_path}")
        sys.exit(1)

    print("\nEscolha o modo de detecção:")
    print(" [1] RMS (permite ajustar a precisão)")
    print(" [2] Regiões Ativas (librosa.effects.split)")
    modo = input("Digite 1 ou 2 e pressione Enter: ").strip()

    if modo == "1":
        sens = input("Sensibilidade (0.01 = muito sensível, 0.05 = mais rígido). Pressione Enter para 0.02: ").strip()
        try:
            sensibilidade = float(sens) if sens else 0.02
        except ValueError:
            print("Valor inválido, usando sensibilidade padrão (0.02).")
            sensibilidade = 0.02
        extrair_notas_rms(audio_path, sensibilidade)

    elif modo == "2":
        extrair_notas_split(audio_path)

    else:
        print("Opção inválida.")
        sys.exit(1)

if __name__ == "__main__":
    main()
