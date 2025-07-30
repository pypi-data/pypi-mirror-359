# 🎵 Blow Notes

**Blow Notes** é uma ferramenta de linha de comando para detectar notas musicais dominantes a partir de um arquivo de áudio (ex: `.wav`, `.mp3`, `.ogg`), útil para análises melódicas, transcrição ou composição.

## ✨ Funcionalidades

- Escolha entre dois métodos de extração:
  - 📈 **RMS (energia por frame)** – com controle de sensibilidade
  - 🎚️ **Split (regiões sonoras ativas)** – baseado no volume total
- Detecta notas dominantes por segundo
- Exporta resultados para `.txt`
- Suporte a `.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg` (requer `ffmpeg`)
- Compatível com futura exportação para MusicXML

## 🚀 Instalação

```bash
pip install blownotes

```

Ou clone e instale localmente:

```bash
git clone https://github.com/izanoth/blownotes
cd blownotes
pip install .
```

## 🎛️ Uso

```bash
blownotes caminho/do/arquivo.wav
```

Será exibido um menu para escolher o modo de análise.

### Parâmetros (modo RMS)

Você poderá definir uma sensibilidade:

    0.01 → muito sensível (capta até ruídos leves)

    0.02 → padrão (voz clara ou instrumento solo)

    0.04+ → mais exigente (apenas sons fortes)

## 🎧 Recomendação importante

Para melhores resultados, separe os elementos do áudio antes da análise (ex: voz, bateria, baixo). Isso evita que sons simultâneos confundam o sistema de detecção.

🔧 Uma ferramenta recomendada é o [Demucs](https://github.com/facebookresearch/demucs):

Depois, use o blownotes apenas no arquivo de voz ou instrumento que desejar.

## 📄 Licença

MIT

Autor: I. Zanoth
ivanzanoth@gmail.com
