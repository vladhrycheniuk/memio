"""Переклади Memio.

Ключ = український текст. Українська є мовою за замовчуванням, тому для неї
нічого перекладати не треба. Щоб додати нову мову:
  1. додай її в LANGS;
  2. додай назви місяців і днів у LISTS;
  3. додай словник перекладів, як EN нижче, і підключи його в TRANSLATIONS.
Якщо перекладу немає, показується український текст, тож нічого не ламається.
"""
import locale

LANGS = {"uk": "Українська", "en": "English", "sv": "Svenska"}

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
    "sv": {
        "months": ["Januari", "Februari", "Mars", "April", "Maj", "Juni",
                   "Juli", "Augusti", "September", "Oktober", "November", "December"],
        "months_gen": ["januari", "februari", "mars", "april", "maj", "juni",
                       "juli", "augusti", "september", "oktober", "november", "december"],
        "weekdays": ["Mån", "Tis", "Ons", "Tors", "Fre", "Lör", "Sön"],
        "weekdays_full": ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag",
                          "Lördag", "Söndag"],
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
    # «Мій день» і «Щоденник»
    "📖  Щоденник": "📖  Diary",
    "Щоденник": "Diary",
    "Справи дня": "Tasks of the day",
    "Фото дня": "Photo of the day",
    "Фото автоматично потрапляє в календар «Щоденник».":
        "The photo automatically appears in the Diary calendar.",
    "Фото й запис можна додати в сам день 🌿":
        "You can add a photo and a note on the day itself 🌿",
    "Збережено ✓": "Saved ✓",
    "Дата": "Date",
    "Завтра": "Tomorrow",
    "Через тиждень": "In a week",
    "Без дати": "No date",
    # повтори, «головне», «заповнений місяць»
    "Повтор": "Repeat",
    "Повторювати до": "Repeat until",
    "Кінця місяця": "End of month",
    "Кінця року": "End of year",
    "Кінця наступного року": "End of next year",
    "Повторюватиметься до {date}": "Repeats until {date}",
    "Частина серії повторів": "Part of a repeating series",
    "Застосувати до": "Apply to",
    "Лише це завдання": "Only this task",
    "Це й наступні": "This and following",
    "Усі в серії": "All in the series",
    "Не повторювати": "Don't repeat",
    "Щодня": "Daily",
    "По буднях": "Weekdays",
    "Щотижня": "Weekly",
    "Щомісяця": "Monthly",
    "★ Головне на день": "★ Top pick of the day",
    "Головне на день": "Top picks of the day",
    "Решта": "The rest",
    "Познач ★ до трьох справ, які справді важливі. Решта за можливості.":
        "Mark up to three tasks with ★ that truly matter. The rest is optional.",
    "Головних справ може бути не більше трьох.": "You can have at most three top picks per day.",
    "Не вдалося зберегти завдання.": "Could not save the task.",
    "Головне зроблено, решта це бонус 🌿": "The main things are done, the rest is a bonus 🌿",
    "Заповнено {filled} з {total} днів": "Filled {filled} of {total} days",
    "Кожен день це маленька історія. Почни з сьогоднішнього 🌱":
        "Every day is a small story. Start with today 🌱",
    "Дні можна дописувати пізніше, нічого не згорає 🌿":
        "You can fill in days later, nothing expires 🌿",
    "Місяць заповнено! Можна друкувати календар 🌸":
        "The month is full! Time to print the calendar 🌸",
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

