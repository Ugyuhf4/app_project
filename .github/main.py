import os
import json
import traceback
from datetime import datetime
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty,
    ListProperty, DictProperty, ObjectProperty
)
from kivy.metrics import dp

# Настройка окна
Window.size = (800, 600)
Window.minimum_width, Window.minimum_height = 400, 300

class SoundManager:
    """Менеджер звуков и музыки"""
    
    def __init__(self):
        self.background_music = None
        self.sounds = {}
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.music_enabled = True
        self.sounds_enabled = True
        
        # Создаем необходимые папки
        self.create_folders()
    
    def create_folders(self):
        """Создание необходимых папок"""
        folders = ['audio', 'characters', 'backgrounds', 'saves']
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    def play_background_music(self, filename, loop=True):
        """Воспроизведение фоновой музыки"""
        try:
            if not self.music_enabled:
                return False
                
            # Останавливаем предыдущую музыку
            if self.background_music:
                self.background_music.stop()
            
            # Полный путь к файлу
            filepath = os.path.join('audio', filename)
            if not os.path.exists(filepath):
                print(f"Файл музыки не найден: {filepath}")
                # Создаем заглушку
                return False
            
            self.background_music = SoundLoader.load(filepath)
            if self.background_music:
                self.background_music.volume = self.music_volume
                self.background_music.loop = loop
                self.background_music.play()
                return True
        except Exception as e:
            print(f"Ошибка воспроизведения музыки: {e}")
        return False
    
    def play_sound(self, filename, volume=None):
        """Воспроизведение звукового эффекта"""
        try:
            if not self.sounds_enabled:
                return False
            
            # Используем громкость по умолчанию если не указана
            if volume is None:
                volume = self.sound_volume
            
            # Полный путь к файлу
            filepath = os.path.join('audio', filename)
            if not os.path.exists(filepath):
                print(f"Файл звука не найден: {filepath}")
                # Просто возвращаем True, чтобы игра продолжалась
                return True
            
            # Загружаем или используем кэшированный звук
            if filename not in self.sounds:
                self.sounds[filename] = SoundLoader.load(filepath)
            
            sound = self.sounds[filename]
            if sound:
                sound.volume = volume
                sound.play()
                return True
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
        return False
    
    def stop_music(self):
        """Остановка музыки"""
        if self.background_music:
            try:
                self.background_music.stop()
            except:
                pass
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop_music()
        for sound in self.sounds.values():
            try:
                sound.stop()
            except:
                pass
        self.sounds.clear()

