import librosa
import numpy as np

def extrair_notas_rms(audio_path, limiar_rms=0.02):
    print(f"\n[1/4] Carregando áudio: {audio_path}")
    y, sr = librosa.load(audio_path)
    hop_length = 256

    print(f"[2/4] Calculando RMS (limiar: {limiar_rms}) e pitch tracking...")
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

    total_frames = pitches.shape[1]
    frames_por_segundo = sr / hop_length

    print("[3/4] Extraindo notas por segundo com energia suficiente...")
    resultados = []
    notas_por_segundo = {}

    for t in range(total_frames):
        if rms[t] < limiar_rms:
            continue

        tempo_segundo = int(t / frames_por_segundo)
        idx = magnitudes[:, t].argmax()
        pitch = pitches[idx, t]

        if pitch > 0:
            note_name = librosa.hz_to_note(pitch)
            if tempo_segundo not in notas_por_segundo:
                notas_por_segundo[tempo_segundo] = []
            if note_name not in notas_por_segundo[tempo_segundo]:
                notas_por_segundo[tempo_segundo].append(note_name)
                linha = f"{tempo_segundo}s  →  {note_name:4}  ({pitch:.2f} Hz)"
                print(linha)
                resultados.append(linha)

    output_file = "notas_rms.txt"
    with open(output_file, "w") as f:
        for linha in resultados:
            f.write(linha + "\n")

    print(f"\n✅ Resultado salvo em: {output_file}")
