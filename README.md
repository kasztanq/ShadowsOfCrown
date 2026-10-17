\# Repozytorium zawiera hobbistyczny zestaw gier: Chestnut Arcade Game Hub (Snake i space impact) oraz Cienie Korony (Shadows of the Crown) w wersji mobilnej i desktopowej



# Chestnut Arcade Game Hub 🌰🚀



A retro dual-game HTML5 arcade cabinet built entirely with vanilla JavaScript, HTML5 Canvas, and the Web Audio API.



Included Games



Chestnut Snake: A classic grid-based snake game set in an autumn forest. Collect glossy chestnuts (and golden bonuses) bursting from spiky burrs to grow longer and scale up your speed.



Space Chestnut: A Nokia Space Impact-inspired horizontal space shooter. Pilot the Chestnut Starfighter, blast alien bugs and space squirrels, destroy rotating burr-asteroids, and defeat multi-phase cosmic bosses using spinning mini-chestnut projectiles.



Features



Zero External Dependencies: Self-contained single-file architecture running in any modern browser.



Synth Audio: Retro arpeggios, laser pew-pews, and explosion sounds synthesized on the fly via the Web Audio API.



Responsive Controls: Supports keyboard (WASD / Arrows / Space), mobile touch D-pads, and an auto-fire toggle.



Persistent High Scores: LocalStorage integration to save your high scores across sessions.






# Cienie Korony (Shadows of the Crown)



\*Cienie Korony\* to turowa gra strategiczno-narracyjna osadzona w średniowiecznym dworze, opierająca się na mechanikach intryg, zdrady, szantażu i zarządzania wpływami. Gra czerpie inspirację z tytułów takich jak \*Reigns\* oraz \*Crusader Kings\*.



\## 👑 Rola Gracza

Wcielasz się w postać szarej eminencji lub podupadłego szlachcica, który potajemnie pociąga za sznurki za tronem słabego monarchy. Twoim zadaniem jest utrzymanie równowagi między frakcjami dworskimi przy jednoczesnym knuciu spisków i eliminowaniu rywali.



\---



\## 🛠️ Wymagania techniczne

\* \*\*Silnik:\*\* Godot Engine 4.2+ (zalecany renderer: \*\*Mobile\*\*)

\* \*\*Platforma docelowa:\*\* Android (orientacja pionowa / Portrait)



\---



\## 📁 Struktura Projektu



Projekt opiera się na dynamicznym systemie wczytywania danych z plików JSON oraz modułowej architekturze interfejsu:



```text

res://

├── data/

│   ├── characters.json     # Baza postaci dworskich, statystyki i sekrety

│   ├── intrigues.json      # Wieloetapowe drzewa spisków i operacji

│   └── events.json         # Karty dylematów i wydarzeń dworskich

├── scripts/

│   ├── game\_controller.gd         # Główny kontroler rozgrywki, HUD i animacje Tween

│   └── spy\_operations\_modal.gd    # Siatka szpiegów, czarny rynek i zamachy

└── README.md

🚀 Instrukcja uruchomienia i wdrożenia

1\. Klonowanie / Pobranie projektu

Pobierz lub sklonuj repozytorium do wybranego folderu na swoim komputerze.



2\. Otwarcie w Godot Engine 4

Uruchom Godot Engine 4.



Kliknij Import i wybierz plik project.godot z folderu projektu.



Otwórz projekt w edytorze.



3\. Ustawienie ekranu mobilnego (Portrait)

Upewnij się, że projekt jest skonfigurowany pod ekrany smartfonów:



Wejdź w Project -> Project Settings -> Display -> Window.



Ustaw rozdzielczość: Width: 720, Height: 1280.



Ustaw Orientation: Portrait oraz tryb dopasowania (Stretch Mode: canvas\_items, Aspect: expand).



4\. Testowanie gry

Naciśnij klawisz F5 w edytorze Godot, aby uruchomić główną scenę gry.



📱 Eksport do pliku .APK (Android)

Zainstaluj Android SDK oraz OpenJDK 17 zgodnie z oficjalnym podręcznikiem Godota.



W Godocie przejdź do Project -> Export.



Dodaj profil Android, zaznacz architekturę arm64-v8a oraz uprawnienie do wibracji (Vibrate).



Kliknij Export Project i wskaż ścieżkę do zapisu pliku .apk.



📜 Licencja

Projekt stworzony do celów edukacyjnych i hobbystycznych. Możesz go dowolnie modyfikować i rozwijać.