class VisualNovelGame:
    """Логика визуальной новеллы"""
    
    def __init__(self):
        self.current_scene = "start"
        self.current_dialogue_index = 0
        self.variables = {
            "reputation": 0,      # -100 до 100
            "relationship_alice": 0,  # Отношения с Алисой
            "relationship_bob": 0,    # Отношения с Бобом
            "karma": 50,          # Карма (0-100)
            "money": 100,         # Деньги
            "choices_made": []    # История выбора
        }
        self.dialogue_history = []
        self.game_data = {}
        
        # Загружаем данные игры
        self.load_game_data()
    
    def load_game_data(self):
        """Загрузка данных игры из JSON"""
        try:
            with open('game_data.json', 'r', encoding='utf-8') as f:
                self.game_data = json.load(f)
            print("Данные игры успешно загружены")
        except FileNotFoundError:
            print("Файл game_data.json не найден. Используются данные по умолчанию.")
            self.create_default_data()
        except json.JSONDecodeError as e:
            print(f"Ошибка в формате JSON: {e}. Используются данные по умолчанию.")
            self.create_default_data()
        except Exception as e:
            print(f"Неизвестная ошибка при загрузке: {e}")
            self.create_default_data()
    
    def create_default_data(self):
        """Создание данных по умолчанию"""
        self.game_data = {
            "scenes": {
                "start": {
                    "background": "backgrounds/city.jpg",
                    "music": "ambient_city.mp3",
                    "dialogues": [
                        {
                            "character": "Алиса",
                            "text": "Привет! Рада тебя видеть. Куда направляемся?",
                            "expression": "happy"
                        }
                    ],
                    "choices": [
                        {
                            "text": "Пойдем в парк",
                            "next_scene": "park",
                            "effects": {
                                "relationship_alice": 10,
                                "reputation": 5
                            }
                        },
                        {
                            "text": "Пойдем в кафе",
                            "next_scene": "cafe",
                            "effects": {
                                "relationship_alice": 5,
                                "money": -20
                            }
                        }
                    ]
                },
                "park": {
                    "background": "backgrounds/park.jpg",
                    "music": "ambient_park.mp3",
                    "dialogues": [
                        {
                            "character": "Алиса",
                            "text": "Какой прекрасный день! Давно я не была в парке.",
                            "expression": "happy"
                        },
                        {
                            "character": "Боб",
                            "text": "О, привет! Что вы тут делаете?",
                            "expression": "neutral"
                        }
                    ],
                    "choices": [
                        {
                            "text": "Поздороваться вежливо",
                            "next_scene": "park_friendly",
                            "effects": {
                                "relationship_bob": 10,
                                "reputation": 10
                            }
                        },
                        {
                            "text": "Игнорировать Боба",
                            "next_scene": "park_ignore",
                            "effects": {
                                "relationship_alice": -5,
                                "karma": -10
                            }
                        }
                    ]
                },
                "cafe": {
                    "background": "backgrounds/cafe.jpg",
                    "music": "ambient_cafe.mp3",
                    "dialogues": [
                        {
                            "character": "Алиса",
                            "text": "Люблю этот маленький уютный кофейный магазинчик!",
                            "expression": "happy"
                        }
                    ],
                    "choices": [
                        {
                            "text": "Угостить Алису кофе",
                            "next_scene": "cafe_coffee",
                            "effects": {
                                "relationship_alice": 15,
                                "money": -50
                            }
                        },
                        {
                            "text": "Заказать только себе",
                            "next_scene": "cafe_selfish",
                            "effects": {
                                "relationship_alice": -10,
                                "reputation": -5
                            }
                        }
                    ]
                }
            },
            "characters": {
                "Алиса": {
                    "images": {
                        "happy": "characters/alice_happy.png",
                        "neutral": "characters/alice_neutral.png",
                        "sad": "characters/alice_sad.png"
                    },
                    "color": "#FF6B9D"
                },
                "Боб": {
                    "images": {
                        "happy": "characters/bob_happy.png",
                        "neutral": "characters/bob_neutral.png",
                        "angry": "characters/bob_angry.png"
                    },
                    "color": "#4A90E2"
                }
            }
        }
    
    def get_current_dialogue(self):
        """Получение текущего диалога"""
        scene = self.game_data["scenes"].get(self.current_scene, {})
        dialogues = scene.get("dialogues", [])
        
        if dialogues and self.current_dialogue_index < len(dialogues):
            return dialogues[self.current_dialogue_index]
        return None
    
    def get_choices(self):
        """Получение вариантов выбора для текущей сцены"""
        scene = self.game_data["scenes"].get(self.current_scene, {})
        return scene.get("choices", [])
    
    def next_dialogue(self):
        """Переход к следующему диалогу"""
        scene = self.game_data["scenes"].get(self.current_scene, {})
        dialogues = scene.get("dialogues", [])
        
        if self.current_dialogue_index < len(dialogues) - 1:
            self.current_dialogue_index += 1
            return True
        return False
    
    def make_choice(self, choice_index):
        """Обработка выбора игрока"""
        choices = self.get_choices()
        if choice_index < 0 or choice_index >= len(choices):
            return False
        
        choice = choices[choice_index]
        
        # Сохраняем выбор в историю
        self.dialogue_history.append({
            "scene": self.current_scene,
            "choice": choice["text"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Применяем эффекты выбора
        effects = choice.get("effects", {})
        for key, value in effects.items():
            if key in self.variables:
                # Для некоторых переменных ограничиваем диапазон
                if key in ["reputation", "relationship_alice", "relationship_bob", "karma"]:
                    self.variables[key] = max(-100, min(100, self.variables[key] + value))
                elif key == "money":
                    self.variables[key] = max(0, self.variables[key] + value)
                else:
                    self.variables[key] += value
        
        # Переходим к следующей сцене
        self.current_scene = choice.get("next_scene", self.current_scene)
        self.current_dialogue_index = 0
        
        # Автосохранение
        self.auto_save()
        
        return True
    
    def auto_save(self):
        """Автосохранение игры"""
        try:
            save_data = {
                "current_scene": self.current_scene,
                "current_dialogue_index": self.current_dialogue_index,
                "variables": self.variables,
                "dialogue_history": self.dialogue_history,
                "timestamp": datetime.now().isoformat()
            }
            
            with open('saves/autosave.json', 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка автосохранения: {e}")
    
    def load_save(self, filename="autosave.json"):
        """Загрузка сохранения"""
        try:
            filepath = os.path.join('saves', filename)
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.current_scene = save_data.get("current_scene", "start")
            self.current_dialogue_index = save_data.get("current_dialogue_index", 0)
            self.variables = save_data.get("variables", self.variables.copy())
            self.dialogue_history = save_data.get("dialogue_history", [])
            
            return True
        except Exception as e:
            print(f"Ошибка загрузки сохранения: {e}")
            return False
    
    def reset_game(self):
        """Сброс игры к началу"""
        self.current_scene = "start"
        self.current_dialogue_index = 0
        self.variables = {
            "reputation": 0,
            "relationship_alice": 0,
            "relationship_bob": 0,
            "karma": 50,
            "money": 100,
            "choices_made": []
        }
        self.dialogue_history = []

class DialogueLabel:
    """Класс для анимированного вывода текста"""
    
    def __init__(self, callback=None):
        self.full_text = ""
        self.displayed_text = ""
        self.index = 0
        self.speed = 30  # символов в секунду
        self.callback = callback
        self.is_animating = False
        self.clock_event = None
    
    def set_text(self, text):
        """Установка нового текста для анимации"""
        self.full_text = text
        self.displayed_text = ""
        self.index = 0
        self.is_animating = True
        
        # Останавливаем предыдущую анимацию если есть
        if self.clock_event:
            self.clock_event.cancel()
        
        # Запускаем анимацию
        interval = 1.0 / self.speed
        self.clock_event = Clock.schedule_interval(self.update_text, interval)
    
    def update_text(self, dt):
        """Обновление отображаемого текста"""
        if self.index < len(self.full_text):
            self.displayed_text += self.full_text[self.index]
            self.index += 1
        else:
            self.complete_animation()
    
    def complete_animation(self):
        """Завершение анимации"""
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        
        self.is_animating = False
        self.displayed_text = self.full_text
        
        if self.callback:
            self.callback()
    
    def skip_animation(self):
        """Пропуск анимации"""
        if self.is_animating:
            self.complete_animation()
    
    def get_text(self):
        """Получение текущего текста"""
        return self.displayed_text

class GameScreen(BoxLayout):
    """Основной игровой экран"""
    
    # Свойства для связи с KV
    character_name = StringProperty("")
    dialogue_text = StringProperty("")
    background_image = StringProperty("")
    character_image = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_logic = VisualNovelGame()
        self.sound_manager = SoundManager()
        self.dialogue_animator = DialogueLabel(self.on_dialogue_complete)
        
        # Запускаем начальную сцену
        Clock.schedule_once(lambda dt: self.load_scene(), 0.1)
    
    def load_scene(self):
        """Загрузка текущей сцены"""
        scene = self.game_logic.game_data["scenes"].get(self.game_logic.current_scene, {})
        
        # Устанавливаем фон
        self.background_image = scene.get("background", "")
        
        # Запускаем фоновую музыку
        music = scene.get("music", "")
        if music:
            self.sound_manager.play_background_music(music)
        
        # Загружаем первый диалог
        self.load_current_dialogue()
    
    def load_current_dialogue(self):
        """Загрузка текущего диалога"""
        dialogue = self.game_logic.get_current_dialogue()
        
        if dialogue:
            # Устанавливаем персонажа
            self.character_name = dialogue.get("character", "")
            
            # Получаем изображение персонажа
            character_data = self.game_logic.game_data["characters"].get(self.character_name, {})
            expression = dialogue.get("expression", "neutral")
            images = character_data.get("images", {})
            self.character_image = images.get(expression, "")
            
            # Начинаем анимацию текста
            self.dialogue_animator.set_text(dialogue.get("text", ""))
            self.update_dialogue_text()
            
            # Проигрываем звук появления текста
            self.sound_manager.play_sound("text_appear.wav", volume=0.3)
        else:
            # Если диалогов нет, показываем выбор
            self.show_choices()
    
    def update_dialogue_text(self):
        """Обновление текста диалога"""
        self.dialogue_text = self.dialogue_animator.get_text()
    
    def on_dialogue_complete(self):
        """Вызывается когда диалог полностью отобразился"""
        pass
    
    def advance_dialogue(self):
        """Переход к следующему диалогу"""
        # Пропускаем анимацию если она еще идет
        if self.dialogue_animator.is_animating:
            self.dialogue_animator.skip_animation()
            self.update_dialogue_text()
            return
        
        # Звук клика
        self.sound_manager.play_sound("click.wav")
        
        # Переходим к следующему диалогу
        if self.game_logic.next_dialogue():
            self.load_current_dialogue()
        else:
            # Если диалоги закончились, показываем выбор
            self.show_choices()
    
    def show_choices(self):
        """Показ вариантов выбора"""
        # Этот метод будет вызываться из KV файла
        pass
    
    def make_choice(self, choice_index):
        """Обработка выбора"""
        # Звук выбора
        self.sound_manager.play_sound("choice_select.wav")
        
        # Обрабатываем выбор в логике игры
        if self.game_logic.make_choice(choice_index):
            # Загружаем новую сцену
            self.load_scene()
    
    def get_choices(self):
        """Получение вариантов выбора"""
        return self.game_logic.get_choices()
    
    def get_variables(self):
        """Получение переменных игры"""
        return self.game_logic.variables
    
    def save_game(self):
        """Сохранение игры"""
        self.game_logic.auto_save()
        # Проигрываем звук сохранения
        self.sound_manager.play_sound("save.wav")
        print("Игра сохранена")
    
    def load_game(self):
        """Загрузка игры"""
        if self.game_logic.load_save():
            self.load_scene()
            # Проигрываем звук загрузки
            self.sound_manager.play_sound("load.wav")
            print("Игра загружена")
            return True
        return False
    
    def on_stop(self):
        """При остановке приложения"""
        self.sound_manager.cleanup()

class SettingsScreen(BoxLayout):
    """Экран настроек"""
    
    def __init__(self, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)

class MainMenuScreen(BoxLayout):
    """Главное меню"""
    
    def __init__(self, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.orientation = 'vertical'
        self.padding = dp(50)
        self.spacing = dp(20)

class VisualNovelApp(App):
    """Главное приложение визуальной новеллы"""
    
    def build(self):
        self.title = "Визуальная Новелла"
        
        # Создаем главный игровой экран
        self.game_screen = GameScreen()
        
        return self.game_screen
    
    def on_stop(self):
        """При остановке приложения"""
        if hasattr(self, 'game_screen'):
            self.game_screen.on_stop()

# Точка входа
if __name__ == '__main__':
    try:
        print("=" * 50)
        print("Запуск Визуальной Новеллы...")
        print("=" * 50)
        
        # Создаем необходимые папки
        for folder in ['audio', 'characters', 'backgrounds', 'saves']:
            os.makedirs(folder, exist_ok=True)
        
        # Запускаем приложение
        VisualNovelApp().run()
        
    except Exception as e:
        print(f"\n{'='*50}")
        print("КРИТИЧЕСКАЯ ОШИБКА!")
        print(f"{'='*50}")
        print(f"Ошибка: {e}")
        traceback.print_exc()
        print(f"{'='*50}")
        
        # Пробуем запустить в безопасном режиме
        try:
            print("Попытка запуска в безопасном режиме...")
            from kivy.app import App
            from kivy.uix.label import Label
            safe_app = App()
            safe_app.build = lambda: Label(text="Визуальная новелла\n(безопасный режим)")
            safe_app.run()
        except:
            print("Не удалось запустить приложение")