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

    def test_miami_v2_mission_markers_activate_and_mission_cars_respawn(self):
        page, errors = self.open_page("miami_77_v2.html")
        try:
            page.locator("#startGameBtn").click()
            result = page.evaluate(
                """() => {
                    const story = gameState.mainStory;
                    story.actIndex = 1;
                    story.started = true;
                    story.completed = false;
                    startMainStoryAct();
                    const pickups = story.pickups;
                    const pickupMarkersReachable = pickups.every(
                        point => !isPointInBuilding(point.x, point.y, 13)
                    );
                    for (const pickup of pickups) {
                        player.x = pickup.x;
                        player.y = pickup.y;
                        updateMainStory(0.016);
                    }
                    const storyPickupsActivated =
                        story.actIndex === 2 && pickups.every(pickup => pickup.collected);

                    story.started = false;
                    player.inCar = null;
                    const booth = gameState.phoneBooths.find(item => item.id === 'grinch_hq');
                    gameState.pendingMissionChallenge =
                        MAFIA_MISSION_CHALLENGES.find(item => item.id === 'smuggle');
                    gameState.missionChallengeDeck = ['smuggle'];
                    startMissionFromBooth(booth);
                    const delivery = gameState.activeMission;
                    player.x = delivery.packagePoint.x;
                    player.y = delivery.packagePoint.y;
                    updateGame(0.016);
                    const deliveryMarkerActivated = delivery.packageDelivered;
                    player.x = delivery.dropOff.x;
                    player.y = delivery.dropOff.y;
                    updateGame(0.016);
                    const deliveryCompleted = gameState.activeMission === null;

                    const missionMarkerReachability = {};
                    for (const challenge of MAFIA_MISSION_CHALLENGES) {
                        if (gameState.activeMission) {
                            gameState.activeMission.targetCars.forEach(car => {
                                const index = gameState.cars.indexOf(car);
                                if (index >= 0) gameState.cars.splice(index, 1);
                            });
                            gameState.activeMission.targetPeds.forEach(ped => {
                                const index = gameState.peds.indexOf(ped);
                                if (index >= 0) gameState.peds.splice(index, 1);
                            });
                        }
                        gameState.activeMission = null;
                        gameState.pendingMissionChallenge = challenge;
                        gameState.missionChallengeDeck = [challenge.id];
                        startMissionFromBooth(booth);
                        const mission = gameState.activeMission;
                        const markers = [
                            { x: mission.targetX, y: mission.targetY },
                            ...mission.targetCars,
                            ...mission.targetPeds,
                            ...mission.checkpoints,
                            mission.packagePoint,
                            mission.dropOff,
                            mission.home,
                            mission.escapePoint,
                            mission.targetShop?.marker
                        ].filter(Boolean);
                        missionMarkerReachability[challenge.id] = markers.length > 0 &&
                            markers.every(marker =>
                                Number.isFinite(marker.x) &&
                                Number.isFinite(marker.y) &&
                                marker.x >= 0 &&
                                marker.x <= WORLD_SIZE &&
                                marker.y >= 0 &&
                                marker.y <= WORLD_SIZE &&
                                !isPointInBuilding(marker.x, marker.y, 13)
                            );
                    }

                    const respawns = [];
                    for (const challengeId of ['gold_limo', 'funk_van', 'v8_speed']) {
                        if (gameState.activeMission) {
                            gameState.activeMission.targetCars.forEach(car => {
                                const index = gameState.cars.indexOf(car);
                                if (index >= 0) gameState.cars.splice(index, 1);
                            });
                            gameState.activeMission.targetPeds.forEach(ped => {
                                const index = gameState.peds.indexOf(ped);
                                if (index >= 0) gameState.peds.splice(index, 1);
                            });
                        }
                        gameState.activeMission = null;
                        gameState.pendingMissionChallenge =
                            MAFIA_MISSION_CHALLENGES.find(item => item.id === challengeId);
                        gameState.missionChallengeDeck = [challengeId];
                        startMissionFromBooth(booth);
                        const mission = gameState.activeMission;
                        const wreck = mission.targetCar;
                        const oldPosition = { x: wreck.x, y: wreck.y };
                        player.inCar = wreck;
                        damageCar(wreck, wreck.maxHp + 1, true);
                        respawns.push({
                            active: gameState.activeMission === mission,
                            replaced: mission.targetCar !== wreck,
                            moved: Math.hypot(
                                mission.targetCar.x - oldPosition.x,
                                mission.targetCar.y - oldPosition.y
                            ) >= BLOCK_SIZE,
                            playerSurvived: !gameState.isGameOver && player.inCar === null
                        });
                    }

                    gameState.activeMission = null;
                    player.inCar = null;
                    story.actIndex = 3;
                    story.started = true;
                    startMainStoryAct();
                    const surveillanceWreck = story.targetCar;
                    const surveillanceOrigin = { x: surveillanceWreck.x, y: surveillanceWreck.y };
                    damageCar(surveillanceWreck, surveillanceWreck.maxHp + 1, true);
                    const storyCarRespawned =
                        story.targetCar !== surveillanceWreck &&
                        Math.hypot(
                            story.targetCar.x - surveillanceOrigin.x,
                            story.targetCar.y - surveillanceOrigin.y
                        ) >= BLOCK_SIZE;

                    return {
                        pickupMarkersReachable,
                        storyPickupsActivated,
                        deliveryMarkerActivated,
                        deliveryCompleted,
                        missionMarkerReachability,
                        respawns,
                        storyCarRespawned
                    };
                }"""
            )
            self.assertTrue(result["pickupMarkersReachable"])
            self.assertTrue(result["storyPickupsActivated"])
            self.assertTrue(result["deliveryMarkerActivated"])
            self.assertTrue(result["deliveryCompleted"])
            self.assertTrue(result["storyCarRespawned"])
            self.assertTrue(all(result["missionMarkerReachability"].values()))
            self.assertEqual(len(result["respawns"]), 3)
            for respawn in result["respawns"]:
                with self.subTest(respawn=respawn):
                    self.assertTrue(respawn["active"])
                    self.assertTrue(respawn["replaced"])
                    self.assertTrue(respawn["moved"])
                    self.assertTrue(respawn["playerSurvived"])
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_miami_v2_v8_marker_identifies_and_tracks_the_v8(self):
        page, errors = self.open_page("miami_77_v2.html")
        try:
            page.locator("#startGameBtn").click()
            marker = page.evaluate(
                """() => {
                    gameState.started = true;
                    const booth = gameState.phoneBooths.find(item => item.id === 'phone_chestnuts');
                    const challenge = MAFIA_MISSION_CHALLENGES.find(item => item.id === 'v8_speed');
                    gameState.pendingMissionChallenge = challenge;
                    gameState.missionChallengeDeck = [challenge.id];
                    startMissionFromBooth(booth);
                    const mission = gameState.activeMission;
                    updateGame(0.016);

                    const labels = [];
                    const originalFillText = ctx.fillText.bind(ctx);
                    ctx.fillText = (text, ...args) => {
                        labels.push(String(text));
                        originalFillText(text, ...args);
                    };
                    renderGame();
                    ctx.fillText = originalFillText;

                    return {
                        active: gameState.activeMission === mission,
                        targetIsSpawned: gameState.cars.includes(mission.targetCar),
                        isV8: mission.targetCar.model.name.includes('V8'),
                        markerTracksCar:
                            mission.targetX === mission.targetCar.x &&
                            mission.targetY === mission.targetCar.y,
                        label: labels.includes('V8 • CEL MISJI')
                    };
                }"""
            )
            self.assertEqual(
                marker,
                {
                    "active": True,
                    "targetIsSpawned": True,
                    "isV8": True,
                    "markerTracksCar": True,
                    "label": True,
                },
            )
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_miami_v2_mario_escort_marks_mario_and_the_hideout(self):
        page, errors = self.open_page("miami_77_v2.html")
        try:
            page.locator("#startGameBtn").click()
            markers = page.evaluate(
                """() => {
                    gameState.started = true;
                    const booth = gameState.phoneBooths.find(item => item.id === 'phone_chestnuts');
                    const challenge = MAFIA_MISSION_CHALLENGES.find(item => item.id === 'escort_mario');
                    gameState.pendingMissionChallenge = challenge;
                    gameState.missionChallengeDeck = [challenge.id];
                    startMissionFromBooth(booth);
                    const mission = gameState.activeMission;
                    const witness = mission.targetPed;
                    updateGame(0.016);

                    const labels = [];
                    const originalFillText = ctx.fillText.bind(ctx);
                    ctx.fillText = (text, x, y, ...args) => {
                        labels.push({ text: String(text), x, y });
                        originalFillText(text, x, y, ...args);
                    };
                    renderGame();
                    ctx.fillText = originalFillText;

                    return {
                        marioMarked: witness.isMissionMario &&
                            labels.some(label =>
                                label.text === 'MARIO' &&
                                Math.abs(label.x - witness.x) < 1 &&
                                Math.abs(label.y - (witness.y - 31)) < 1
                            ),
                        hideoutMarked: labels.some(label =>
                            label.text === 'KRYJÓWKA' &&
                            Math.abs(label.x - mission.home.x) < 1 &&
                            Math.abs(label.y - (mission.home.y - 41)) < 1
                        ),
                        objectiveNamesBoth: mission.desc.includes('Mario') &&
                            mission.desc.includes('kryjówki'),
                        markerPointsToHideout:
                            mission.targetX === mission.home.x &&
                            mission.targetY === mission.home.y,
                        marioStartsOnScreen:
                            witness.x >= player.x - canvas.width / 2 &&
                            witness.x <= player.x + canvas.width / 2 &&
                            witness.y >= player.y - canvas.height / 2 &&
                            witness.y <= player.y + canvas.height / 2
                    };
                }"""
            )
            self.assertEqual(
                markers,
                {
                    "marioMarked": True,
                    "hideoutMarked": True,
                    "objectiveNamesBoth": True,
                    "markerPointsToHideout": True,
                    "marioStartsOnScreen": True,
                },
            )
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_miami_v2_alive_mission_guards_return_after_player_death(self):
        page, errors = self.open_page("miami_77_v2.html")
        try:
            page.locator("#startGameBtn").click()
            result = page.evaluate(
                """() => {
                    gameState.started = true;
                    const booth = gameState.phoneBooths.find(item => item.id === 'phone_weasels');
                    const challenge = MAFIA_MISSION_CHALLENGES.find(item => item.id === 'debt_gang');
                    gameState.pendingMissionChallenge = challenge;
                    gameState.missionChallengeDeck = [challenge.id];
                    startMissionFromBooth(booth);
                    const mission = gameState.activeMission;
                    const survivingGuard = mission.targetPeds[0];
                    const defeatedGuard = mission.targetPeds[1];
                    killPedestrian(gameState.peds.indexOf(defeatedGuard));
                    gameState.peds = [survivingGuard];

                    triggerGameOver('test');
                    document.getElementById('restartGameBtn').click();

                    return {
                        missionStillActive: gameState.activeMission === mission,
                        survivorRestored: gameState.peds.includes(survivingGuard),
                        survivorStillMarked: survivingGuard.isMissionTarget,
                        defeatedGuardNotRestored: !gameState.peds.includes(defeatedGuard),
                        remainingTargetCount: mission.targetPeds.filter(
                            ped => gameState.peds.includes(ped)
                        ).length
                    };
                }"""
            )
            self.assertEqual(
                result,
                {
                    "missionStillActive": True,
                    "survivorRestored": True,
                    "survivorStillMarked": True,
                    "defeatedGuardNotRestored": True,
                    "remainingTargetCount": 3,
                },
            )
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_miami_v2_can_enter_car_near_booth_during_active_mission(self):
        page, errors = self.open_page("miami_77_v2.html")
        try:
            page.locator("#startGameBtn").click()
            result = page.evaluate(
                """() => {
                    gameState.started = true;
                    const booth = gameState.phoneBooths.find(item => item.id === 'phone_chestnuts');
                    player.x = booth.x;
                    player.y = booth.y;
                    const car = createCar(
                        booth.x + 35,
                        booth.y,
                        0,
                        CAR_MODELS_70S.find(model => model.id === 'muscle'),
                        '#f97316'
                    );
                    gameState.cars.push(car);

                    gameState.pendingMissionChallenge =
                        MAFIA_MISSION_CHALLENGES.find(item => item.id === 'v8_speed');
                    gameState.missionChallengeDeck = ['v8_speed'];
                    startMissionFromBooth(booth);
                    document.getElementById('dialogueModal').classList.add('hidden');

                    handleContextAction();

                    return {
                        enteredVehicle: player.inCar === car,
                        missionStillActive: gameState.activeMission?.challengeId === 'v8_speed',
                        dialogueStayedClosed:
                            document.getElementById('dialogueModal').classList.contains('hidden')
                    };
                }"""
            )
            self.assertEqual(
                result,
                {
                    "enteredVehicle": True,
                    "missionStillActive": True,
                    "dialogueStayedClosed": True,
                },
            )
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_every_miami_v2_faction_mission_can_be_completed(self):
        page, errors = self.open_page("miami_77_v2.html")
        try:
            page.locator("#startGameBtn").click()
            completed = page.evaluate(
                """() => {
                    gameState.started = true;
                    gameState.isGameOver = false;
                    gameState.mainStory.started = false;
                    const booth = gameState.phoneBooths.find(item => item.id === 'grinch_hq');
                    let previousMission = null;
                    const results = {};

                    for (const challenge of MAFIA_MISSION_CHALLENGES) {
                        if (previousMission) {
                            previousMission.targetCars.forEach(car => {
                                const index = gameState.cars.indexOf(car);
                                if (index >= 0) gameState.cars.splice(index, 1);
                            });
                            previousMission.targetPeds.forEach(ped => {
                                const index = gameState.peds.indexOf(ped);
                                if (index >= 0) gameState.peds.splice(index, 1);
                            });
                        }
                        player.inCar = null;
                        gameState.wantedLevel = 0;
                        gameState.wantedDecayTimer = 0;
                        gameState.pendingMissionChallenge = challenge;
                        gameState.missionChallengeDeck = [challenge.id];
                        startMissionFromBooth(booth);
                        const mission = gameState.activeMission;

                        if (challenge.id === 'smuggle' || challenge.id === 'express_delivery') {
                            player.x = mission.packagePoint.x;
                            player.y = mission.packagePoint.y;
                            updateGame(0.016);
                            player.x = mission.dropOff.x;
                            player.y = mission.dropOff.y;
                            updateGame(0.016);
                        } else if (challenge.id === 'armored_van') {
                            damageCar(mission.targetCar, mission.targetCar.maxHp + 1, true);
                            updateGame(0.016);
                        } else if (challenge.id === 'escort_mario') {
                            mission.targetPed.speed = 0;
                            mission.targetPed.x = mission.home.x;
                            mission.targetPed.y = mission.home.y;
                            player.x = mission.home.x;
                            player.y = mission.home.y;
                            updateGame(0.016);
                        } else if (challenge.id === 'gold_limo' || challenge.id === 'funk_van') {
                            const car = mission.targetCar;
                            car.aiState = 'parked';
                            player.inCar = car;
                            player.x = car.x;
                            player.y = car.y;
                            updateGame(0.016);
                            car.x = mission.dropOff.x;
                            car.y = mission.dropOff.y;
                            player.x = car.x;
                            player.y = car.y;
                            updateGame(0.016);
                        } else if (challenge.id === 'spy_hunt') {
                            const index = gameState.peds.indexOf(mission.targetPed);
                            if (index >= 0) gameState.peds.splice(index, 1);
                            updateGame(0.016);
                        } else if (challenge.id === 'police_surveillance') {
                            for (const checkpoint of mission.checkpoints) {
                                player.x = checkpoint.x;
                                player.y = checkpoint.y;
                                updateGame(0.016);
                            }
                        } else if (challenge.id === 'froggy_robbery') {
                            mission.targetShop.robberyCooldown = 0;
                            player.x = mission.targetShop.marker.x;
                            player.y = mission.targetShop.marker.y;
                            robFroggyShop(mission.targetShop);
                            gameState.wantedLevel = 0;
                            player.x = mission.escapePoint.x;
                            player.y = mission.escapePoint.y;
                            updateGame(0.016);
                        } else if (challenge.id === 'debt_gang') {
                            mission.targetPeds.forEach(ped => {
                                const index = gameState.peds.indexOf(ped);
                                if (index >= 0) gameState.peds.splice(index, 1);
                            });
                            updateGame(0.016);
                        } else if (challenge.id === 'v8_speed') {
                            const car = mission.targetCar;
                            car.aiState = 'player_controlled';
                            car.vx = 300;
                            car.angle = 0;
                            player.inCar = car;
                            mission.progress = 9.99;
                            updateGame(0.02);
                        } else if (challenge.id === 'rival_demolition') {
                            mission.targetCars.forEach(car => { car.hp = 0; });
                            mission.targetPeds.forEach(ped => {
                                const index = gameState.peds.indexOf(ped);
                                if (index >= 0) gameState.peds.splice(index, 1);
                            });
                            updateGame(0.016);
                        }

                        results[challenge.id] = gameState.activeMission === null;
                        previousMission = mission;
                        player.inCar = null;
                    }
                    return results;
                }"""
            )
            self.assertEqual(set(completed), {challenge["id"] for challenge in page.evaluate(
                "() => MAFIA_MISSION_CHALLENGES.map(challenge => ({id: challenge.id}))"
            )})
            self.assertTrue(
                all(completed.values()),
                f"Faction mission could not complete: {completed}",
            )
            self.assertEqual(errors, [])
        finally:
            page.close()

    def test_miami_v2_full_mission_campaign_survives_death(self):
        page, errors = self.open_page("miami_77_v2.html")
        try:
            page.locator("#startGameBtn").click()
            results = page.evaluate(
                """() => {
                    gameState.started = true;
                    gameState.isGameOver = false;
                    gameState.mainStory.started = false;
                    const challenges = MAFIA_MISSION_CHALLENGES;
                    const booths = {
                        chestnuts: gameState.phoneBooths.find(item => item.id === 'phone_chestnuts'),
                        rhavens: gameState.phoneBooths.find(item => item.id === 'phone_rhavens'),
                        magicians: gameState.phoneBooths.find(item => item.id === 'phone_magicians'),
                        weasels: gameState.phoneBooths.find(item => item.id === 'phone_weasels')
                    };
                    const schedule = [
                        ...challenges.slice(0, 5).map(challenge => ({ challenge, faction: 'chestnuts' })),
                        ...challenges.slice(5, 10).map(challenge => ({ challenge, faction: 'rhavens' })),
                        ...[...challenges.slice(10), ...challenges.slice(0, 3)]
                            .map(challenge => ({ challenge, faction: 'magicians' })),
                        ...challenges.slice(2, 7).map(challenge => ({ challenge, faction: 'weasels' }))
                    ];
                    const campaign = {};
                    let previousMission = null;

                    const killTargetPed = ped => {
                        const index = gameState.peds.indexOf(ped);
                        if (index >= 0) killPedestrian(index);
                    };
                    const setOnlyMissionTargets = mission => {
                        gameState.peds = mission.targetPeds.filter(ped => ped.hp > 0);
                        gameState.cars = mission.targetCars.filter(car => car.hp > 0);
                    };
                    const completeMission = mission => {
                        const id = mission.challengeId;
                        if (id === 'smuggle' || id === 'express_delivery') {
                            player.inCar = null;
                            player.x = mission.packagePoint.x;
                            player.y = mission.packagePoint.y;
                            updateGame(0.016);
                            player.x = mission.dropOff.x;
                            player.y = mission.dropOff.y;
                            updateGame(0.016);
                        } else if (id === 'armored_van') {
                            damageCar(mission.targetCar, mission.targetCar.hp + 1);
                            updateGame(0.016);
                        } else if (id === 'escort_mario') {
                            mission.targetPed.speed = 0;
                            mission.targetPed.x = mission.home.x;
                            mission.targetPed.y = mission.home.y;
                            player.x = mission.home.x;
                            player.y = mission.home.y;
                            updateGame(0.016);
                        } else if (id === 'gold_limo' || id === 'funk_van') {
                            const car = mission.targetCar;
                            car.aiState = 'parked';
                            player.inCar = car;
                            player.x = car.x;
                            player.y = car.y;
                            updateGame(0.016);
                            car.x = mission.dropOff.x;
                            car.y = mission.dropOff.y;
                            player.x = car.x;
                            player.y = car.y;
                            updateGame(0.016);
                        } else if (id === 'spy_hunt') {
                            killTargetPed(mission.targetPed);
                            updateGame(0.016);
                        } else if (id === 'police_surveillance') {
                            while (mission.checkpointIndex < mission.checkpoints.length) {
                                const checkpoint = mission.checkpoints[mission.checkpointIndex];
                                player.x = checkpoint.x;
                                player.y = checkpoint.y;
                                updateGame(0.016);
                            }
                        } else if (id === 'froggy_robbery') {
                            gameState.wantedLevel = 0;
                            player.x = mission.escapePoint.x;
                            player.y = mission.escapePoint.y;
                            updateGame(0.016);
                        } else if (id === 'debt_gang') {
                            [...mission.targetPeds].forEach(killTargetPed);
                            updateGame(0.016);
                        } else if (id === 'v8_speed') {
                            const car = mission.targetCar;
                            car.aiState = 'player_controlled';
                            car.vx = 300;
                            car.angle = 0;
                            player.inCar = car;
                            mission.progress = 9.99;
                            updateGame(0.02);
                        } else if (id === 'rival_demolition') {
                            mission.targetCars.forEach(car => {
                                if (car.hp > 0) damageCar(car, car.hp + 1);
                            });
                            [...mission.targetPeds].forEach(killTargetPed);
                            updateGame(0.016);
                        }
                    };

                    for (const { challenge, faction } of schedule) {
                        if (previousMission) {
                            previousMission.targetPeds.forEach(ped => {
                                const index = gameState.peds.indexOf(ped);
                                if (index >= 0) gameState.peds.splice(index, 1);
                            });
                            previousMission.targetCars.forEach(car => {
                                const index = gameState.cars.indexOf(car);
                                if (index >= 0) gameState.cars.splice(index, 1);
                            });
                        }
                        gameState.activeMission = null;
                        gameState.peds = [];
                        gameState.cars = [];
                        gameState.wantedLevel = 0;
                        gameState.health = 100;
                        player.inCar = null;
                        player.x = 2000;
                        player.y = 2000;
                        gameState.pendingMissionChallenge = challenge;
                        gameState.missionChallengeDeck = [challenge.id];
                        startMissionFromBooth(booths[faction]);
                        const mission = gameState.activeMission;
                        setOnlyMissionTargets(mission);

                        if (challenge.id === 'smuggle' || challenge.id === 'express_delivery') {
                            player.x = mission.packagePoint.x;
                            player.y = mission.packagePoint.y;
                            updateGame(0.016);
                        } else if (challenge.id === 'armored_van') {
                            damageCar(mission.targetCar, 20, false);
                        } else if (challenge.id === 'escort_mario') {
                            mission.targetPed.hp -= 10;
                        } else if (challenge.id === 'gold_limo' || challenge.id === 'funk_van') {
                            player.inCar = mission.targetCar;
                            player.x = mission.targetCar.x;
                            player.y = mission.targetCar.y;
                            updateGame(0.016);
                        } else if (challenge.id === 'spy_hunt') {
                            mission.targetPed.hp -= 10;
                        } else if (challenge.id === 'police_surveillance') {
                            const checkpoint = mission.checkpoints[0];
                            player.x = checkpoint.x;
                            player.y = checkpoint.y;
                            updateGame(0.016);
                        } else if (challenge.id === 'froggy_robbery') {
                            mission.targetShop.robberyCooldown = 0;
                            player.x = mission.targetShop.marker.x;
                            player.y = mission.targetShop.marker.y;
                            robFroggyShop(mission.targetShop);
                        } else if (challenge.id === 'debt_gang') {
                            killTargetPed(mission.targetPeds[0]);
                        } else if (challenge.id === 'v8_speed') {
                            mission.progress = 4.5;
                            player.inCar = mission.targetCar;
                        } else if (challenge.id === 'rival_demolition') {
                            damageCar(mission.targetCars[0], mission.targetCars[0].hp + 1);
                            killTargetPed(mission.targetPeds[0]);
                        }

                        gameState.health = 1;
                        damagePlayer(1, `Śmierć podczas misji ${challenge.id}`);
                        document.getElementById('restartGameBtn').click();
                        const survivedRestart = gameState.activeMission === mission &&
                            !gameState.isGameOver &&
                            mission.targetPeds.every(ped =>
                                ped.hp <= 0 || gameState.peds.includes(ped)
                            ) &&
                            mission.targetCars.every(car =>
                                car.hp <= 0 || gameState.cars.includes(car)
                            );
                        const progressPreserved = {
                            smuggle: () => mission.packageDelivered,
                            express_delivery: () => mission.packageDelivered,
                            armored_van: () =>
                                mission.targetCar.hp < mission.targetCar.maxHp,
                            escort_mario: () => mission.targetPed.hp < 130,
                            gold_limo: () => mission.lootCollected,
                            funk_van: () => mission.lootCollected,
                            spy_hunt: () => mission.targetPed.hp < 110,
                            police_surveillance: () => mission.checkpointIndex === 1,
                            froggy_robbery: () => mission.lootCollected,
                            debt_gang: () => mission.targetPeds[0].hp <= 0 &&
                                !gameState.peds.includes(mission.targetPeds[0]),
                            v8_speed: () => mission.progress >= 4.5,
                            rival_demolition: () => mission.targetCars[0].hp <= 0 &&
                                mission.targetPeds[0].hp <= 0 &&
                                !gameState.peds.includes(mission.targetPeds[0])
                        }[challenge.id]();
                        setOnlyMissionTargets(mission);
                        player.inCar = null;
                        gameState.wantedLevel = 0;
                        gameState.health = 100;
                        completeMission(mission);
                        const key = `${faction}:${challenge.id}`;
                        campaign[key] = {
                            resumed: survivedRestart,
                            progressPreserved,
                            completed: gameState.activeMission === null,
                            respect: gameState.respect[faction]
                        };
                        previousMission = mission;
                    }

                    const respectsUnlockedStory = allSyndicatesRespected();
                    if (!respectsUnlockedStory) {
                        return {
                            factionMissionCount: Object.keys(campaign).length,
                            factionMissions: campaign,
                            respectsUnlockedStory,
                            respect: gameState.respect
                        };
                    }
                    startMainStory();
                    const story = gameState.mainStory;
                    const acts = {};
                    const dieAndRestart = () => {
                        const currentAct = story.actIndex;
                        gameState.health = 1;
                        damagePlayer(1, `Śmierć podczas aktu ${currentAct}`);
                        document.getElementById('restartGameBtn').click();
                        return story.started && !story.completed && story.actIndex === currentAct;
                    };
                    const activateNextAct = () => {
                        if (!story.started && !story.completed) startMainStory();
                    };
                    const isolateStoryTargets = () => {
                        gameState.cars = story.targetCars.filter(car => car.hp > 0);
                        gameState.peds = story.targetPeds.filter(ped => ped.hp > 0);
                    };

                    player.x = story.pickups[0].x;
                    player.y = story.pickups[0].y;
                    updateMainStory(0.016);
                    const act1Restarted = dieAndRestart();
                    const act1Reset = story.pickups.every(pickup => !pickup.collected);
                    story.pickups.forEach(pickup => {
                        player.x = pickup.x;
                        player.y = pickup.y;
                        updateMainStory(0.016);
                    });
                    acts.act1 = act1Restarted && act1Reset && story.actIndex === 2;

                    activateNextAct();
                    isolateStoryTargets();
                    let raceCar = story.raceCar;
                    player.inCar = raceCar;
                    player.x = story.checkpoints[0].x;
                    player.y = story.checkpoints[0].y;
                    updateMainStory(0.016);
                    gameState.health = 30;
                    const raceWreck = story.raceCar;
                    player.inCar = raceWreck;
                    damageCar(raceWreck, raceWreck.hp + 1, true);
                    const act2VehicleRecovered = story.raceCar !== raceWreck &&
                        Math.hypot(story.raceCar.x - raceWreck.x, story.raceCar.y - raceWreck.y) >= BLOCK_SIZE &&
                        !gameState.isGameOver && player.inCar === null;
                    const act2Restarted = dieAndRestart();
                    const act2Reset = story.checkpointIndex === 0 &&
                        story.raceCar !== raceCar &&
                        gameState.cars.includes(story.raceCar);
                    isolateStoryTargets();
                    raceCar = story.raceCar;
                    player.inCar = raceCar;
                    for (const checkpoint of story.checkpoints) {
                        player.x = checkpoint.x;
                        player.y = checkpoint.y;
                        updateMainStory(0.016);
                    }
                    acts.act2 = act2VehicleRecovered && act2Restarted &&
                        act2Reset && story.actIndex === 3;

                    activateNextAct();
                    isolateStoryTargets();
                    story.surveillanceProgress = 4;
                    gameState.health = 30;
                    const surveillanceWreck = story.targetCar;
                    player.inCar = surveillanceWreck;
                    damageCar(surveillanceWreck, surveillanceWreck.hp + 1, true);
                    const act3VehicleRecovered = story.targetCar !== surveillanceWreck &&
                        Math.hypot(
                            story.targetCar.x - surveillanceWreck.x,
                            story.targetCar.y - surveillanceWreck.y
                        ) >= BLOCK_SIZE &&
                        !gameState.isGameOver && player.inCar === null;
                    const act3Restarted = dieAndRestart();
                    const act3Reset = story.surveillanceProgress === 0 &&
                        !!story.targetCar && gameState.cars.includes(story.targetCar);
                    isolateStoryTargets();
                    story.targetCar.angle = 0;
                    player.x = story.targetCar.x - 150;
                    player.y = story.targetCar.y;
                    story.surveillanceProgress = 11.99;
                    updateMainStory(0.02);
                    acts.act3 = act3VehicleRecovered && act3Restarted &&
                        act3Reset && story.actIndex === 4;

                    activateNextAct();
                    isolateStoryTargets();
                    let accountant = story.accountant;
                    player.x = accountant.x;
                    player.y = accountant.y;
                    updateMainStory(0.016);
                    const act4Restarted = dieAndRestart();
                    const act4Reset = !story.escortStarted &&
                        story.accountant !== accountant &&
                        gameState.peds.includes(story.accountant);
                    isolateStoryTargets();
                    accountant = story.accountant;
                    player.x = accountant.x;
                    player.y = accountant.y;
                    updateMainStory(0.016);
                    accountant.x = story.hideout.x;
                    accountant.y = story.hideout.y;
                    player.x = story.hideout.x;
                    player.y = story.hideout.y;
                    updateMainStory(0.016);
                    acts.act4 = act4Restarted && act4Reset && story.actIndex === 5;

                    activateNextAct();
                    isolateStoryTargets();
                    killPedestrian(gameState.peds.indexOf(story.targetPeds[0]));
                    const act5Restarted = dieAndRestart();
                    const act5Reset = story.targetPeds.length === 4 &&
                        story.targetPeds.every(ped => gameState.peds.includes(ped));
                    isolateStoryTargets();
                    [...story.targetPeds].forEach(ped =>
                        killPedestrian(gameState.peds.indexOf(ped))
                    );
                    updateMainStory(0.016);
                    acts.act5 = act5Restarted && act5Reset && story.actIndex === 6;

                    activateNextAct();
                    isolateStoryTargets();
                    damageCar(story.targetCar, story.targetCar.hp + 1, true);
                    updateMainStory(0.016);
                    const bossSpawnedBeforeDeath = story.bossSpawned && !!story.grinch;
                    const act6Restarted = dieAndRestart();
                    const act6Reset = !story.bossSpawned && !!story.targetCar &&
                        gameState.cars.includes(story.targetCar);
                    isolateStoryTargets();
                    damageCar(story.targetCar, story.targetCar.hp + 1, true);
                    updateMainStory(0.016);
                    if (story.grinch) {
                        const bossIndex = gameState.peds.indexOf(story.grinch);
                        if (bossIndex >= 0) killPedestrian(bossIndex);
                    }
                    updateMainStory(0.016);
                    acts.act6 = bossSpawnedBeforeDeath && act6Restarted && act6Reset &&
                        story.completed && !gameState.started;

                    return {
                        factionMissionCount: Object.keys(campaign).length,
                        factionMissions: campaign,
                        respectsUnlockedStory,
                        respect: gameState.respect,
                        storyStarted: story.started || story.completed,
                        acts,
                        storyCompleted: story.completed
                    };
                }"""
            )
            self.assertEqual(results["factionMissionCount"], 20)
            self.assertTrue(
                all(case["resumed"] for case in results["factionMissions"].values()),
                f"Faction mission lost targets or progress after death: {results['factionMissions']}",
            )
            self.assertTrue(
                all(case["progressPreserved"] for case in results["factionMissions"].values()),
                f"Faction mission lost partial progress after death: {results['factionMissions']}",
            )
            self.assertTrue(
                all(case["completed"] for case in results["factionMissions"].values()),
                f"Faction mission could not be completed after restart: {results['factionMissions']}",
            )
            self.assertTrue(
                results["respectsUnlockedStory"],
                f"Faction missions did not unlock the story: {results['respect']}",
            )
            self.assertTrue(all(results["acts"].values()), f"Story act failed: {results['acts']}")
            self.assertTrue(results["storyCompleted"], f"Story did not complete: {results}")
            self.assertEqual(errors, [])
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
