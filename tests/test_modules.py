from pathlib import Path
import unittest

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
MODULES = {
    "autumn_neon_chestnut_2p_arcade_hub.html": (
        "#hub-view",
        'button:has-text("Launch Chestnut Jump")',
        "#game-view",
        True,
        None,
    ),
    "chess_nuts.html": (
        "#chessboard",
        "#info-modal-btn",
        "#guide-modal",
        True,
        None,
    ),
    "chestnut_arcade_game_hub.html": (
        "#hubView",
        'button:has-text("SURPRISE ME")',
        "#cabinetView",
        True,
        None,
    ),
    "chestnut_arcade_game_hub_v2.html": (
        "#mainMenuView",
        'button:has-text("PLAY CHESTNUT SNAKE")',
        "#gameCabinetView",
        True,
        None,
    ),
    "grinch_chest_conquest.html": (
        "#hub-view",
        'button[onclick*="launchGame(\'chestpac\')"]',
        "#game-view",
        True,
        None,
    ),
    "kraina_wyraznej_mowy.html": (
        "#view-dashboard",
        'button[onclick="openWarmupModal()"]',
        "#warmupModal",
        True,
        None,
    ),
    "logopedia.html": (
        "#interaction-area",
        ".tabs button:nth-child(2)",
        "#mode-title",
        True,
        "Budowniczy Słów",
    ),
    "miami_77.html": (
        "#gameCanvas",
        "#startGameBtn",
        "#startModal",
        False,
        None,
    ),
    "ShadowsOfCrown.html": (
        "#choices-box",
        ".bottom-nav button",
        "#spy-modal",
        True,
        None,
    ),
    "smerfastyczny_labirynt.html": (
        "#gameCanvas",
        "#btn-levels",
        "#modal-levels",
        True,
        None,
    ),
}


class GameModuleBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def open_page(self, filename):
        page = self.browser.new_page()
        page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.url.startswith(("http://", "https://"))
            else route.continue_(),
        )
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((ROOT / filename).as_uri(), wait_until="load")
        # Tailwind is blocked for offline, deterministic tests.
        page.add_style_tag(content=".hidden { display: none !important; }")
        return page, errors

    def test_every_game_module_starts_without_uncaught_javascript_errors(self):
        for filename in MODULES:
            with self.subTest(module=filename):
                page, errors = self.open_page(filename)
                try:
                    page.wait_for_timeout(250)
                    self.assertEqual(
                        errors,
                        [],
                        f"Uncaught JavaScript errors during startup: {errors}",
                    )
                finally:
                    page.close()

    def test_every_game_module_loads_and_handles_a_primary_action(self):
        for filename, (
            surface_selector,
            action_selector,
            result_selector,
            result_visible,
            expected_text,
        ) in MODULES.items():
            with self.subTest(module=filename):
                page, errors = self.open_page(filename)
                try:
                    self.assertGreater(
                        page.locator(surface_selector).count(),
                        0,
                        f"Missing application surface {surface_selector}",
                    )

                    action = page.locator(action_selector).first
                    self.assertTrue(action.is_visible(), f"Missing action {action_selector}")
                    action.click()
                    page.wait_for_timeout(100)

                    result = page.locator(result_selector)
                    self.assertEqual(
                        result.is_visible(),
                        result_visible,
                        f"Unexpected state for {result_selector}",
                    )
                    if expected_text:
                        self.assertIn(expected_text, result.inner_text())

                    self.assertEqual(
                        errors,
                        [],
                        f"Uncaught JavaScript errors after action: {errors}",
                    )
                finally:
                    page.close()

    def test_homepage_hidden_miami_link_opens_the_game(self):
        page, errors = self.open_page("index.htm")
        try:
            link = page.locator(".miami-egg")
            self.assertEqual(link.get_attribute("href"), "./miami_77.html")
            self.assertEqual(link.evaluate("(element) => getComputedStyle(element).opacity"), "0")

            with page.expect_navigation(wait_until="load"):
                link.click(force=True)

            self.assertIn("MIAMI '77", page.title())
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_homepage_hidden_new_game_links_open_the_games(self):
        hidden_games = (
            (".oczko-egg", "./KasztanoweOczko.html", "Kasztanowe Oczko"),
            (
                ".tetris-egg",
                "./kasztanix_kasztanowy_tetris.html",
                "Kasztanix - Kasztanowy Tetris 3000",
            ),
            (".pasjans-egg", "./kasztanowy_pasjans.html", "Kasztanowy Pasjans"),
            (".combat-egg", "./chestnut_combat.html", "CHESTNUT COMBAT"),
            (".strike-egg", "./chestnut_strike.html", "CHESTNUT STRIKE"),
        )
        for selector, href, title in hidden_games:
            with self.subTest(game=href):
                page, errors = self.open_page("index.htm")
                try:
                    link = page.locator(selector)
                    self.assertEqual(link.get_attribute("href"), href)
                    self.assertEqual(
                        link.evaluate(
                            "(element) => getComputedStyle(element).opacity"
                        ),
                        "0",
                    )

                    with page.expect_navigation(wait_until="load"):
                        link.click(force=True)

                    self.assertIn(title, page.title())
                    self.assertEqual(errors, [])
                finally:
                    page.close()


if __name__ == "__main__":
    unittest.main()
