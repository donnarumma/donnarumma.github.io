# Verification

Eseguita il 2026-09-14 sulla copia locale, senza pubblicare il sito.

## Ricontrollo Del 2026-09-15

- Ripetuti con esito positivo i controlli statici e tutte le 18 combinazioni
  pagina/viewport dopo la sostituzione del riquadro OpenAlex con il logo ufficiale.
- Logo originale a 526 x 526 pixel, visualizzato entro 62 pixel su desktop e
  40 su mobile; nessun riquadro pieno, deformazione o fuoriuscita dal contenitore.
- Copia del PDF aggiornata e verificata byte per byte rispetto all'ultimo
  `DONNARUMMA_CV.pdf` compilato nella cartella principale.
- Font, immagini, ricerca e filtri offline verificati; nessun errore JavaScript
  o richiesta HTTP/HTTPS originata dalle pagine durante i test.
- Prima versione completa caricata nel repository GitHub, commit `8c65efd`.
  Il deploy automatico Pages gia' presente e' terminato con successo. Nessun
  avvio manuale del workflow alternativo o modifica di dominio/impostazioni Pages.

## Esito

- Build offline completata con Python standard, senza Node o dipendenze di rete.
- Controllati 7 HTML: homepage principale e sei percorsi del sito.
- Tutte le 70 voci bibliografiche presenti, nell'ordine del sorgente.
- Link interni, ancore, immagini, font e hash degli asset originali verificati.
- Chromium: 18 combinazioni pagina/viewport, senza errori JavaScript o richieste
  HTTP/HTTPS originate dalle pagine, con Internet bloccato.
- Tutte le sei pagine a 1440 x 1000 e 390 x 844; Home e Papers anche a
  320 x 740, 768 x 1024 e 1920 x 1080.
- Nessuno scorrimento orizzontale indesiderato; immagini e sfondi caricati,
  font locali disponibili e scritta OpenAlex contenuta correttamente.
- Ricerca globale, filtri per testo/anno, stato senza risultati, reset dei filtri,
  apertura/chiusura del menu mobile e chiusura della ricerca verificati.
- Verifica aggiuntiva a 320 pixel senza JavaScript: navigazione e tutte le
  70 voci restano disponibili.
- Pacchetto `_site` confrontato con la copia locale. Contiene solo pagine,
  asset e file di configurazione pubblici, non sorgenti o cache di lavoro.
- Browser dedicato ai test chiuso al termine. Nessun server necessario per
  aprire `index.html` localmente.

Screenshot e rapporti dettagliati: `.local/checks/`, esclusi da Git.
Il controllo non certifica la disponibilita' dei link esterni storici o la
configurazione GitHub Pages/DNS, che non sono state modificate.
