# Repozytorium zawiera hobbistyczny zestaw gier: Chestnut Arcade Game Hub (Snake, space impact, bomberman and tanks) oraz Cienie Korony (Shadows of the Crown) w wersji webowej.

## Pliki gry

* [chestnut\_arcade\_game\_hub.html](./chestnut_arcade_game_hub.html) — centrum gier arcade z 4 mini-grami: Snake, Space Impact, Tanks i Bomberman.
* [ShadowsOfCrown.html](./ShadowsOfCrown.html) — strategiczno-narracyjna gra w stylu dworskiego intryganta.

# Chestnut Arcade Game Hub 🌰🚀

A retro hub-game HTML5 arcade cabinet built entirely with vanilla JavaScript, HTML5 Canvas, and the Web Audio API.

## Included Games

###### Cartridge #01 — Chestnut Snake:



* Slither across a 32×20 autumn forest grid using WASD or Arrow Keys.



* Collect glossy chestnuts with spiky green husks to grow longer and faster, with Golden Bonus Chestnuts (+30 pts) spawning every 5th pickup.



###### Cartridge #02 — Space Chestnut:



* A Nokia Space Impact-inspired horizontal shoot-'em-up where you pilot the Chestnut Starfighter and fire spinning little chestnuts (Spacebar or Auto-Fire).



* Structured 4-Sector Progression: Battle through 3 distinct waves (Wave X-1, Wave X-2, Wave X-3) with 2.5-second breather transitions before facing each Sector's unique Boss (Wave X-BOSS):



* Sector 1 (Deep Autumn Orbit) — Boss: Cosmic Burr-Titan (3-way seed spreads + timed Burr-Mines).



* Sector 2 (Crimson Sap Nebula) — Boss: Mecha-Squirrel Dreadnought (lane dashes + twin lasers + homing Squirrel Drones).



* Sector 3 (Golden Harvest Belt) — Boss: Queen Autumn Moth (figure-8 flight + crescent blades + telegraphed Solar Sap Beam).



* Sector 4+ (Omega Cyber-Void) — Boss: Omega Chestnut Core (protected by 3 Orbiting Husk Shield Nodes + spiral bullet rings).



* Power-Up Capsules: Collect \[WPN+] (4 weapon tiers up to Quad + Homing Micro-Nuts), \[SHD] (Spiky Burr Shield), \[+1 HP] (Hull Repair), and \[NOVA] (Super Chestnut Nova Bomb via E or B).



###### Cartridge #03 — Chestnut Tanks:



* A Battle City-inspired 21×13 top-down tank arena (38px tiles) with a forgiving 26×26 tank hitbox, smooth corner-sliding, and a guaranteed clear perimeter around the Golden Chestnut Base (cols baseCol-5..baseCol+5, rows ROWS-3..ROWS-1) so tanks never get boxed in on the left or right side of the base.



* Features 6 distinct Level Biomes \& Wall Blueprints (Autumn Woodland Glade, Crimson Canyon Quarry, Iron Husk Citadel Boss Arena, Frost-Pine Tundra, Golden Amber Stronghold, and Volcanic Ember Forge), plus Burr Shields (SHD), Rapid Nut Cannons (SPD), and Base Fortify kits (FIX).



###### Cartridge #04 — Chestnut Bomberman ("Bomber-Nut"):



* A 17×11 grid action-maze game where you plant ticking Spiky Chestnut Bombs (Spacebar) that detonate in cross-shaped burr blasts.
* Features 6 unique Stage Biomes \& Indestructible Pillar Layouts (Mossy Forest Clearing, Twilight Mushroom Cavern, King Burr-Golem's Amber Throne Boss Ring, Frosted Birch Ruins, Sunken Root Labyrinth, and Volcanic Cinder Pit), a guaranteed clear spawn corner, crate upgrades (+1 Bomb, +1 Blast Range, Speed Boots), and the King Burr-Golem Boss every 3rd stage.
Features
* Zero external dependencies: Self-contained single-file architecture running in any modern browser.
* Synth audio: Retro arpeggios, laser pew-pews, and explosion sounds synthesized on the fly via the Web Audio API.
* Responsive controls: Supports keyboard (WASD / Arrows / Space), mobile touch D-pads, and an auto-fire toggle.
* Persistent high scores: LocalStorage integration to save your high scores across sessions.

* 

# Cienie Korony (Shadows of the Crown)

*Cienie Korony* to turowa gra strategiczno-narracyjna osadzona na średniowiecznym dworze. Jako dworski intrygant podejmujesz decyzje w kartach wydarzeń, dbasz o wpływy wśród króla, Kościoła i szlachty, a za kulisami budujesz siatkę szpiegowską i przygotowujesz drogę do tronu.

## 👑 Rozgrywka

* Podejmuj decyzje w kolejnych wydarzeniach dworskich. Każdy wybór wpływa na relacje z królem, Kościołem i szlachtą oraz na poziom podejrzeń.
* Zdobywaj złoto i haki (tajne informacje), awansuj od Szeptacza Dworskiego do Szarej Eminencji i rozwijaj swoje wpływy.
* Zarządzaj agentami i zasobami: rekrutuj szpiegów, infiltruj archiwum, kupuj truciznę, przekupuj strażników lub zlecaj zamachy na rywali.
* Zrealizuj cztery etapy Wielkiego Spisku, by przejąć koronę. Wysokie podejrzenia albo utrata poparcia króla, Kościoła lub szlachty kończą grę.

## 🛠️ Wymagania i uruchomienie

Obie gry są samodzielnymi plikami HTML, które zawierają interfejs i kod gry. Nie wymagają silnika, instalacji ani zewnętrznych bibliotek.

1. Pobierz lub sklonuj repozytorium.
2. Otwórz odpowiedni plik w nowoczesnej przeglądarce:

   * [chestnut\_arcade\_game\_hub.html](./chestnut_arcade_game_hub.html) — hub z arcade mini-grami,
   * [ShadowsOfCrown.html](./ShadowsOfCrown.html) — gra strategiczna.
3. Gra działa na komputerach i urządzeniach mobilnych. Postęp jest zapisywany lokalnie w pamięci przeglądarki; przycisk nowej gry rozpoczyna rozgrywkę od początku.

Interfejs zawiera również syntetyzowane efekty dźwiękowe, które można wyciszyć w grze.

## 📜 Licencja

Projekt stworzony do celów edukacyjnych i hobbystycznych. Możesz go dowolnie modyfikować i rozwijać.

