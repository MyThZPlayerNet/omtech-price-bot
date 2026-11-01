# OMTech K40 — instrukcja po polsku

Gotowy monitor ceny konkretnego wariantu `43552694304950` w niemieckim sklepie OMTech. Działa w Pythonie 3.12, bez dodatkowych bibliotek. GitHub Actions uruchamia go co 2 godziny, więc komputer może być wyłączony.

**Zacznij od punktu 1. Nie potrzebujesz instalować Pythona na komputerze.** Jeżeli projekt został już wgrany do Twojego repozytorium, przejdź do punktu 4.

## Co jest już przygotowane

- Cena w EUR z publicznego API Shopify, wybór wyłącznie podanego ID wariantu.
- Kontrola waluty sesji przez `/cart.js`, we wspólnej sesji z zapytaniem o produkt.
- Obniżka co najmniej 5% względem **poprzedniego poprawnego odczytu**.
- Domyślna cena alarmowa **650 EUR**. Możesz ją zmienić lub wyłączyć.
- Historia każdego udanego odczytu w `data/price_history.csv`.
- Trwały stan i kolejka wiadomości w `data/store.json`, zapisywane jako commity Git.
- Telegram, test konfiguracji, ochrona przed zwykłym powtarzaniem alertów.
- Ograniczone ponawianie błędów sieciowych; blokady dostępu nie są obchodzone.

Wyniki rzeczywistych testów znajdziesz w `RAPORT_TESTOW.md`. Paczka nie zawiera tokenów ani danych Twojego czatu. Historia zacznie powstawać po pierwszym udanym uruchomieniu `check`.

## 1. Konto GitHub