SV = {
    # меню та розділи
    "🗂  Плани": "🗂  Planer",
    "🌸  Мій день": "🌸  Min dag",
    "📅  Календар": "📅  Kalender",
    "📖  Щоденник": "📖  Dagbok",
    "⚙  Налаштування": "⚙  Inställningar",
    "💙  Про Memio": "💙  Om Memio",
    "Меню": "Meny",
    "Плани": "Planer",
    "Календар": "Kalender",
    "Мій день": "Min dag",
    "Щоденник": "Dagbok",
    "Налаштування": "Inställningar",
    "Про Memio": "Om Memio",
    # періоди, пріоритети, колонки, теми
    "День": "Dag", "Тиждень": "Vecka", "Місяць": "Månad", "Рік": "År", "Усі": "Alla",
    "Високий": "Hög", "Середній": "Medel", "Низький": "Låg",
    "Зробити": "Att göra", "В процесі": "Pågår", "Готово": "Klart",
    "Навчання": "Studier", "Робота": "Jobb", "Дім": "Hem", "Особисте": "Personligt",
    "Хвиля": "Våg", "Сакура": "Körsbärsblom", "Мʼята": "Mynta", "Ніч": "Natt",
    # завдання
    "+ Додати завдання": "+ Lägg till uppgift",
    "Нове завдання": "Ny uppgift",
    "Редагувати завдання": "Redigera uppgift",
    "Назва": "Titel",
    "Введи назву": "Ange en titel",
    "Опис (необовʼязково)": "Beskrivning (valfritt)",
    "Пріоритет": "Prioritet",
    "Тема": "Ämne",
    "Без теми": "Inget ämne",
    "Або нова тема": "Eller ett nytt ämne",
    "Усі теми": "Alla ämnen",
    "Усі завдання": "Alla uppgifter",
    "Видалити": "Ta bort",
    "Скасувати": "Avbryt",
    "Зберегти": "Spara",
    "Закрити": "Stäng",
    "Сьогодні": "Idag",
    "Сьогодні · ": "Idag · ",
    "Дата": "Datum",
    "Завтра": "Imorgon",
    "Через тиждень": "Om en vecka",
    "Без дати": "Inget datum",
    "Перенести на сьогодні": "Flytta till idag",
    "🌿 Невиконаних справ з минулих днів: {n}. Нічого страшного, їх можна перенести.":
        "🌿 Oavslutade uppgifter från tidigare dagar: {n}. Ingen fara, de kan flyttas.",
    "Тут поки нічого не заплановано. Спокійний час 🌿": "Inget planerat här än. Lugn tid 🌿",
    "Поки нічого не заплановано. Спокійний день 🌿": "Inget planerat än. En lugn dag 🌿",
    "+{n} ще": "+{n} till",
    # календар, «Мій день», «Щоденник»
    "Планування": "Planering",
    "Підсумки": "Sammanfattning",
    "Плани дня": "Dagens planer",
    "Натисни на день, щоб додати фото, настрій і записку 🌸":
        "Tryck på en dag för att lägga till foto, humör och anteckning 🌸",
    "📷  Додати фото дня": "📷  Lägg till dagens foto",
    "Змінити фото": "Byt foto",
    "Прибрати фото": "Ta bort foto",
    "Настрій": "Humör",
    "Записка дня (до 280 символів)": "Dagens anteckning (upp till 280 tecken)",
    "Обери фото дня": "Välj dagens foto",
    "Зображення": "Bilder",
    "Усі файли": "Alla filer",
    "Не вдалося відкрити вибір файлу.": "Kunde inte öppna filväljaren.",
    "Не вдалося завантажити фото.": "Kunde inte ladda upp fotot.",
    "Не вдалося завантажити фото. Спробуй інший файл (jpg або png).":
        "Kunde inte ladda upp fotot. Prova en annan fil (jpg eller png).",
    "Справи дня": "Dagens uppgifter",
    "Фото дня": "Dagens foto",
    "Фото автоматично потрапляє в календар «Щоденник».":
        "Fotot hamnar automatiskt i kalendern i Dagboken.",
    "Фото й запис можна додати в сам день 🌿":
        "Foto och anteckning kan läggas till under själva dagen 🌿",
    "Збережено ✓": "Sparat ✓",
    "Зроблено {done} з {total}": "Klart {done} av {total}",
    "Усе зроблено, чудовий день 💙": "Allt klart, en underbar dag 💙",
    "Іноді день це просто відпочинок 🌿": "Ibland är en dag bara vila 🌿",
    "Решту можна спокійно перенести 🌿": "Resten kan lugnt flyttas 🌿",
    # повтори, «головне», «заповнений місяць»
    "Повтор": "Upprepning",
    "Повторювати до": "Upprepa till",
    "Кінця місяця": "Slutet av månaden",
    "Кінця року": "Slutet av året",
    "Кінця наступного року": "Slutet av nästa år",
    "Повторюватиметься до {date}": "Upprepas till {date}",
    "Частина серії повторів": "Del av en återkommande serie",
    "Застосувати до": "Gäller för",
    "Лише це завдання": "Bara den här uppgiften",
    "Це й наступні": "Denna och följande",
    "Усі в серії": "Alla i serien",
    "Не повторювати": "Upprepa inte",
    "Щодня": "Dagligen",
    "По буднях": "Vardagar",
    "Щотижня": "Varje vecka",
    "Щомісяця": "Varje månad",
    "★ Головне на день": "★ Dagens viktigaste",
    "Головне на день": "Dagens viktigaste",
    "Решта": "Resten",
    "Познач ★ до трьох справ, які справді важливі. Решта за можливості.":
        "Markera upp till tre uppgifter med ★ som verkligen är viktiga. Resten gör du i mån av tid.",
    "Головних справ може бути не більше трьох.": "Du kan ha högst tre viktigaste uppgifter per dag.",
    "Не вдалося зберегти завдання.": "Kunde inte spara uppgiften.",
    "Головне зроблено, решта це бонус 🌿": "Det viktigaste är klart, resten är en bonus 🌿",
    "Заповнено {filled} з {total} днів": "Ifyllt {filled} av {total} dagar",
    "Кожен день це маленька історія. Почни з сьогоднішнього 🌱":
        "Varje dag är en liten berättelse. Börja med idag 🌱",
    "Дні можна дописувати пізніше, нічого не згорає 🌿":
        "Du kan fylla i dagar senare, inget försvinner 🌿",
    "Місяць заповнено! Можна друкувати календар 🌸":
        "Månaden är full! Dags att skriva ut kalendern 🌸",
    # друк
    "🖨 Друк місяця": "🖨 Skriv ut månaden",
    "Друк · {month} {year}": "Utskrift · {month} {year}",
    "Формат файлу": "Filformat",
    "Орієнтація аркуша A4": "Orientering på A4-arket",
    "Альбомна": "Liggande",
    "Книжкова": "Stående",
    "Рамка": "Ram",
    "Без рамки": "Ingen ram",
    "Лінія": "Linje",
    "Подвійна": "Dubbel",
    "Заокруглена": "Rundad",
    "Пунктир": "Streckad",
    "Колір рамки": "Ramfärg",
    "Товщина рамки": "Ramtjocklek",
    "Тонка": "Tunn",
    "Середня": "Medel",
    "Товста": "Tjock",
    "Клітинки днів": "Dagrutor",
    "Круглі кути": "Runda hörn",
    "Прямі кути": "Raka hörn",
    "З логотипом": "Med logotyp",
    "Без логотипа": "Utan logotyp",
    "Смайлики настрою не друкуються, лише фото й числа.":
        "Humörsymboler skrivs inte ut, bara foton och datum.",
    "Оновлюю перегляд…": "Uppdaterar förhandsvisningen…",
    "Не вдалося створити перегляд": "Kunde inte skapa förhandsvisningen",
    "Створити файл": "Skapa fil",
    "Створюю файл…": "Skapar filen…",
    "Не вдалося створити файл.": "Kunde inte skapa filen.",
    "Готово: {file} (папка exports)": "Klart: {file} (mappen exports)",
    "Відкрити папку": "Öppna mappen",
    # налаштування
    "Колірна тема": "Färgtema",
    "Мова": "Språk",
    "Налаштування зберігаються автоматично.": "Inställningarna sparas automatiskt.",
    # про Memio
    "Memio — затишний планувальник і щоденник: плануй день вранці, а ввечері зберігай його фото, настрій і записку.":
        "Memio är en mysig planerare och dagbok: planera dagen på morgonen och spara kvällens foto, humör och anteckning.",
    "Версія": "Version",
    "Автор": "Skapare",
    "Пошта": "E-post",
    "Написати листа": "Skriv ett mejl",
    "Сайт": "Webbplats",
    "Підтримати проєкт": "Stöd projektet",
    "Memio безкоштовний. Якщо він тобі подобається, можеш підтримати розробку.":
        "Memio är gratis. Gillar du appen kan du stödja utvecklingen.",
    "Відгук або ідея": "Feedback eller idé",
    "Що б ти хотів змінити чи додати?": "Vad skulle du vilja ändra eller lägga till?",
    "Надіслати поштою": "Skicka via e-post",
    "Напиши кілька слів, щоб було що надсилати.": "Skriv några ord först.",
    "Відкрив поштову програму. Якщо вона не відкрилась, напиши на {email}":
        "Öppnade din e-postapp. Om den inte öppnades, skriv till {email}",
}

TRANSLATIONS = {"en": EN, "sv": SV}


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
    # якщо перекладу немає, пробуємо англійську, потім українську
    return table.get(text) or EN.get(text) or text


def detect_language():
    """Мова системи, якщо вона підтримується; інакше англійська."""
    try:
        code = (locale.getdefaultlocale()[0] or "").lower()
    except Exception:
        code = ""
    if code.startswith("uk"):
        return "uk"
    if code.startswith("sv"):
        return "sv"
    return "en" if code else "uk"
