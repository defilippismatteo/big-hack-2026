import base64
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import urllib.error
import wave

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / 'audio'
AUDIO.mkdir(exist_ok=True)
VOICE = 'W71zT1VwIFFx3mMGH2uZ'
MODEL = 'eleven_v4'


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(path)]))


def main():
    key = Path(sys.argv[1]).read_text().strip()
    cues = json.loads((ROOT / 'copione-cues.json').read_text())['segments']
    segments = []
    for index, cue in enumerate(cues):
        if index == 3:
            parts = [(27.25, 33.55, 'Qui seguiamo una previsione del costo per mille impressioni, dal sedici al trenta novembre.'), (33.55, 36.70, 'La linea si disegna giorno dopo giorno,'), (36.70, 38.95, 'poi la vista si allarga:'), (38.95, 43.50, "così possiamo leggere l'intero andamento, senza aggiungere picchi artificiali.")]
        elif index == 4:
            parts = [(44.05, 46.10, 'Le date chiave danno contesto.'), (46.10, 48.40, 'Timestral prevede i costi pubblicitari;'), (48.40, 52.85, 'CatBoost entra nel confronto dei modelli sui dati di validazione.')]
        elif index == 9:
            parts = [(104.05, 111.90, cue['text'])]
        else:
            parts = [(cue['speechStartTarget'], cue['speechEndTarget'], cue['text'])]
        for start, end, text in parts:
            segments.append({'scene': index + 1, 'start': start, 'end': end, 'text': text})
    records = []
    for index, segment in enumerate(segments):
        stem = AUDIO / f'segment-{index + 1:02}'
        audio_path = stem.with_suffix('.mp3')
        alignment_path = stem.with_suffix('.alignment.json')
        if not audio_path.exists() or not alignment_path.exists():
            payload = {'text': segment['text'], 'model_id': MODEL, 'language_code': 'it', 'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75, 'speed': 1.08 if segment['scene'] == 10 else 0.95}}
            request = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(payload).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    result = json.load(response)
            except urllib.error.HTTPError as error:
                detail = json.loads(error.read()).get('detail', {})
                raise RuntimeError(f'ElevenLabs HTTP {error.code}: {detail}') from None
            alignment = result.get('normalized_alignment') or result.get('alignment')
            if not alignment:
                raise RuntimeError('Timestamp assenti: impossibile verificare sincronizzazione')
            alignment_path.write_text(json.dumps(alignment, ensure_ascii=False, indent=2))
            audio_path.write_bytes(base64.b64decode(result['audio_base64']))
        alignment = json.loads(alignment_path.read_text())
        ends = alignment['character_end_times_seconds']
        starts = alignment['character_start_times_seconds']
        characters = alignment['characters']
        spoken = [position for position, character in enumerate(characters) if character.strip()]
        first = starts[spoken[0]]
        last = ends[spoken[-1]]
        window = segment['end'] - segment['start']
        rate = max(1.0, (last - first) / window)
        record = dict(segment, file=audio_path.name, duration=duration(audio_path), first=first, last=last, rate=rate)
        records.append(record)
        (AUDIO / 'generation-progress.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
        print(f'{index + 1}/{len(segments)} scene={segment["scene"]} spoken={last-first:.2f}s window={window:.2f}s local_rate={rate:.3f}', flush=True)
    if any(record['rate'] > 1.18 for record in records):
        raise RuntimeError('Un segmento richiede oltre 18% di accelerazione locale: revisione necessaria prima del mix')
    filters = []
    inputs = []
    word_times = []
    for index, record in enumerate(records):
        inputs += ['-i', str(AUDIO / record['file'])]
        filters.append(f'[{index}:a]atrim=start={record["first"]}:end={record["last"]},asetpts=PTS-STARTPTS,atempo={record["rate"]},adelay={round(record["start"]*1000)}:all=1[a{index}]')
        alignment = json.loads((AUDIO / record['file'].replace('.mp3', '.alignment.json')).read_text())
        for character, start, end in zip(alignment['characters'], alignment['character_start_times_seconds'], alignment['character_end_times_seconds']):
            word_times.append({'character': character, 'start': record['start'] + (start - record['first']) / record['rate'], 'end': record['start'] + (end - record['first']) / record['rate']})
    filters.append(''.join(f'[a{index}]' for index in range(len(records))) + f'amix=inputs={len(records)}:normalize=0,apad,atrim=duration=150,loudnorm=I=-16:TP=-1.5:LRA=11[voice]')
    samples = bytearray(150 * 48000 * 2)
    previous_end = 0
    for index, record in enumerate(records):
        clip = AUDIO / f'placed-{index:02}.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(AUDIO / record['file']), '-af', f'atrim=start={record["first"]}:end={record["last"]},asetpts=PTS-STARTPTS,atempo={record["rate"]}', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(clip)], check=True)
        with wave.open(str(clip), 'rb') as reader:
            content = reader.readframes(reader.getnframes())
        offset = round(record['start'] * 48000) * 2
        if offset < previous_end:
            raise RuntimeError('Sovrapposizione audio rilevata')
        if offset + len(content) > len(samples):
            raise RuntimeError('Audio supera fine video')
        samples[offset:offset + len(content)] = content
        previous_end = offset + len(content)
        record['measured_placed_end'] = previous_end / 96000
    with wave.open(str(AUDIO / 'voice-placed.wav'), 'wb') as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(48000)
        writer.writeframes(samples)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(AUDIO / 'voice-placed.wav'), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-t', '150', str(AUDIO / 'ADERA-voce-150s.wav')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ROOT / 'ADERA-UNIFICATO-150s.mp4'), '-i', str(AUDIO / 'ADERA-voce-150s.wav'), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', '150', '-movflags', '+faststart', str(ROOT / 'ADERA-UNIFICATO-150s-CON-VOCE.mp4')], check=True)
    (AUDIO / 'character-timestamps-global.json').write_text(json.dumps(word_times, ensure_ascii=False))
    report = {'voice': VOICE, 'voice_name': 'MarcoTrox - Warm, Balanced and Polished', 'model': MODEL, 'segments': records, 'global_acceleration': False, 'alignment_source': 'ElevenLabs character timestamps; not independent ASR', 'audio_duration': duration(AUDIO / 'ADERA-voce-150s.wav'), 'video_duration': duration(ROOT / 'ADERA-UNIFICATO-150s-CON-VOCE.mp4')}
    (AUDIO / 'sync-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
