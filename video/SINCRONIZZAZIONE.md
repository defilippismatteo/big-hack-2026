# Sincronizzazione del copione approvato

Aggiornamento: audio generato e montato. Le tabelle seguenti conservano il piano originale; per tempi misurati, correzioni locali e limiti consultare `audio/sync-report.json` e `audio/VERIFICA.md`. Il master audio e video dura 150 secondi. Verifica basata su timestamp del provider, non ASR indipendente o controllo umano delle pronunce.

Testo invariato. 13 blocchi coprono le scene dei 150 secondi. I valori sotto sono budget di lettura, non misure di audio: la voce non è ancora generata.

| Finestra parlato | Parole | Ritmo previsto |
|---|---:|---:|
|0.30–8.50 s|16|117.1 parole/min|
|9.30–15.50 s|13|125.8 parole/min|
|16.30–26.50 s|21|123.5 parole/min|
|27.30–43.50 s|35|129.6 parole/min|
|44.05–52.85 s|20|136.4 parole/min|
|53.30–64.50 s|25|133.9 parole/min|
|65.30–75.50 s|23|135.3 parole/min|
|76.30–94.50 s|37|122.0 parole/min|
|95.30–103.50 s|17|124.4 parole/min|
|104.30–111.50 s|16|133.3 parole/min|
|112.30–126.50 s|30|126.8 parole/min|
|127.30–143.50 s|34|125.9 parole/min|
|144.30–149.50 s|5|57.7 parole/min|

Il blocco modelli usa 44.05–52.85 s per evitare un ritmo eccessivo: widget in ingresso 45.8–46.55 s, frase Timestral da 46.1 s e frase CatBoost da 48.4 s.

## Cue del grafico e dei modelli

| Tempo | Frase |
|---|---|
|27.25–33.55 s|Qui seguiamo una previsione del costo per mille impressioni, dal sedici al trenta novembre.|
|33.55–36.70 s|La linea si disegna giorno dopo giorno,|
|36.70–38.95 s|poi la vista si allarga:|
|38.95–43.50 s|così possiamo leggere l'intero andamento, senza aggiungere picchi artificiali.|
|44.05–46.10 s|Le date chiave danno contesto.|
|46.10–48.40 s|Timestral prevede i costi pubblicitari;|
|48.40–52.85 s|CatBoost entra nel confronto dei modelli sui dati di validazione.|

La battuta «poi la vista si allarga» attraversa lo zoom-out originale 37.2–38 s. Etichette evento in ingresso 44.2/44.7/45.2 s. Il pan dashboard avviene 128.4–131 s, nella prima frase del relativo blocco. La firma finale parte dopo 144.3 s, lasciando una pausa finale.

Dopo la generazione: misurare l’audio per segmento e gli allineamenti parola per parola; aggiustare pause o ritmo locale, mantenendo il testo approvato. Validare assenza di troncamenti, sovrapposizioni e deriva alla fine dei 150 s. Nessuna accelerazione globale automatica.
