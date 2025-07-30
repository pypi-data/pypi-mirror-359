import librosa
import numpy as np

def extrair_notas_split(audio_path):
    print(f"\n[1/4] Carregando áudio: {audio_path}")
    y, sr = librosa.load(audio_path)
    hop_length = 256

    print("[2/4] Detectando regiões com som (librosa.effects.split)...")
    intervals = librosa.effects.split(y, top_db=30)
    print(f"🔍 {len(intervals)} regiões sonoras detectadas.")

    resultados = []
    segundos_registrados = set()
    frames_por_segundo = sr / hop_length

    print("[3/4] Extraindo notas dominantes por segundo...")
    for start, end in intervals:
        y_segment = y[start:end]
        pitches, magnitudes = librosa.piptrack(y=y_segment, sr=sr, hop_length=hop_length)
        total_frames = pitches.shape[1]

        for t in range(total_frames):
            tempo_global = (start / sr) + (t / frames_por_segundo)
            tempo_segundo = int(tempo_global)

            if tempo_segundo in segundos_registrados:
                continue

            idx = magnitudes[:, t].argmax()
            pitch = pitches[idx, t]

            if pitch > 0:
                note_name = librosa.hz_to_note(pitch)
                linha = f"{tempo_segundo}s  →  {note_name:4}  ({pitch:.2f} Hz)"
                print(linha)
                resultados.append(linha)
                segundos_registrados.add(tempo_segundo)

    output_file = "notas_split.txt"
    with open(output_file, "w") as f:
        for linha in resultados:
            f.write(linha + "\n")

    print(f"\n✅ Resultado salvo em: {output_file}")
