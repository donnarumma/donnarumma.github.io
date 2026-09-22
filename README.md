# donnarumma.github.io

Sito personale di **Francesco Donnarumma**. Replica statica e modificabile offline
del [sito Google Sites](https://www.francescodonnarumma.net/), importato il
14 settembre 2026.

Repository: <https://github.com/donnarumma/donnarumma.github.io>.
Cartella locale: `CurriculumVitae/Website`, con un proprio `.git`, indipendente
dal repository del CV. Nessun materiale di Sara Di Costanzo e' incluso.

## Aprire Il Sito

Aprire [index.html](index.html) nel browser. Non servono server, Node, npm,
Google Sites o connessione Internet. I file HTML gia' generati sono inclusi.

Sono locali pagine, ricerca, filtri, immagini, GIF, font, CV e bibliografia.
I collegamenti a editori, profili e video YouTube richiedono Internet quando
vengono aperti; non vengono caricati iframe o tracker in background.

I link esterni si aprono in una nuova scheda con `noopener noreferrer`.
Navigazione interna, ancore e download locali restano nella stessa scheda;
anche gli URL assoluti dei domini personali e di `donnarumma.github.io`
sono riconosciuti come interni. La regola viene applicata alla generazione
dell'HTML, quindi funziona anche senza JavaScript.

GitHub e' tra i dodici profili principali della barra superiore. DBLP rimane
tra i profili attivi nella pagina Contacts, senza occupare spazio nella barra:
`secondary_profiles` in `content/settings.json` controlla questa distinzione
ed e' separato da `archived_profiles`, riservato ai profili non piu' usati.

## Modificare I Contenuti

| File | Contenuto |
| --- | --- |
| [content/site.json](content/site.json) | Testi delle sei pagine, 70 voci bibliografiche, immagini, highlights e video. |
| [content/settings.json](content/settings.json) | Contatti, profili aggiuntivi, URL pubblico e indicizzazione. |
| [assets/css/site.css](assets/css/site.css) | Impaginazione, colori e versioni desktop/mobile. |
| [templates/base.html](templates/base.html) | Struttura comune, navigazione, metadati e ricerca. |
| [assets/images/](assets/images/) | Immagini originali e animazioni conservate localmente. |
| [assets/downloads/](assets/downloads/) | Copie pubblicabili del CV PDF e del BibTeX canonico. |

In `content/site.json`, cercare il titolo o il testo da modificare. Ogni voce di
`pages.papers.entries` ha un `id` stabile, un `year` per il filtro e una lista
`paragraphs` con testo/HTML semplice (`strong`, `em`, `a`, `br`). Si possono usare
normalmente lettere accentate UTF-8. L'ordine nell'array e' l'ordine nella pagina.
Per aggiungere una voce usare un nuovo ID, senza rinumerare le vecchie ancore.
Il campo facoltativo `title` permette di specificare il titolo nella ricerca.

Dalla cartella `Website`, dopo le modifiche:

```bash
python3 tools/build.py
python3 tools/check.py
```

Servono solo Python 3 e la sua libreria standard. Non modificare direttamente
gli `index.html` o `assets/js/search-index.js`: vengono rigenerati.

Per aggiornare esplicitamente i due download dal CV nella cartella superiore:

```bash
python3 tools/sync_cv.py
python3 tools/build.py
python3 tools/check.py
```

La sincronizzazione copia solo PDF e BibTeX: non riscrive automaticamente la
pagina Papers, che conserva anche tesi, interventi e contributi presenti nel
sito storico ma non necessariamente nel BibTeX. Nessuna modifica ai CV originali.

### PDF E Citazioni Dei Singoli Lavori

Le copie locali dei paper sono in `assets/downloads/papers/`; i record BibTeX
individuali sono nella sottocartella `bibs/`. I link `[pdf]` e `[bib]` vengono
definiti nelle rispettive voci di `content/site.json`, senza modificare i DOI
dei titoli o i link alle pagine arXiv. I PDF ufficiali gia' collegati restano
preferiti alle copie locali.

L'integrazione del 17 settembre 2026 usa `~/OneDrive/PUBLIC/papers/` per i PDF
e il BibTeX canonico del CV per le citazioni, con un record presente solo nel
BibTeX dell'archivio pubblico. Il confronto avviene per titolo e DOI, non solo
per anno nel nome del file. Provenienza, hash e abbinamenti da verificare sono
in [migration/paper-downloads.json](migration/paper-downloads.json).

Il PDF del commento BBS del 2010 contiene anche altri contributi: il link apre
la pagina 28 del documento raccolto. La copia del commento Physics of Life
Reviews del 2015 e' una bozza editoriale (proof), indicata nel tooltip.
Il file del 2008 sulle interfacce cervello-calcolatore non e' stato associato
a "L'uomo bionico e il futuro della mente": il titolo differisce e
l'equivalenza resta da confermare. I file originali dell'archivio non vengono
modificati e non vengono pubblicate cartelle private del progetto CV.

## Verifiche

`tools/check.py` controlla file, link interni, ancore, conteggio delle voci,
assenza di dipendenze remote, destinazione dei link e integrita' delle immagini
originali. I test mirati per URL, attributi e riscritture dei link si eseguono con:

```bash
python3 -m unittest discover -s tools -p 'test_*.py'
```

Il test opzionale `tools/browser_check.py` verifica Chromium a cinque larghezze,
con Internet bloccato: immagini, font, ricerca, filtri e navigazione mobile.
Richiede `websockets` e un browser dedicato con CDP sulla porta 9334.

```bash
chromium --headless=new --disable-gpu --remote-debugging-port=9334 --user-data-dir=/tmp/francesco-website-test about:blank
```

In un altro terminale:

```bash
python3 tools/browser_check.py
```

Risultati e screenshot in `.local/checks/`, esclusi da Git e dalla pubblicazione.
Arrestare il browser di test al termine. Il controllo statico non certifica la
disponibilita' attuale di tutti i vecchi link verso editori e servizi esterni.

## Pubblicazione

Prima versione completa caricata il 2026-09-15, commit `8c65efd`.
**GitHub Pages era gia' attivo** sul repository: il deploy automatico esistente
ha pubblicato il sito su <https://donnarumma.github.io/> dopo il push.
Non sono state modificate le impostazioni Pages, Google Sites o DNS.
Il dominio personale resta invariato.

Il workflow alternativo [Publish Website (Manual)](.github/workflows/pages.yml)
e' predisposto ma non e' stato eseguito. Se adottato come sorgente di
pubblicazione, carica solo HTML e `assets`, escludendo sorgenti e note.
La configurazione Pages attualmente esistente aggiorna invece il sito dopo
il push; `.local/` e `_site/` non sono comunque presenti nel repository remoto.

Procedura e punti da rivedere prima del passaggio:
[migration/README.md](migration/README.md).

## Substack Import Staging

`substack-staging/` contains a deliberately unlinked and `noindex` RSS source
for importing selected long-form posts into Substack. The current feed is:

<https://www.francescodonnarumma.net/substack-staging/feed.xml>

It carries only the article *Reading is a form of active sampling*, including
the four figure files at stable public URLs. In Substack use `Settings` ->
`Import/Export` -> `Import posts`, then provide the feed URL and import the
single discovered item. The staging page is public only so that Substack can
fetch it; it is not linked from the site navigation and asks search engines not
to index it.

## Provenienza E Licenze

I contenuti e le immagini provengono dal sito personale esistente. Questo
repository non concede una licenza generale sui testi, sulle immagini o sui
marchi di terzi. I loghi identificano i rispettivi servizi.

- Lato e Pacifico: licenze OFL incluse in `assets/fonts/`.
- Lucide 0.468.0: licenza ISC inclusa in `assets/vendor/Lucide-LICENSE`.
- OpenAlex: [simbolo ufficiale bianco](https://github.com/ourresearch/openalex-gui/blob/master/public/brand-assets/openalex-mark-white.png),
  introdotto nel [nuovo marchio](https://blog.openalex.org/a-new-logo-for-openalex/),
  conservato in PNG a 526 x 526 pixel e visualizzato piu' piccolo degli altri loghi.
- Substack e W Social: icone ufficiali delle rispettive piattaforme, conservate
  localmente in PNG a 180 x 180 pixel.
- GitHub: logo bianco ufficiale dal [Brand Toolkit](https://brand.github.com/foundations/logo),
  conservato localmente per collegare il profilo `github.com/donnarumma`.
- [migration/assets.json](migration/assets.json): URL originali, dimensioni,
  numero di fotogrammi e hash SHA-256.
- [migration/cv-snapshot.json](migration/cv-snapshot.json): provenienza dei download.

`tools/import_google_site.py` e' uno strumento di **prima importazione**, non di
sincronizzazione quotidiana. Richiede BeautifulSoup/Pillow e puo' richiedere la
cache del browser per i file Google. Si rifiuta di sovrascrivere i contenuti
esistenti senza `--overwrite`: non rieseguirlo sui testi gia' modificati.
