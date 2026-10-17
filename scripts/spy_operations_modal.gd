class_name SpyOperationsModal
extends Control

signal operation_completed(gold_delta: int, suspicion_delta: int, message: String)

@onready var sheet_container: PanelContainer = $SheetContainer
@onready var dimmer_background: ColorRect = $DimmerBackground
@onready var dynamic_content: VBoxContainer = $SheetContainer/MarginContainer/VBoxContainer/ContentScroll/DynamicContentVBox
@onready var status_label: Label = $SheetContainer/MarginContainer/VBoxContainer/StatusBar/StatusLabel

# Referencja do kontrolera gry (do weryfikacji złota i podejrzeń)
var game_controller: GameController

# Baza przedmiotów i operacji
var inventory: Dictionary = {
	"tojad": 0,           # Trucizna
	"sztylet_cienia": 0,  # Broń zamachowca
	"falszywa_pieczec": 0 # Podrzucanie dowodów
}

var spies_count: int = 1
var max_spies: int = 3

var targets: Array[Dictionary] = [
	{
		"id": "char_marshal_vane",
		"name": "Lord Gerard Vane (Marszałek)",
		"guard_level": "Wysoka (Ochrona gwardii)",
		"base_success": 0.50,
		"risk_suspicion": 35
	},
	{
		"id": "char_bishop_anselm",
		"name": "Biskup Anselm",
		"guard_level": "Średnia (Katedra)",
		"base_success": 0.70,
		"risk_suspicion": 25
	}
]

func _ready() -> void:
	visible = false
	dimmer_background.modulate.a = 0.0
	_connect_navigation()


func _connect_navigation() -> void:
	$SheetContainer/MarginContainer/VBoxContainer/HeaderHBox/CloseButton.pressed.connect(close_panel)
	$SheetContainer/MarginContainer/VBoxContainer/TabsHBox/TabSpiesBtn.pressed.connect(func(): show_tab("spies"))
	$SheetContainer/MarginContainer/VBoxContainer/TabsHBox/TabMarketBtn.pressed.connect(func(): show_tab("market"))
	$SheetContainer/MarginContainer/VBoxContainer/TabsHBox/TabAssassinationsBtn.pressed.connect(func(): show_tab("assassinations"))


# --- OTWIERANIE / ZAMYKANIE Z ANIMACJĄ NA TELEFONIE ---
func open_panel(controller: GameController) -> void:
	game_controller = controller
	visible = true
	update_status_bar()
	show_tab("spies")
	
	# Animacja wsuwania od dołu
	var screen_height = get_viewport_rect().size.y
	sheet_container.position.y = screen_height
	
	var tween = create_tween().set_parallel(true).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(dimmer_background, "modulate:a", 1.0, 0.25)
	tween.tween_property(sheet_container, "position:y", screen_height - sheet_container.size.y, 0.3)


func close_panel() -> void:
	var screen_height = get_viewport_rect().size.y
	var tween = create_tween().set_parallel(true).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_property(dimmer_background, "modulate:a", 0.0, 0.2)
	tween.tween_property(sheet_container, "position:y", screen_height, 0.25)
	tween.finished.connect(func(): visible = false)


func update_status_bar() -> void:
	status_label.text = "Złoto: %d | Szpiedzy: %d/%d | Tojad: %d | Sztylety: %d" % [
		game_controller.gold, spies_count, max_spies, inventory["tojad"], inventory["sztylet_cienia"]
	]


# --- RENDEROWANIE ZAKŁADEK ---
func _clear_content() -> void:
	for child in dynamic_content.get_children():
		child.queue_free()


func show_tab(tab_name: String) -> void:
	_clear_content()
	match tab_name:
		"spies":
			_render_spies_tab()
		"market":
			_render_market_tab()
		"assassinations":
			_render_assassinations_tab()


# --- 1. ZAKŁADKA AGENTÓW ---
func _render_spies_tab() -> void:
	var recruit_card = _create_card("Zwerbuj Nowego Szpiega", "Koszt: 75 Złota. Pozwala inwigilować dworzan.")
	var btn_recruit = Button.new()
	btn_recruit.text = "Zwerbuj szpiega (-75g)"
	btn_recruit.disabled = (game_controller.gold < 75 or spies_count >= max_spies)
	btn_recruit.pressed.connect(func():
		if game_controller.gold >= 75 and spies_count < max_spies:
			game_controller.gold -= 75
			spies_count += 1
			_haptic()
			update_status_bar()
			_render_spies_tab()
	)
	recruit_card.add_child(btn_recruit)
	dynamic_content.add_child(recruit_card)

	# Misje szpiegowskie
	var mission_card = _create_card("Infiltracja Kancelarii Królewskiej", "Zdobywa kompromaty i haki na dworzan. Ryzyko wpadki: Niskie.")
	var btn_mission = Button.new()
	btn_mission.text = "Wyślij agenta (-25g, +5 Podejrzeń)"
	btn_mission.disabled = (game_controller.gold < 25 or spies_count <= 0)
	btn_mission.pressed.connect(func():
		_execute_mission(25, 5, "Twój agent zdobył prywatną korespondencję kanclerza!", "token_intel")
	)
	mission_card.add_child(btn_mission)
	dynamic_content.add_child(mission_card)


