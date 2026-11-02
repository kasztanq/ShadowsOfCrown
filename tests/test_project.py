from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
GAME_PAGES = sorted(ROOT.glob("*.html"))
SITE_PAGES = GAME_PAGES
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
MODULE_CONTRACTS = {
    "chestnut_arcade_game_hub.html": (
        'id="hubView"',
        'id="gamesGrid"',
        "launchRandomGame",
    ),
    "chestnut_arcade_game_hub_v2.html": ("id=\"mainMenuView\"", "returnToMenu"),
    "autumn_neon_chestnut_2p_arcade_hub.html": ("id=\"hub-view\"", "startGame(gameId)"),
    "grinch_chest_conquest.html": ("id=\"hub-view\"", "class GrinchConquestApp"),
    "miami_77_v2.html": ('id="gameCanvas"', 'id="startGameBtn"', "function gameLoop"),
    "KasztanoweOczko.html": ('id="bankrollDisplay"', "function startRound"),
    "kasztanix_kasztanowy_tetris.html": ('id="tetris-canvas"', 'id="start-btn"'),
    "kasztanowy_pasjans.html": ('id="stockStack"', "class SolitaireEngine"),
    "chestnut_combat.html": ('id="gameCanvas"', "class ChestnutCombatEngine"),
    "chestnut_strike.html": ('id="gameCanvas"', "class GameEngine"),
    "smerfastyczny_labirynt.html": ('id="gameCanvas"', "function generateMazeLevel", "function triggerVictoryModal"),
    "chess_nuts.html": ("id=\"chessboard\"", "Chess-Nuts"),
    "logopedia.html": ("id=\"interaction-area\"", "function switchMode", "function resetTask"),
    "kraina_wyraznej_mowy.html": ("id=\"view-dashboard\"", "function navigateTo"),
    "kasztanowa_obrona_stanowiska.html": (
        'id="gameCanvas"',
        'id="stat-lives"',
        "function gameLoop",
    ),
    "miami_77.html": ('id="gameCanvas"', 'id="startGameBtn"', "function gameLoop"),
    "mizia.html": ('id="gameCanvas"', 'id="btnPlayCampaign"'),
    "mizia_halloween.html": ('id="gameCanvas"', 'id="btnPlayCampaign"'),
    "play.html": ('id="gamesGrid"', "function selectGame(game)"),
    "roadtomerge.html": ('id="gameCanvas"', 'id="btnPlayGame"', "function gameLoop"),
    "index.html": ('id="game-frame"', 'id="choices-box"'),
    "micro_arena_pixel_brawlers.html": (
        'id="arenaCanvas"',
        'id="menuOverlay"',
        'id="btnStartGame"',
        "class GameEngine",
    ),
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = Counter()
        self.ids = []
        self.links = []
        self.handlers = []
        self.inline_scripts = []
        self.markup_errors = []
        self.open_elements = []
        self.home_links = 0
        self._current_script = None

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        attributes = dict(attrs)

        if tag not in VOID_ELEMENTS:
            self.open_elements.append((tag, self.getpos()[0]))

        if "id" in attributes:
            self.ids.append(attributes["id"])

        if tag == "a" and attributes.get("href") == "./index.html":
            if attributes.get("aria-label", "").strip():
                self.home_links += 1

        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)
            if name.startswith("on") and value:
                self.handlers.append((name, value))

        if tag == "script" and "src" not in attributes:
            self._current_script = []
            self.inline_scripts.append(self._current_script)

    def handle_data(self, data):
        if self._current_script is not None:
            self._current_script.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self._current_script = None
        if tag in VOID_ELEMENTS:
            return
        if not self.open_elements:
            self.markup_errors.append(
                f"Line {self.getpos()[0]}: unexpected closing tag </{tag}>"
            )
        elif self.open_elements[-1][0] != tag:
            open_tag, open_line = self.open_elements[-1]
            self.markup_errors.append(
                f"Line {self.getpos()[0]}: </{tag}> closes while "
                f"<{open_tag}> from line {open_line} is open"
            )
        else:
            self.open_elements.pop()


