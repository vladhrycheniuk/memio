"""Переклади Memio.

Ключ = український текст. Українська є мовою за замовчуванням, тому для неї
нічого перекладати не треба. Щоб додати нову мову:
  1. додай її в LANGS;
  2. додай назви місяців і днів у LISTS;
  3. додай словник перекладів, як EN нижче, і підключи його в TRANSLATIONS.
Якщо перекладу немає, показується український текст, тож нічого не ламається.
"""
import locale

LANGS = {"uk": "Українська", "en": "English"}

_state = {"lang": "uk"}

LISTS = {
    "uk": {
        "months": ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
                   "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"],
        "months_gen": ["січня", "лютого", "березня", "квітня", "травня", "червня",
                       "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"],
        "weekdays": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
        "weekdays_full": ["Понеділок", "Вівторок", "Середа", "Четвер", "Пʼятниця",
                          "Субота", "Неділя"],
    },
    "en": {
        "months": ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"],
        "months_gen": ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"],
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "weekdays_full": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                          "Saturday", "Sunday"],
    },
}

EN = {
    # меню та розділи
    "🗂  Плани": "🗂  Plans",
    "📅  Календар": "📅  Calendar",
    "🌸  Мій день": "🌸  My day",
    "⚙  Налаштування": "⚙  Settings",
    "💙  Про Memio": "💙  About Memio",
    "Меню": "Menu",
    "Плани": "Plans",
    "Календар": "Calendar",
    "Мій день": "My day",
    "Налаштування": "Settings",
    "Про Memio": "About Memio",
    # періоди, пріоритети, колонки, теми
    "День": "Day", "Тиждень": "Week", "Місяць": "Month", "Рік": "Year", "Усі": "All",
    "Високий": "High", "Середній": "Medium", "Низький": "Low",
    "Зробити": "To do", "В процесі": "In progress", "Готово": "Done",
    "Навчання": "Study", "Робота": "Work", "Дім": "Home", "Особисте": "Personal",
    "Хвиля": "Wave", "Сакура": "Sakura", "Мʼята": "Mint", "Ніч": "Night",
    # завдання
    "+ Додати завдання": "+ Add task",
    "Нове завдання": "New task",
    "Редагувати завдання": "Edit task",
    "Назва": "Title",
    "Введи назву": "Enter a title",
    "Опис (необовʼязково)": "Description (optional)",
    "Дата РРРР-ММ-ДД (необовʼязково)": "Date YYYY-MM-DD (optional)",
    "Формат: 2026-10-31": "Format: 2026-10-31",
    "Пріоритет": "Priority",
    "Тема": "Topic",
    "Без теми": "No topic",
    "Або нова тема": "Or a new topic",
    "Усі теми": "All topics",
    "Усі завдання": "All tasks",
    "Видалити": "Delete",
    "Скасувати": "Cancel",
    "Зберегти": "Save",
    "Закрити": "Close",
    "Сьогодні": "Today",
    "Сьогодні · ": "Today · ",
    "Перенести на сьогодні": "Move to today",
    "🌿 Невиконаних справ з минулих днів: {n}. Нічого страшного, їх можна перенести.":
        "🌿 Unfinished tasks from past days: {n}. No worries, they can be moved.",
    "Тут поки нічого не заплановано. Спокійний час 🌿": "Nothing planned here yet. Calm time 🌿",
    "Поки нічого не заплановано. Спокійний день 🌿": "Nothing planned yet. A calm day 🌿",
    "+{n} ще": "+{n} more",
    # календар і «Мій день»
    "Планування": "Planning",
    "Підсумки": "Summaries",
    "Плани дня": "Day's plans",
    "Натисни на день, щоб додати фото, настрій і записку 🌸":
        "Tap a day to add a photo, mood and a note 🌸",
    "📷  Додати фото дня": "📷  Add photo of the day",
    "Змінити фото": "Change photo",
    "Прибрати фото": "Remove photo",
    "Настрій": "Mood",
    "Записка дня (до 280 символів)": "Note of the day (up to 280 characters)",
    "Обери фото дня": "Choose the photo of the day",
    "Зображення": "Images",
    "Усі файли": "All files",
    "Не вдалося відкрити вибір файлу.": "Could not open the file picker.",
    "Не вдалося завантажити фото.": "Could not upload the photo.",
    "Не вдалося завантажити фото. Спробуй інший файл (jpg або png).":
        "Could not upload the photo. Try another file (jpg or png).",
    "На цей день нічого не було заплановано 🌿": "Nothing was planned for this day 🌿",
    "Зроблено {done} з {total}": "Done {done} of {total}",
    "Усе зроблено, чудовий день 💙": "All done, a wonderful day 💙",
    "Іноді день це просто відпочинок 🌿": "Sometimes a day is just for resting 🌿",
    "Решту можна спокійно перенести 🌿": "The rest can calmly be moved 🌿",
    # друк
    "🖨 Друк місяця": "🖨 Print month",
    "Друк · {month} {year}": "Print · {month} {year}",
    "Формат файлу": "File format",
    "Орієнтація аркуша A4": "A4 page orientation",
    "Альбомна": "Landscape",
    "Книжкова": "Portrait",
    "Рамка": "Frame",
    "Без рамки": "No frame",
    "Лінія": "Line",
    "Подвійна": "Double",
    "Заокруглена": "Rounded",
    "Пунктир": "Dashed",
    "Колір рамки": "Frame color",
    "Товщина рамки": "Frame thickness",
    "Тонка": "Thin",
    "Середня": "Medium",
    "Товста": "Thick",
    "Клітинки днів": "Day cells",
    "Круглі кути": "Rounded corners",
    "Прямі кути": "Square corners",
    "З логотипом": "With logo",
    "Без логотипа": "No logo",
    "Смайлики настрою не друкуються, лише фото й числа.":
        "Mood emojis are not printed, only photos and numbers.",
    "Оновлюю перегляд…": "Updating preview…",
    "Не вдалося створити перегляд": "Could not create the preview",
    "Створити файл": "Create file",
    "Створюю файл…": "Creating file…",
    "Не вдалося створити файл.": "Could not create the file.",
    "Готово: {file} (папка exports)": "Done: {file} (exports folder)",
    "Відкрити папку": "Open folder",
    # налаштування
    "Колірна тема": "Color theme",
    "Мова": "Language",
    "Налаштування зберігаються автоматично.": "Settings are saved automatically.",
    # про Memio
    "Memio — затишний планувальник і щоденник: плануй день вранці, а ввечері зберігай його фото, настрій і записку.":
        "Memio is a cozy planner and diary: plan your day in the morning, and in the evening keep its photo, mood and a note.",
    "Версія": "Version",
    "Автор": "Author",
    "Зв’язок": "Contact",
    "Пошта": "Email",
    "Написати листа": "Write an email",
    "Сайт": "Website",
    "Підтримати проєкт": "Support the project",
    "Memio безкоштовний. Якщо він тобі подобається, можеш підтримати розробку.":
        "Memio is free. If you like it, you can support its development.",
    "Відгук або ідея": "Feedback or an idea",
    "Що б ти хотів змінити чи додати?": "What would you like to change or add?",
    "Надіслати поштою": "Send by email",
    "Напиши кілька слів, щоб було що надсилати.": "Write a few words first.",
    "Відкрив поштову програму. Якщо вона не відкрилась, напиши на {email}":
        "Opened your mail app. If it did not open, write to {email}",
}

TRANSLATIONS = {"en": EN}


def set_language(code):
    _state["lang"] = code if code in LANGS else "uk"


def get_language():
    return _state["lang"]


def lists():
    return LISTS[_state["lang"]]


def tr(text):
    table = TRANSLATIONS.get(_state["lang"])
    if not table:
        return text
    return table.get(text, text)


def detect_language():
    """Мова системи, якщо вона підтримується; інакше англійська."""
    try:
        code = (locale.getdefaultlocale()[0] or "").lower()
    except Exception:
        code = ""
    if code.startswith("uk"):
        return "uk"
    return "en" if code else "uk"