1. Otwórz [github.com/signup](https://github.com/signup).
2. Podaj własny e-mail, ustaw hasło i nazwę użytkownika. Wykonaj weryfikację wymaganą przez GitHub.
3. Potwierdź adres e-mail wiadomością od GitHuba. Wybierz bezpłatny plan, jeśli pojawi się wybór.
4. Zaloguj się na [github.com/login](https://github.com/login). Jeżeli masz już konto, użyj go.

## 2. Prywatne repozytorium

1. Otwórz [github.com/new](https://github.com/new).
2. W polu **Repository name** wpisz `omtech-price-bot`.
3. Wybierz **Private**. Zaznacz **Add a README file** (w nowszym widoku: przełącznik **Add README**).
4. Pozostaw pozostałe ustawienia domyślne i kliknij **Create repository**.
5. Sukces: adres ma postać `https://github.com/TWOJ_LOGIN/omtech-price-bot`, a przy nazwie widnieje **Private**.

Nie zmieniaj istniejącego repozytorium innego projektu. Jeśli taka nazwa jest już zajęta na Twoim koncie, użyj `omtech-k40-monitor`.

## 3. Dodanie plików

1. Kliknij pobrany ZIP prawym przyciskiem → **Wyodrębnij wszystkie** → **Wyodrębnij**.
2. Otwórz rozpakowany folder `omtech-price-bot`. W środku muszą być m.in. `monitor.py`, `config.json`, foldery `.github`, `scripts`, `tests`, `data`.
3. W repozytorium, w zakładce **Code**, kliknij **Add file → Upload files** (czasem **+ → Upload files**).
4. Przeciągnij **zawartość** folderu `omtech-price-bot` do pola przesyłania. Nie przesyłaj samego ZIP-a i nie przeciągaj nadrzędnego folderu jako dodatkowego poziomu.
5. Wpisz opis `Dodanie monitora OMTech` i kliknij **Commit changes**, zapisując do gałęzi `main`.
6. Sprawdź, że `monitor.py` i `config.json` są w głównym katalogu repozytorium.
7. Kliknij `.github` → `workflows`. Muszą być tam `check-price.yml` oraz `tests.yml`.

Jeżeli przeglądarka pominęła `.github`: w głównym katalogu kliknij **Add file → Create new file**, wpisz nazwę `.github/workflows/check-price.yml`, wklej pełną zawartość odpowiadającego pliku z paczki i zapisz **Commit changes**. Powtórz dla `.github/workflows/tests.yml`. Możesz otworzyć plik YAML przez prawy przycisk → **Otwórz za pomocą → Notatnik**. Te pliki nie zawierają sekretów.

Sukces: w zakładce **Actions** pojawiają się **Monitor OMTech K40** i **Testy projektu**. Testy projektu powinny zakończyć się zielonym symbolem.

## 4. Utwórz bota w Telegramie

1. Otwórz [t.me/BotFather](https://t.me/BotFather) i wybierz **Open in Telegram**. Używaj oficjalnego, zweryfikowanego konta `@BotFather`.
2. Kliknij **Start**, wyślij `/newbot`.
3. Gdy zapyta o nazwę, wpisz np. `Mój OMTech K40`.
4. Gdy zapyta o username, wpisz unikalną nazwę zakończoną `bot`, np. `omtech_k40_twojlogin_bot`. Jeśli nazwa jest zajęta, dopisz własne cyfry.
5. BotFather pokaże komunikat o utworzeniu bota i token API. Zachowaj go w tej rozmowie z BotFather lub w swoim menedżerze haseł.
6. Kliknij link do nowego bota w wiadomości BotFather. Kliknij **Start** lub wyślij `/start` w **prywatnej rozmowie**.

Token jest hasłem do bota. **Nie wklejaj go do rozmowy z asystentem, kodu, issue ani plików GitHuba.** Bezpośrednio z BotFather wkleisz go do GitHub Secrets w punkcie 6. Jeśli został ujawniony, odwołaj go w BotFather przez `/revoke`, a następnie zaktualizuj sekret.

## 5. Poznaj identyfikator prywatnego czatu bez tokenu w adresie przeglądarki

Do paczki dołączony jest mały pomocnik Windows. Token wprowadzasz lokalnie w ukrytym polu; skrypt nie zapisuje go do pliku ani nie wypisuje. Nie korzysta z zewnętrznych botów do odczytywania ID.

1. W Eksploratorze plików otwórz rozpakowany folder `omtech-price-bot` (ten z `monitor.py`).
2. Kliknij pasek adresu folderu, wpisz `powershell` i naciśnij Enter. Otworzy się okno PowerShell w tym folderze.
3. Wpisz dokładnie poniższe polecenie i naciśnij Enter:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\telegram-chat-id.ps1
   ```

   Zezwolenie na wykonanie dotyczy tylko tego uruchomienia; polecenie nie zmienia systemowej polityki skryptów.

4. Gdy zobaczysz `Wklej token z BotFather`, wklej token bezpośrednio z BotFather i naciśnij Enter. Znaki są ukryte. Nie wpisuj tokenu jako osobnego polecenia PowerShell.
5. Skrypt pokaże username potwierdzonego bota i jednorazowy tekst, np. `/setup_a1b2c3d4e5`.
6. W prywatnej rozmowie z **tym botem** wyślij dokładnie wyświetlony tekst.
7. Wróć do PowerShell i naciśnij Enter.
8. Skopiuj liczbę po `TELEGRAM_CHAT_ID =`. To identyfikator Twojego czatu. Sukces: pojawia się ta liczba i nazwa właściwego bota.
9. Zamknij okno PowerShell. Nie wykonuj tego etapu w sesji z włączonym nagrywaniem poleceń/transkrypcji.

Jeśli nie ma kodu w odpowiedzi, sprawdź właściwego bota i spróbuj ponownie. Telegram przechowuje oczekujące aktualizacje ograniczony czas; wykonaj kroki bez długiej przerwy. Ten pomocnik jest przeznaczony dla nowego bota bez webhooka i bez innego programu odbierającego wiadomości.

## 6. Wstaw dwie wartości do GitHub Secrets

1. Otwórz swoje repozytorium → **Settings**.
2. Z lewej wybierz **Secrets and variables → Actions**.
3. Kliknij **New repository secret**.
4. W **Name** wpisz `TELEGRAM_BOT_TOKEN`. W **Secret** wklej token **bezpośrednio z BotFather**. Kliknij **Add secret**.
5. Ponownie **New repository secret**. W **Name** wpisz `TELEGRAM_CHAT_ID`. W **Secret** wklej liczbę z pomocnika. Kliknij **Add secret**.
6. Sukces: na liście są obie nazwy. GitHub nie pokaże zapisanych wartości — to prawidłowe.

Nie dodawaj spacji, cudzysłowów ani nazwy zmiennej do pola wartości. Użyj zakładki **Secrets**, nie **Variables**. Nie potrzeba osobistego tokenu GitHuba: zapis historii wykorzystuje automatyczny `GITHUB_TOKEN`.

## 7. Włącz Actions i sprawdź uprawnienia

1. Otwórz **Actions**. Jeśli widzisz komunikat o włączeniu przepływów, kliknij **I understand my workflows, go ahead and enable them**.
2. W **Settings → Actions → General** upewnij się, że Actions są dozwolone i dopuszczone są oficjalne akcje `actions/*`.
3. Workflow ma już `permissions: contents: write`, potrzebne wyłącznie do zapisu historii. Jeśli polityka konta lub organizacji blokuje to uprawnienie, właściciel musi dopuścić zapis. Nie potrzeba otwierania repozytorium publicznie ani dodawania PAT.
4. Gałąź domyślna (zwykle `main`) musi pozwalać botowi zapisywać commity w `data/`. Ochrona wymagająca PR dla każdej zmiany może blokować ten projekt. Instrukcja zakłada nowe, prywatne repozytorium bez takiej reguły.

## 8. Pierwsze testy i uruchomienie

W repozytorium przejdź do **Actions → Monitor OMTech K40 → Run workflow**. Wybieraj gałąź domyślną `main`.

1. W polu **mode** wybierz `fetch`. Pozostaw **alert_id** puste. Kliknij zielone **Run workflow**.
2. Otwórz nowe uruchomienie → zadanie **monitor** → krok **Rzeczywisty odczyt bez zapisu i bez Telegrama**. Sukces: zielony wynik, `variant_id` równe `43552694304950`, `currency` równe `EUR`, dodatnia cena. Ten test sprawdza dostęp sklepu **z serwera GitHuba**.
3. Ponownie **Run workflow**, tym razem **mode: test**. Sukces: zielony wynik oraz wiadomość `TEST OMTech K40: Telegram działa` w Twoim Telegramie. Test nie zapisuje fikcyjnej ceny.
4. Ponownie **Run workflow**, wybierz **mode: check**. Sukces: powstają `data/store.json` i `data/price_history.csv`; dostajesz wiadomość uruchomienia z ceną. Jeśli już spełniony jest próg 650 EUR, dostaniesz zamiast niej alert cenowy.
5. Uruchom `check` ponownie. Przy tej samej cenie nie powinno być drugiego alertu; w CSV powinien pojawić się drugi pomiar.
6. Harmonogram działa automatycznie: `17 */2 * * *`, czyli o minucie 17 co drugą godzinę UTC. W Polsce zimą to ok. 01:17, 03:17 itd., latem ok. 02:17, 04:17 itd.
7. Po kilku godzinach sprawdź, czy pojawiło się uruchomienie z przyczyną **schedule** oraz kolejny wiersz historii. Dopiero to potwierdza automatyczną pracę.

GitHub może opóźnić lub pominąć uruchomienie. To harmonogram orientacyjny, bez gwarancji dokładnie 120 minut. Bot zapisuje rzeczywisty czas pomiaru w UTC i nie wymyśla odczytów z pominiętych godzin.

## 9. Jak zmienić cenę alarmową

1. **Code → config.json → ikona ołówka**.
2. Zmień tylko wartość w `"target_price_eur": "650"`, np. na `"600"` albo `"649.99"`. Zostaw cudzysłowy i poprawne przecinki JSON.
3. Kliknij **Commit changes**, zapisz do `main`.
4. Uruchom `check` ręcznie lub poczekaj na harmonogram. Jeśli zmieniony próg jest spełniony, bot wyśle alert.

Aby wyłączyć próg kwotowy, wpisz `"target_price_eur": ""`. Reguła spadku 5% nadal działa. `price_drop_percent` domyślnie wynosi `"5"`; nie trzeba go zmieniać.

Zasady alertów:

- 800 → 760 EUR: alert, bo spadek wynosi dokładnie 5%.
- 800 → 770 → 740 EUR: bez alertu procentowego, bo żaden pojedynczy spadek nie osiąga 5%. Próg 650 EUR jest osobnym warunkiem.
- Stała cena poniżej progu: jeden alert. Dalsza niższa cena poniżej progu: nowy alert. Sam wzrost nadal poniżej progu nie alarmuje.
- Powrót ceny ponad próg, a potem ponowne zejście do niego: nowy alert.
- Powrót dostępności przy cenie spełniającej próg: nowy alert.
- Spadek co najmniej 5% powoduje alert także przy niedostępności, z wyraźnym statusem **Niedostępny**. Bot monitoruje każdą taką obniżkę.
- Cena przekreślona przez sklep nie jest podstawą alertu. Pierwszy odczyt nie udaje obniżki względem nieznanej poprzedniej ceny.

## 10. Historia i bieżący stan

Otwórz **Code → data → price_history.csv**. Każdy wiersz oznacza udaną kontrolę: czas UTC, wariant, cena EUR, waluta, dostępność. Dla czasu polskiego dodaj 1 godzinę zimą lub 2 latem.

Możesz kliknąć **Download raw file**, zapisać CSV i otworzyć w Excelu przez **Dane → Z tekstu/CSV**, wybierając separator przecinek i kodowanie UTF-8. Ceny mają kropkę dziesiętną. **History** przy pliku pokazuje wcześniejsze wersje.

`data/store.json` jest głównym źródłem danych. Zawiera te same pomiary i kolejkę alertów. Statusy wiadomości: `pending` — oczekuje, `sent` — potwierdzona, `uncertain` — wynik nieznany. Nie usuwaj go do codziennej obsługi bota.

## 11. Problemy i odzyskiwanie

| Objaw | Co zrobić |
|---|---|
| Czerwony wynik | Actions → dane uruchomienie → monitor → czerwony krok. Przeczytaj komunikat. |
| Brak sekretów | Dodaj dwie wartości z punktu 6 i ponów `test`. |
| Telegram 400/401/403 | Sprawdź token, Chat ID, kliknij Start u bota, odblokuj bota. Popraw Secrets i ponów `test`, potem `check`. |
| OMTech 403/404, HTML zamiast JSON, brak wariantu | Brak zapisu błędnej ceny i brak nowego alertu. Sprawdź produkt ręcznie. Przy trwałej zmianie sklepu trzeba poprawić odczyt. Nie obchodź blokady. |
| Błąd sieci / 429 | Bot ponawia tylko przejściowe odczyty GET, najwyżej 3 razy; długie Retry-After respektuje, kończąc bieżącą kontrolę. Następny harmonogram spróbuje ponownie. |
| Git push odrzucony | Sprawdź uprawnienia, ochronę gałęzi i limity. Nie usuwaj historii. W podsumowaniu błędnego uruchomienia, w **Artifacts**, pobierz `omtech-recovery-...` w ciągu 7 dni. |
| Uszkodzone store.json | Przywróć ostatnią poprawną wersję obu plików `data/` z historii Git. Bot celowo nie zeruje uszkodzonego stanu. |
| Długo brak automatycznych kontroli | Sprawdź Actions, limity i komunikaty o wyłączeniu harmonogramu. Włącz workflow i uruchom `check`. |

**Nieznany wynik Telegrama (`uncertain`):** sprawdź wiadomość na Telegramie po jej ID. Jeśli już dotarła: **Run workflow → mode: acknowledge**, w **alert_id** wklej ID z wiadomości lub `data/store.json`. To oznaczy ją jako odebraną bez ponownej wysyłki. Jeśli nie dotarła: **mode: retry** świadomie ponowi wszystkie niepewne wiadomości. Zwykłe `check` nie ponawia niepewnej wiadomości, ale nadal zapisuje nowe pomiary i może dostarczać nowe alerty. `retry` może wygenerować duplikat, jeśli pierwotna wiadomość jednak dotarła.

Stan jest utrwalany przed wysyłką i po niej. Nie ma jednak transakcji obejmującej jednocześnie GitHub i Telegram. Jeśli serwer zostanie przerwany po wysłaniu wiadomości, ale przed zapisem potwierdzenia w Git, możliwy jest duplikat przy kolejnym uruchomieniu. Każda wiadomość ma ID, co pomaga go rozpoznać. Nie da się uczciwie zagwarantować dostarczenia dokładnie raz przez samo Telegram `sendMessage`.

Jeśli zapis po wysyłce zawiedzie, **przed kolejnym `check` wstrzymaj workflow** i odzyskaj `store.json` oraz CSV z artefaktu tego uruchomienia. Porównaj daty i przywróć oba pliki razem, zanim wznowisz. Równoczesne modyfikacje danych wymagają scalenia; nie nadpisuj nowszej historii starszą kopią. Automatyczne zapisy nie używają force-push.

## 12. Jak zatrzymać i wznowić

1. **Actions → Monitor OMTech K40 → menu ⋯ → Disable workflow**.
2. Jeśli kontrola właśnie działa, otwórz ją i wybierz **Cancel workflow**. Anulowanie podczas wysyłki może pozostawić nieznany wynik — sprawdź czat i stan.
3. Historia pozostaje w repozytorium. Nie trzeba usuwać bota Telegram ani sekretów.
4. Aby wznowić: **Enable workflow**, następnie ręcznie `check`. Po przerwie porównanie odbywa się z ostatnią poprawną ceną sprzed przerwy.

## Koszty i ograniczenia

Projekt nie potrzebuje płatnych usług ani stale włączonego PC. Dla prywatnego repozytorium Actions zużywa bezpłatną pulę planu; inne Twoje projekty również mogą ją zużywać. Orientacyjnie to 360–372 krótkie kontrole miesięcznie, ale nie jest to gwarancja zmieszczenia się w limicie. W ustawieniach konta sprawdź **Billing and licensing / Billing and plans → Usage / Budgets and alerts**. Nie włączaj płatnego przekroczenia limitu. Projekt nie aktywuje płatności. Artefakty są tworzone tylko po awarii i wygasają po 7 dniach; trwała historia jest w Git.

W publicznych repozytoriach standardowe runnery Actions są bezpłatne, lecz kod i historia byłyby widoczne publicznie. Zalecane jest prywatne repozytorium. GitHub opisuje także automatyczne wyłączanie harmonogramów publicznych repozytoriów po 60 dniach braku aktywności. Regularnie kontroluj, czy harmonogram działa; sam kod nie gwarantuje ciągłości usługi.

Monitorowana jest cena wariantu udostępniona przez niemiecki sklep, bez kuponów, rabatów koszykowych, kosztów dostawy i zmian podatku wynikających z polskiego adresu. `available` oznacza możliwość zakupu według danych sklepu, nie liczbę sztuk ani gwarantowany termin dostawy. Zmiany API, geolokalizacja serwera i blokady mogą wymagać aktualizacji.

## Dla osoby technicznej

```sh
python -m unittest discover -s tests -v
python monitor.py --mode fetch
```

Tryb `fetch` jest tylko do odczytu, nie potrzebuje sekretów. Tryby `collect`, `deliver`, `test`, `retry` i `acknowledge` wymagają zmiennych środowiskowych Telegrama. W automatyzacji należy zachować kolejność: `collect` → `scripts/persist.py` → `deliver` → `scripts/persist.py`. Nie uruchamiaj wielu lokalnych procesów na tym samym katalogu danych; GitHub ma wspólną grupę `concurrency`.

## Źródła techniczne

- [Produkt OMTech](https://de.omtech.com/products/k40-lasercutter-graviermaschine?variant=43552694304950)
- [Publiczny endpoint produktu](https://de.omtech.com/products/k40-lasercutter-graviermaschine.js)
- [Shopify Ajax Product API — ceny i waluta](https://shopify.dev/docs/api/ajax/reference/product)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [GitHub — harmonogramy, opóźnienia, 60 dni](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [GitHub — rozliczanie Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