# --- 2. ZAKŁADKA CZARNEGO RYNKU (TRUCIZNY I PRZEDMIOTY) ---
func _render_market_tab() -> void:
	_create_market_item("Wywar z Tojadu (Wilcze Łyko)", "Subtelna trucizna. Zwiększa szansę udanego zamachu o 30%.", 60, "tojad")
	_create_market_item("Cichy Sztylet z Toledo", "Narzędzie skrytobójcy. Pozwala zorganizować napad na trakcie.", 45, "sztylet_cienia")
	_create_market_item("Sfałszowana Pieczęć Królewska", "Pozwala podłożyć fałszywy rozkaz w archiwum.", 80, "falszywa_pieczec")


func _create_market_item(title: String, desc: String, price: int, item_key: String) -> void:
	var item_card = _create_card(title, desc + "\nPosiadane: " + str(inventory[item_key]))
	var btn = Button.new()
	btn.text = "Kup za %d Złota" % price
	btn.disabled = (game_controller.gold < price)
	btn.pressed.connect(func():
		if game_controller.gold >= price:
			game_controller.gold -= price
			inventory[item_key] += 1
			_haptic()
			update_status_bar()
			show_tab("market")
	)
	item_card.add_child(btn)
	dynamic_content.add_child(item_card)


# --- 3. ZAKŁADKA ZAMACHÓW (ZLECENIA ZABÓJSTW) ---
func _render_assassinations_tab() -> void:
	for target in targets:
		var has_poison = inventory["tojad"] > 0
		var calculated_chance = target["base_success"] + (0.30 if has_poison else 0.0)
		calculated_chance = clamp(calculated_chance, 0.05, 0.95)
		
		var desc = "Ochrona: %s\nSzansa powodzenia: %d%%\nRyzyko podejrzeń: +%d" % [
			target["guard_level"], int(calculated_chance * 100), target["risk_suspicion"]
		]
		if has_poison:
			desc += "\n[color=green]Aktywny bonus: Trucizna tojad (+30% szans)[/color]"

		var card = _create_card("Cel: " + target["name"], desc)
		
		var btn = Button.new()
		btn.text = "Zleć morderstwo (Koszty: 1 Szpieg, 100g)"
		btn.disabled = (game_controller.gold < 100 or spies_count <= 0)
		btn.pressed.connect(func():
			_execute_assassination(target, calculated_chance, has_poison)
		)
		card.add_child(btn)
		dynamic_content.add_child(card)


func _execute_assassination(target: Dictionary, chance: float, used_poison: bool) -> void:
	game_controller.gold -= 100
	if used_poison:
		inventory["tojad"] -= 1

	var roll = randf()
	if roll <= chance:
		# Sukces eliminacji
		_haptic(100)
		game_controller.stats["suspicion"] += int(target["risk_suspicion"] * 0.4) # Częściowe podejrzenia
		targets.erase(target)
		_show_feedback_modal("Zamach udany!", target["name"] + " nie żyje. Dwór pogrążył się w chaosie.")
	else:
		# Porażka – wpadka siatki
		_haptic(250)
		spies_count = max(0, spies_count - 1)
		game_controller.stats["suspicion"] += target["risk_suspicion"]
		_show_feedback_modal("ZAMACH ZDEMASKOWANY!", "Twój zamachowiec został pojmany na gorącym uczynku i zeznaje na torturach!")

	game_controller.update_all_meters(true)
	update_status_bar()
	show_tab("assassinations")


# --- METODY POMOCNICZE I UI ---
func _create_card(title: String, body_text: String) -> PanelContainer:
	var panel = PanelContainer.new()
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)

	var title_lbl = Label.new()
	title_lbl.text = title
	title_lbl.add_theme_font_size_override("font_size", 16)

	var desc_lbl = RichTextLabel.new()
	desc_lbl.bbcode_enabled = true
	desc_lbl.text = body_text
	desc_lbl.fit_content = true
	desc_lbl.scroll_active = false

	vbox.add_child(title_lbl)
	vbox.add_child(desc_lbl)
	panel.add_child(vbox)
	return panel


func _execute_mission(cost: int, suspicion_gain: int, success_msg: String, reward_token: String) -> void:
	game_controller.gold -= cost
	game_controller.stats["suspicion"] += suspicion_gain
	if not game_controller.active_tokens.has(reward_token):
		game_controller.active_tokens.append(reward_token)
	
	_haptic(40)
	game_controller.update_all_meters(true)
	update_status_bar()
	_show_feedback_modal("Raport Agenta", success_msg)
	show_tab("spies")


func _show_feedback_modal(title: String, message: String) -> void:
	var dialog = AcceptDialog.new()
	dialog.title = title
	dialog.dialog_text = message
	add_child(dialog)
	dialog.popup_centered()


func _haptic(duration_ms: int = 40) -> void:
	if OS.has_feature("mobile"):
		Input.vibrate_handheld(duration_ms)