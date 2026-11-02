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
    "micro_arena_pixel_brawlers.html": (
        "#arenaCanvas",
        "#btnStartGame",
        "#menuOverlay",
        False,
        None,
    ),
    "index.html": (
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

    def test_homepage_discreet_game_catalog_link_opens_play_page(self):
        page, errors = self.open_page("index.html")
        try:
            self.assertIn("Cienie Korony", page.title())
            self.assertEqual(page.locator("#choices-box").count(), 1)
            catalog_link = page.locator(".games-link")
            self.assertEqual(catalog_link.get_attribute("href"), "./play.html")
            self.assertEqual(
                catalog_link.evaluate("(element) => getComputedStyle(element).opacity"),
                "0.14",
            )

            with page.expect_navigation(wait_until="load"):
                catalog_link.click()

            self.assertIn("Salon Kasztanowych Gier", page.title())
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_play_catalog_lists_every_game_and_random_selects_each_tile(self):
        page, errors = self.open_page("play.html")
        try:
            tiles = page.locator("#gamesGrid .game-tile")
            hrefs = tiles.evaluate_all(
                "(elements) => elements.map((element) => new URL(element.href).pathname.split('/').pop())"
            )
            expected_games = sorted(
                path.name
                for path in ROOT.glob("*.html")
                if path.name not in {"index.html", "play.html"}
            )
            self.assertEqual(sorted(hrefs), expected_games)
            self.assertEqual(int(page.locator("#gameCount").inner_text()), len(hrefs))

            for index, href in enumerate(hrefs):
                page.evaluate(
                    "(value) => { Math.random = () => value; }",
                    (index + 0.1) / len(hrefs),
                )
                page.locator("#pickRandomBtn").click()
                self.assertEqual(
                    page.locator("#selectedTitle").evaluate(
                        "(element) => new URL(element.href).pathname.split('/').pop()"
                    ),
                    href,
                    f"Random selection did not include {href}",
                )

            self.assertEqual(errors, [])
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
