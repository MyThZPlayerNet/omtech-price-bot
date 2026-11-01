# Raport weryfikacji — 1 listopada 2026

## Wykonane lokalnie

| Kontrola | Wynik |
|---|---|
| 39 testów logiki, plików, konfiguracji, API i obsługi błędów | **39/39 OK**, Python 3.12.14 |
| Walidacja obu workflow GitHub Actions | **OK**, actionlint 1.7.12, kod wyjścia 0 |
| Składnia pomocnika Telegram PowerShell | **OK**, parser PowerShell, bez wysyłania tokenu |
| Rzeczywisty odczyt gotowym skryptem | **OK**, 01.11.2026 19:34:18 czasu polskiego (18:34:18 UTC) |
| Cena i wariant | **699,99 EUR**, `43552694304950`, dostępny, „Maschine + 6 Acrylplatten geschenkt / Ohne LightBurn” |
| Dwa testy integracji Git w lokalnym Windows | **Nie zaliczone z powodu ograniczenia środowiska**, przed właściwym testem zapisu |
| Wysyłka do rzeczywistego Telegrama użytkownika | **Niewykonana**, brak skonfigurowanych sekretów |

Lokalne testy Git nie przeszły etapu utworzenia klona repozytorium testowego: Git for Windows nie mógł uruchomić procesu powłoki MSYS (`NtCreateDirectoryObject`, `0xC0000022`). Następnie te same testy **przeszły na Ubuntu w GitHub Actions** — szczegóły poniżej.

## Wykonane na GitHub Actions

**41/41 testów OK**, w tym oba testy integracji Git: zapis do zdalnego repozytorium testowego, brak pustych commitów, ochrona plików spoza data/ oraz ponowienie push z rebase po równoczesnej zmianie README. Testowe repozytorium zdalne było lokalnym bare remote na runnerze, bez osobnych usług i opłat.

- [Zakończone uruchomienie testów — Success](https://github.com/MyThZPlayerNet/omtech-price-bot/actions/runs/41338094668)
- [Log zadania z 41 testami i rzeczywistym odczytem](https://github.com/MyThZPlayerNet/omtech-price-bot/actions/runs/41338094668/job/124942108231)
- Sprawdzony commit: `85099939e78cc29dd2a2b5d3305cc28dd1da3618`.
- Środowisko: Ubuntu 24.04.5, Python 3.12.15, Git 2.56.0.
- Czas testów: 0,523 s; pełne uruchomienie około 12 s według GitHuba.
- Rzeczywisty odczyt z serwera GitHuba: **01.11.2026 19:43:57 czasu polskiego**, cena **699,99 EUR**, dostępny, dokładny wariant `43552694304950`.
- Krok pobierania ceny ma własny wynik **success**; nie wnioskujemy tego tylko z zielonego całego zadania, bo odczyt kontrolny ma continue-on-error.

To potwierdza działanie kodu i dostępu do sklepu z runnera. Nie zastępuje testu wysyłki na rzeczywisty Telegram ani produkcyjnego zapisu danych przez GITHUB_TOKEN.

## Zakres 39 zaliczonych testów

Wybór dokładnego wariantu zamiast minimalnej ceny produktu; brak i duplikat wariantu; inna waluta i produkt; puste, zerowe, ujemne, tekstowe i niecałkowite ceny; dostępność znana i nieznana; inicjalizacja bez fałszywej promocji; dokładnie 5% i tuż poniżej; porównanie z poprzednią ceną zamiast maksimum historycznego; kolejne obniżki i ponowna promocja po wzroście; próg kwotowy i jego zmiana; brak ponowienia przy tej samej cenie; powrót dostępności; zapis każdego odczytu CSV; odrzucanie uszkodzonego stanu; zachowanie kolejki przy awarii; deduplikacja po restarcie; ręczne potwierdzanie niepewnej wysyłki; ograniczone ponawianie GET; 403 bez ponawiania; 429 z Retry-After; HTML zamiast JSON; nadmiarowy rozmiar odpowiedzi; przekierowanie; wspólna sesja waluty i produktu; brak sekretów przed pomiarem; ukrywanie tokenu w komunikacie błędu Telegrama.

Wywołania Telegrama w tych testach były **symulowane**. Nie wysłano wiadomości do prawdziwego konta.

## Dowody i odtworzenie

- `verification/unit-tests.txt` — pełny wynik 39 testów.
- `verification/git-integration.txt` — nieudana lokalna próba integracji Git, ścieżki domowe zanonimizowane.
- `verification/workflow-lint.txt` — puste wyjście oznacza brak błędów; kod wyjścia zapisano w results.json.
- `verification/live-fetch.json` i `.txt` — rzeczywisty odczyt API przez monitor.py, bez zapisu produkcyjnej historii.
- `verification/results.json` — kody wyjścia i identyfikacja poprzedniej paczki.

Do odtworzenia: `python -m unittest discover -s tests -v`, `python monitor.py --mode fetch`. W lokalnym środowisku Windows testy plikowe wykonano z TEMP/TMP skierowanymi do zapisywalnego folderu roboczego. Projekt nie wymaga instalowania pakietów pip.

## Stan wdrożenia

Repozytorium wskazane przez użytkownika: https://github.com/MyThZPlayerNet/omtech-price-bot (widoczność Public w momencie sprawdzenia). **Kod, workflow i dokumentacja zostały wgrane do main; Actions są aktywne.** Harmonogram zapisano jako `17 */2 * * *` (UTC).

W ustawieniach GitHub potwierdzono jeszcze brak sekretów Telegrama. Nie wykonano prawdziwego testu wiadomości, pierwszego produkcyjnego `check` ani obserwacji późniejszego uruchomienia schedule. Nie zapisano sztucznych danych w katalogu data/.

Końcowa akceptacja działania wymaga: zielonego testu online, poprawnego odczytu z GitHuba, odebrania rzeczywistej wiadomości testowej, pierwszego `check` z zapisem danych i co najmniej jednej późniejszej kontroli wyzwolonej harmonogramem. Samo istnienie plików workflow tego nie dowodzi.
