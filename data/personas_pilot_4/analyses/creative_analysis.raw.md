*Nota di metodo: tutti i valori citati sono probabilità a set chiuso del modello su 4 profili sintetici e 12 creatività; non rappresentano CTR reali, significatività statistica o preferenze demografiche generalizzabili. I `reason_code` indicano etichette predefinite, non citazioni spontanee.*

---

## 1. Tre pattern ricorrenti

1. **Prevalenza di bassa rilevanza nei profili a basso interesse (`P001`, `P004`)**
   `low_relevance_or_need` ha la media più alta (`0.260`). Su `beauty_skincare-P001` e `beauty_skincare-P004` l'azione più probabile è quasi sempre `scroll` con `scroll__irrelevant` (es. `NDL-S2`: `P001` `scroll 0.571`, score `0.414`; `P004` `scroll 0.590`, score `0.525`; `NDL-B2`: `P004` `scroll 0.596`, score `0.553`). Unica attenuazione su `NDL-S4` (SPF 50): `P004` passa a `glance 0.381` (`click 0.183`, score `0.292`).
   - *Alternative e limiti*: un basso interesse di categoria non è automaticamente un difetto dell'annuncio correggibile; inoltre `context_distraction` (media `0.070`, fino a `0.122` su `NDL-B4`/`P004`) può riflettere il contesto del feed.

2. **Picco di scetticismo su urgenza esplicita e Black Friday con creator (`NDL-B4`, `NDL-U1`)**
   `skepticism` è il secondo driver medio (`0.161`). Quando il gancio iniziale usa countdown o `-40%` (`NDL-B4`, `NDL-U1`), anche i profili interessati `P002` e `P003` passano a `scroll__skeptical`: su `NDL-B4` `P001` (`scroll 0.737`, `skepticism 0.339`), `P002` (`0.496`, `0.289`) e `P003` (`0.411`, `0.303`); su `NDL-U1` `P001` (`0.685`, `0.382`), `P002` (`0.438`, `0.282`) e `P003` (`0.375`, `0.308`). Su formati più sobri (`NDL-S3`, `NDL-U3`), lo scetticismo su `P002`/`P003` cala (`0.063–0.092`).
   - *Alternative e limiti*: il modello non separa causalmente l'effetto della leva promozionale dal ritmo del creator o dal formato video.

3. **Frizione tra `stop` e `click` sui profili interessati (`P002`, `P003`)**
   `P003` si ferma spesso (`NDL-S3` `stop 0.451` vs `click 0.153`; `NDL-U3` `stop 0.412` vs `click 0.113`), ma `weak_offer` (media `0.122`, picco `0.219` su `NDL-B2`/`P003`) e `trust_information_search` (`0.068–0.083` su `P003`) frenano l'apertura. `P002` apre di più su `NDL-S2` (`click 0.309`) e `NDL-S1` (`0.260`), ma frena su `NDL-B2` (`weak_offer 0.195`).
   - *Alternative e limiti*: `P003` cambia routine lentamente per abitudine; nulla può essere dedotto da landing page non mostrate.

---

## 2. Quattro modifiche creative da testare

1. **`NDL-U1` × `beauty_skincare-P002` (Patrizia Ferri)**
   - *Osservazione del modello*: `scroll 0.438` (`scroll__skeptical`), `skepticism 0.282`.
   - *Ipotesi*: il countdown grande nei primi 2 secondi attiva la diffidenza verso l'urgenza e non offre basi informative.
   - *Variante da testare*: aprire con etichetta/INCI leggibile e dati di tollerabilità in primo piano (**da verificare prima** se disponibili e documentabili), eliminando il countdown iniziale e lasciando l'eventuale indicazione promozionale solo in chiusura testuale.

2. **`NDL-S4` × `beauty_skincare-P003` (Lorenzo Cattaneo)**
   - *Osservazione del modello*: `stop 0.334` (`stop__interested`), `click 0.100`, `skepticism 0.181`, `weak_offer 0.152`, `trust_information_search 0.068`.
   - *Ipotesi*: l'infografica fitta con 8 punti e la barra `scorte al 15%` tolgono credibilità a chi cerca dati specifici su filtri, pH e resa.
   - *Variante da testare*: sostituire gli 8 punti e la barra scorte con 3 parametri tecnici essenziali (tipo di filtri solari, pH dichiarato e tempi di assorbimento — **da verificare prima** su scheda tecnica).

3. **`NDL-B3` × `beauty_skincare-P001` (Chiara Bellini)**
   - *Osservazione del modello*: `scroll 0.582` (`scroll__irrelevant`), `low_relevance_or_need 0.433`, `skepticism 0.219`.
   - *Ipotesi*: il carosello di 6 kit a prezzi barrati `-40%` confligge con la ricerca di essenzialità ecologica (fermo restando il basso interesse di categoria).
   - *Variante da testare*: isolare un singolo detergente essenziale evidenziando lista ingredienti breve, imballaggio riciclabile/ricaricabile, certificazioni ecologiche verificabili e sede produttiva europea (**da verificare prima** sul prodotto reale), rimuovendo il framing Black Friday.

4. **`NDL-U2` × `beauty_skincare-P004` (Davide Marchetti)**
   - *Osservazione del modello*: `scroll 0.451` (`scroll__irrelevant`), `low_relevance_or_need 0.473`, `click 0.102`.
   - *Ipotesi*: tre flaconi su marmo con scadenza domenicale non rispondono al bisogno di uso rapido e costi di consegna chiari.
   - *Variante da testare*: mostrare un singolo prodotto essenziale ad applicazione rapida (es. formato stick o resistente a sudore/vento, **da verificare prima** se in gamma) con tempi e costi standard di spedizione espliciti (**da verificare prima**), senza scadenza a tempo.

*Test A/B proposto*: confrontare ogni coppia (asset originale vs variante) in un piccolo test A/B sugli stessi 4 profili congelati a parità di contesto feed, osservando le variazioni di `action_probabilities` e `diagnostic_scores` prima di qualsiasi estensione.

---

## 3. Tre domande diagnostiche aggiuntive per Decision

1. **Quale elemento dell'annuncio ha generato più attrito o esitazione?**
   - *Scelte*: Nessun attrito rilevante | Tono promozionale o urgenza | Mancanza di dati su ingredienti o uso | Visual o formato poco chiaro | Offerta poco comprensibile | Non pertinente (categoria non di interesse) | Non determinabile.

2. **Quale informazione assente nell'annuncio ti servirebbe per valutare l'apertura?**
   - *Scelte*: Nessuna informazione mancante | Composizione/INCI e tollerabilità | Origine produttiva o sostenibilità | Modalità d'uso e resa pratica | Condizioni chiare di prezzo o spedizione | Non pertinente | Non determinabile.

3. **L'eventuale scorrimento rapido dipende soprattutto dal contesto o dall'annuncio?**
   - *Scelte*: Prevalentemente dal contesto del feed/momento | Prevalentemente dall'annuncio | Da entrambi in modo simile | Nessuno scorrimento per distrazione | Non determinabile.
