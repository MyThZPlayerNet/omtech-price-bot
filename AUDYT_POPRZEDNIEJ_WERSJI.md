# Analiza poprzedniej paczki

Przeanalizowano wszystkie pliki `omtech-price-bot.zip`: monitor, testy, README, ignorowane pliki i workflow. Archiwum nie zawierało tokenów Telegrama. Treść dokumentacji potraktowano jako opis poprzedniej implementacji, a wymagania z rozmowy jako właściwą specyfikację.

Zachowano pomysł Pythona bez dodatkowych bibliotek, wyboru wariantu po ID, publicznego API Shopify i zapisu danych w Git. Przebudowano logikę i obsługę trwałości.

| Poprzednio | Obecnie |
|---|---|
| Spadek względem najwyższej ceny od uruchomienia | Spadek względem ostatniej poprawnej obserwacji |
| Dodatkowy warunek ceny przekreślonej, niezamówiony w specyfikacji | Cena przekreślona nie uruchamia alarmu |
| Dalszy alert przy spadku 2% od poprzedniego alertu | Każdy spadek co najmniej 5% względem poprzedniego pomiaru; osobny próg kwotowy |
| EUR zapisane na stałe, bez potwierdzenia sesji | Potwierdzenie EUR przez cart.js we wspólnej sesji |
| Dopuszczenie zaokrąglania wadliwej ceny | Wymagane dodatnie całkowite centy w odpowiedzi .js |
| Automatyczny fallback .json z innymi jednostkami | Jeden sprawdzony endpoint .js; zmiana struktury kończy kontrolę błędem |
| Historia tylko przy zmianie ceny | Historia każdego poprawnego sprawdzenia, także dostępności |
| Wysyłka przed zapisem, utrata obserwacji przy błędzie Telegrama | Obserwacja i kolejka zapisywane przed wysyłką |
| Brak zapisu stanu po błędzie wysyłki | Osobny krok zapisu po dostarczaniu, także przy błędzie |
| Brak rozróżnienia nieznanego wyniku POST | Stan uncertain; brak automatycznego ponowienia niepewnej wiadomości |
| Proste git push | Wspólna grupa concurrency, zapis przed/po wysyłce, bezpieczny rebase, bez force-push, kopia ratunkowa po awarii |
| Token w adresie przeglądarki przy getUpdates | Lokalny pomocnik PowerShell z ukrytym wpisywaniem tokenu |
| Brak potwierdzonego odczytu sklepu | Rzeczywisty odczyt wariantu i waluty; wynik w verification/ |

Nie ma obietnicy stuprocentowej dostępności GitHub Actions ani dostarczenia dokładnie raz pomiędzy dwoma niezależnymi usługami. Granice trwałości i odzyskiwanie opisano w README.

SHA-256 źródłowego ZIP-a: `4613a02594f07d89780a81417f0fc686685b006030b6ddde83ce8205722df8c6`.
