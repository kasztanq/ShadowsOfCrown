from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
GAME_PAGES = sorted(ROOT.glob("*.html"))
SITE_PAGES = [ROOT / "index.htm", *GAME_PAGES]
MODULE_CONTRACTS = {
    "chestnut_arcade_game_hub.html": (
        'id="hubView"',
        'id="gamesGrid"',
        "launchRandomGame",
    ),
    "chestnut_arcade_game_hub_v2.html": ("id=\"mainMenuView\"", "returnToMenu"),
    "autumn_neon_chestnut_2p_arcade_hub.html": ("id=\"hub-view\"", "startGame(gameId)"),
    "grinch_chest_conquest.html": ("id=\"hub-view\"", "class GrinchConquestApp"),
    "chess_nuts.html": ("id=\"chessboard\"", "Chess-Nuts"),
    "logopedia.html": ("id=\"interaction-area\"", "function switchMode", "function resetTask"),
    "kraina_wyraznej_mowy.html": ("id=\"view-dashboard\"", "function navigateTo"),
    "ShadowsOfCrown.html": ('id="game-frame"', 'id="choices-box"'),
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = Counter()
        self.ids = []
        self.links = []
        self.handlers = []
        self.inline_scripts = []
        self._current_script = None

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        attributes = dict(attrs)

        if "id" in attributes:
            self.ids.append(attributes["id"])

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


def parse_page(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


class ProjectPagesTests(unittest.TestCase):
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

    def test_every_game_page_has_an_english_home_icon(self):
        for path in GAME_PAGES:
            with self.subTest(page=path.name):
                contents = path.read_text(encoding="utf-8")
                parser = parse_page(path)
                self.assertIn('aria-label="Back to home"', contents)
                self.assertIn("./index.htm", parser.links)

    def test_homepage_has_a_discreet_chess_nuts_easter_egg(self):
        parser = parse_page(ROOT / "index.htm")
        contents = (ROOT / "index.htm").read_text(encoding="utf-8")

        self.assertEqual(contents.count('class="orbit-nut"'), 7)
        self.assertIn('class="hero-caption"', contents)
        self.assertIn('class="chess-egg" href="./chess_nuts.html"', contents)
        self.assertNotIn("Chess-Nuts</span>", contents)
        self.assertEqual(
            sum(reference == "./chess_nuts.html" for reference in parser.links),
            1,
        )

    def test_arcade_cabinet_one_describes_the_current_hub(self):
        contents = (ROOT / "index.htm").read_text(encoding="utf-8")
        cabinet = contents.split('id="arcade"', maxsplit=1)[1].split(
            "</article>", maxsplit=1
        )[0]

        self.assertIn("10 arcade games", cabinet)
        self.assertIn("Golden chestnuts", cabinet)
        self.assertIn("./chestnut_arcade_game_hub.html", cabinet)


if __name__ == "__main__":
    unittest.main()