def parse_page(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


class ProjectPagesTests(unittest.TestCase):
    def test_all_site_pages_have_balanced_html_tags(self):
        for path in SITE_PAGES:
            with self.subTest(page=path.name):
                parser = parse_page(path)
                errors = parser.markup_errors + [
                    f"Unclosed <{tag}> from line {line}"
                    for tag, line in parser.open_elements
                ]
                self.assertEqual(errors, [])

    def test_all_game_pages_have_document_structure_and_inline_logic(self):
        for path in GAME_PAGES:
            with self.subTest(page=path.name):
                parser = parse_page(path)
                self.assertEqual(parser.tags["html"], 1)
                self.assertEqual(parser.tags["head"], 1)
                self.assertEqual(parser.tags["body"], 1)
                self.assertTrue(
                    any("".join(script).strip() for script in parser.inline_scripts),
                    "Expected an inline application script",
                )

    def test_each_game_module_exposes_its_expected_entry_points(self):
        self.assertEqual({path.name for path in GAME_PAGES}, set(MODULE_CONTRACTS))

        for filename, markers in MODULE_CONTRACTS.items():
            contents = (ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(module=filename):
                for marker in markers:
                    self.assertIn(marker, contents)

    def test_inline_event_handlers_reference_application_code(self):
        for path in GAME_PAGES:
            parser = parse_page(path)
            script = "\n".join(
                "".join(block) for block in parser.inline_scripts
            )

            for event, handler in parser.handlers:
                call = re.match(
                    r"\s*(?:[A-Za-z_$][\w$]*\.)?([A-Za-z_$][\w$]*)\s*\(",
                    handler,
                )
                with self.subTest(page=path.name, event=event, handler=handler):
                    self.assertIsNotNone(call, "Expected a JavaScript callback")
                    self.assertRegex(
                        script,
                        rf"\b{re.escape(call.group(1))}\s*\(",
                        "Expected the callback to be implemented in an inline script",
                    )

    def test_all_site_pages_have_unique_ids(self):
        for path in SITE_PAGES:
            with self.subTest(page=path.name):
                ids = parse_page(path).ids
                duplicates = sorted(
                    identifier
                    for identifier, count in Counter(ids).items()
                    if count > 1
                )
                self.assertEqual(duplicates, [])

    def test_all_local_links_and_assets_resolve(self):
        for path in SITE_PAGES:
            for reference in parse_page(path).links:
                parsed = urlsplit(reference)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue

                with self.subTest(page=path.name, reference=reference):
                    target = (path.parent / parsed.path).resolve()
                    self.assertTrue(target.is_file(), f"Missing local target: {target}")

    def test_every_game_page_has_an_accessible_home_link(self):
        for path in GAME_PAGES:
            if path.name == "index.html":
                continue
            with self.subTest(page=path.name):
                parser = parse_page(path)
                self.assertGreater(
                    parser.home_links,
                    0,
                    f"{path.stem}: missing accessible home page link",
                )

    def test_homepage_is_cienie_korony_with_discreet_game_catalog_link(self):
        parser = parse_page(ROOT / "index.html")
        contents = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("<title>Cienie Korony", contents)
        self.assertIn('id="game-frame"', contents)
        self.assertIn('id="choices-box"', contents)
        self.assertIn(
            '<a class="icon-btn games-link" href="./play.html" '
            'aria-label="Otwórz ukryty katalog gier" title="Katalog gier">🎮</a>',
            contents,
        )
        self.assertIn(".games-link { opacity: 0.14; }", contents)
        self.assertIn(".games-link:hover, .games-link:focus-visible { opacity: 1; }", contents)
        self.assertEqual(
            sum(reference == "./play.html" for reference in parser.links),
            1,
        )

    def test_play_catalog_lists_every_game_page(self):
        parser = parse_page(ROOT / "play.html")
        catalog_games = {
            Path(urlsplit(reference).path).name
            for reference in parser.links
            if urlsplit(reference).path.lower().endswith(".html")
            and Path(urlsplit(reference).path).name not in {"index.html", "play.html"}
        }
        expected_games = {
            path.name for path in GAME_PAGES if path.name not in {"index.html", "play.html"}
        }

        self.assertEqual(catalog_games, expected_games)


if __name__ == "__main__":
    unittest.main()
