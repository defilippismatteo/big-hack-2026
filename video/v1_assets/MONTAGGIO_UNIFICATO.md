# ADERA — specifica del video unificato

## Fonti e stato
- ChatGPT: `outputs/adera-reanimate-sol61-low/ADERA-150s.mp4`, progetto editabile nella stessa directory.
- Gemini: prima versione Gemini, `outputs/adera-reanimate-gemini4-medium/adera-presentation-150s.mp4`, progetto editabile nella stessa directory. NON versione Remotion.
- Matteo: trovata `Video_Matteo/` in `origin/video-matteo`, commit `2a9019ecfa6ee2785fe88471a70c4ce34af4ead0`, con HTML/CSS/GSAP, asset e `renders/ADERA-preliminare.mp4`. Leggere da Git senza cambiare branch; preservare gli originali e le modifiche locali alla dashboard.
- Dashboard: ultima versione effettiva da identificare e verificare al momento dell'integrazione, non cristallizzare automaticamente lo screenshot già usato da ChatGPT. Escludere Come funziona e includere modifiche correnti.

## Regole globali
Riutilizzare gli asset e le specifiche tecniche approvate: 1920×1080, 30 fps, obiettivo 150 secondi, massimo 180, nessuna voce né sottotitoli. Sfondo di Matteo in tutte le scene: solo sfondo, senza importare automaticamente altri elementi. Costruire un progetto editabile unico, non tagliare alla cieca tre MP4 appiattiti quando esistono i sorgenti.

Fedeltà mixed: conservare movimenti e visual delle singole fonti selezionate; dati accurati e risultati verificati. Segnali Decision distinti da CTR/forecast. Non alterare i video originali.

## Mappa scena per scena
| Parte | Animazione | Grafica / contenuti |
|---|---|---|
| Intro | Matteo | Matteo |
| Scena immediatamente successiva | Matteo | Matteo |
| Grafico | ChatGPT: disegno linea, camera segue punta, zoom-out | Struttura Gemini; accuratezza e serie dati ChatGPT, da verificare contro export |
| Etichette sui dati e widget modelli | Gemini | Gemini: Timestral e CatBoost, loghi approvati |
| Orchestrazione T3 Code | Matteo | Matteo |
| Informazioni singola persona | Matteo | Matteo |
| Probabilità e scroll feed | Gemini | Gemini; AGGIUNTA etichetta «Gemini Decision 1» con logo Gemini accanto |
| Zoom-out persone | Matteo | Matteo |
| «Dalle reazioni, segnali» | Matteo | Matteo |
| «Che cosa attira l'attenzione» | Matteo | Matteo |
| Ingresso / movimento dashboard | Gemini: solo animazione | Dashboard ChatGPT aggiornata all'ultima versione disponibile, senza Come funziona |
| Chiusura | Matteo | Matteo |

## Prima del montaggio
1. Localizzare sorgente/video Matteo e leggere istruzioni applicabili, senza cambiare branch né toccare lavoro parallelo.
2. Identificare timestamp e selettori equivalenti nei tre progetti, mantenendo la distinzione fra struttura grafica, movimento e dati.
3. Verificare versione dashboard e mapping colonne/serie del grafico.
4. Comporre in nuova directory, verificare transizioni e renderizzare. Nessun render unificato prodotto finora.
