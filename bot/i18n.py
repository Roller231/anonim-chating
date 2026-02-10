"""
Internationalization module. Loads translations based on BOT_LANG env var.
Usage: from bot.i18n import T
"""
import os

LANG = os.getenv("BOT_LANG", "ru")

RU = {
    # ─── Main menu buttons ───
    "btn_find_girl": "Найти 👩",
    "btn_random": "🎪 Рандом",
    "btn_find_boy": "Найти 🧑",
    "btn_vip": "VIP статус 🔥",
    "btn_rooms": "🏠 Комнаты",
    "btn_profile": "👤 Профиль",

    # ─── Gender ───
    "gender_male": "👨 Мужской",
    "gender_female": "👩 Женский",
    "gender_any": "🔀 Любой",
    "gender_male_short": "Мужской",
    "gender_female_short": "Женский",

    # ─── Age keyboard ───
    "age_under_18": "до 18",
    "age_any": "🔀 Любой",

    # ─── Countries ───
    "countries": [
        ("🇷🇺 Россия", "Россия"),
        ("🇺🇦 Украина", "Украина"),
        ("🇧🇾 Беларусь", "Беларусь"),
        ("🇰🇿 Казахстан", "Казахстан"),
        ("🇺🇿 Узбекистан", "Узбекистан"),
        ("🌍 Другая", "Другая"),
    ],
    "country_any": "🔀 Любая",

    # ─── Interests ───
    "interests": [
        ("Общение", "💬"),
        ("Флирт", "❤️"),
        ("Игры", "🎮"),
        ("Музыка", "🎵"),
        ("Книги", "📚"),
        ("Кино", "🎬"),
        ("Спорт", "⚽"),
        ("IT", "💻"),
        ("Путешествия", "✈️"),
        ("Еда", "🍕"),
        ("Искусство", "🎨"),
        ("Наука", "🔬"),
        ("Фото", "📷"),
        ("Мода", "👗"),
        ("Авто", "🚗"),
        ("Природа", "🌿"),
    ],
    "interests_done": "✅ Готово",
    "interests_none": "Не указаны",

    # ─── Registration ───
    "welcome": (
        "👋 Добро пожаловать в Анонимный чат!\n\n"
        "Давайте заполним вашу анкету.\n\n"
        "👫 Выберите ваш пол:"
    ),
    "choose_age": "🔞 Выберите ваш возраст:",
    "choose_country": "🌎 Выберите вашу страну:",
    "choose_interests": "🎯 Выберите ваши интересы (можно несколько), затем нажмите ✅ Готово:",
    "choose_interests_selected": "Выбрано: {selected}",
    "nothing_selected": "ничего не выбрано",
    "interest_added": "✅ {name} добавлен",
    "interest_removed": "❌ {name} убран",
    "reg_complete": (
        "✅ Регистрация завершена!\n\n"
        "#️⃣ ID — {tid}\n"
        "👫 Пол — {gender}\n"
        "🔞 Возраст — от {age_min} до {age_max}\n"
        "🌎 Страна — {country}\n"
        "🎯 Интересы — {interests}\n\n"
        "Используйте кнопки меню для навигации 👇"
    ),
    "reg_complete_btn": "✅ Регистрация завершена!",
    "start_search_btn": "🔍 Нажмите кнопку ниже чтобы начать поиск!",
    "register_first": "❌ Сначала зарегистрируйтесь: /start",

    # ─── Profile ───
    "profile_title": "👤 Ваш профиль",
    "profile_text": (
        "👤 Ваш профиль\n\n"
        "#️⃣ ID — {tid}\n"
        "👫 Пол — {gender}\n"
        "🔞 Возраст — от {age_min} до {age_max}\n"
        "🌎 Страна — {country}\n"
        "🎯 Интересы — {interests}\n\n"
        "📊 Статистика:\n"
        "    💬 Чатов: {chats}\n"
        "    📨 Сообщений: {messages}\n"
        "    👍 Лайков: {likes}\n"
        "    👎 Дизлайков: {dislikes}\n\n"
        "{vip_line}"
    ),
    "vip_active_line": "👑 VIP до {until}\n",
    "vip_inactive_line": "👑 VIP — нет (купить: «VIP статус 🔥»)\n",
    "edit_gender": "👫 Изменить пол",
    "edit_age": "🔞 Изменить возраст",
    "edit_country": "🌎 Изменить страну",
    "edit_interests": "🎯 Изменить интересы",
    "edit_search": "⚙️ Настройки поиска",
    "gender_changed": "✅ Пол изменён на: {g}",
    "age_changed": "✅ Возраст изменён на: {age_min}-{age_max}",
    "country_changed": "✅ Страна изменена на: {country}",
    "interests_updated": "✅ Интересы обновлены!\n\n🎯 {interests}",
    "saved": "✅ Сохранено!",

    # ─── Search ───
    "in_chat": "💬 Вы уже в чате! Используйте /stop чтобы завершить или /next для нового собеседника.",
    "searching": "🔍 Ищем собеседника...\n👥 В очереди: {count}\n\nОжидайте, мы найдём вам пару!",
    "search_cancelled": "🔍 Поиск отменён.",
    "no_active_chat": "❌ У вас нет активного чата.",
    "no_chat_idle": "💤 У вас нет активного чата.\nНажмите /start чтобы найти собеседника.",

    # ─── Chat connection ───
    "connected_title": "🟢 Собеседник найден!",
    "partner_gender": "👫 Пол",
    "partner_age": "🔞 Возраст",
    "partner_country": "🌎 Страна",
    "partner_interests": "🎯 Интересы",
    "partner_vip_yes": "👑 VIP: Да",
    "chat_stopped": "🔴 Чат завершён.\n💬 Оцените собеседника:",
    "partner_left": "🔴 Собеседник завершил чат.",
    "partner_left_next": "🔴 Собеседник перешёл к следующему чату.",
    "msg_not_delivered": "❌ Не удалось доставить сообщение.",

    # ─── Media limit ───
    "media_limit": (
        "⏳ Лимит медиа: {limit} шт. за {window} сек.\n"
        "Подождите {wait} сек.\n"
        "👑 VIP пользователи отправляют медиа без ограничений!"
    ),
    "photo_fail": "❌ Не удалось доставить фото.",
    "sticker_fail": "❌ Не удалось доставить стикер.",
    "voice_fail": "❌ Не удалось доставить голосовое сообщение.",
    "video_fail": "❌ Не удалось доставить видео.",
    "videonote_fail": "❌ Не удалось доставить видеосообщение.",
    "doc_fail": "❌ Не удалось доставить документ.",

    # ─── Rating ───
    "rate_like": "👍 Лайк",
    "rate_dislike": "👎 Дизлайк",
    "rate_skip": "⏭ Пропустить",
    "rate_done": "{emoji} Вы поставили {label} собеседнику.",
    "rate_like_label": "лайк",
    "rate_dislike_label": "дизлайк",
    "already_rated": "Вы уже оценили этот чат.",

    # ─── Next ───
    "next_stop": "🔴 Предыдущий чат завершён. Ищем нового...",

    # ─── VIP / Menu ───
    "gender_search_limit": (
        "🚫 Лимит поиска по полу на сегодня исчерпан ({limit}/{limit}).\n\n"
        "👑 VIP пользователи ищут без ограничений!\n"
        "Нажмите «VIP статус 🔥» для покупки.\n\n"
        "Или используйте «🎪 Рандом» — без ограничений!"
    ),
    "gender_search_left": "🔍 Осталось поисков по полу на сегодня: {remaining}",
    "vip_title": (
        "👑 VIP статус\n\n"
        "Преимущества VIP:\n"
        "• Безлимитный поиск по полу\n"
        "• Мгновенная отправка медиа\n"
        "• Подробная информация о собеседнике\n"
        "• Доступ к /search (возраст, страна)\n"
        "• Приоритет в очереди поиска\n"
        "• Значок 👑 в чате\n\n"
        "Выберите план:"
    ),
    "vip_free_title": (
        "🎁 Получить VIP статус бесплатно\n\n"
        "Приглашайте друзей и получайте баллы!\n"
        "Обменять 10 баллов на 1 день VIP 👑 — /exchange\n\n"
        "Ваша реферальная ссылка:\n👉 {ref_link}\n\n"
        "Также вы можете оплатить VIP через TON:\n"
        "💎 Кошелек: <code>{wallet}</code>\n"
        "После перевода напишите в поддержку для активации."
    ),
    "vip_free_btn": "🎁 Получить VIP статус бесплатно",
    "vip_buy_success": (
        "✅ Оплата прошла успешно!\n\n"
        "👑 VIP статус активирован до {until}\n\n"
        "Наслаждайтесь преимуществами VIP! 🎉"
    ),

    # ─── Rooms ───
    "rooms_title": "🏠 Комнаты\n\nВыберите комнату для поиска собеседника:",
    "no_rooms": "😔 Комнаты пока недоступны.",

    # ─── Search settings (VIP) ───
    "search_vip_only": (
        "🔒 Команда /search доступна только VIP пользователям!\n\n"
        "👑 Купите VIP подписку, чтобы настраивать поиск по возрасту и стране.\n"
        "Нажмите «VIP статус 🔥» для покупки."
    ),
    "search_settings_title": "⚙️ Настройки поиска",
    "search_current_prefs": "Текущие предпочтения:",
    "search_choose_gender": "👫 Выберите предпочитаемый пол собеседника:",
    "search_choose_age": "🔞 Выберите предпочитаемый возраст собеседника:",
    "search_choose_country": "🌎 Выберите предпочитаемую страну собеседника:",
    "search_saved": (
        "✅ Настройки поиска сохранены!\n\n"
        "{summary}\n\n"
        "Нажмите /start чтобы начать поиск 🔍"
    ),
    "pref_gender_label": "👫 Пол",
    "pref_age_label": "🔞 Возраст",
    "pref_country_label": "🌎 Страна",
    "any_label": "🔀 Любой",
    "any_f_label": "🔀 Любая",
    "any_age_label": "🔀 Любой",

    # ─── Referral ───
    "ref_title": (
        "💼 Реферальный кабинет\n\n"
        "    🔮 Баллов: {points}\n"
        "    🎪 Приглашено: {count}\n\n"
        "💱 Обмен баллов:\n"
        "Обменять 10 баллов на 1 день VIP статуса 👑 — /exchange\n\n"
        "Для получения баллов распространяйте свою персональную ссылку:\n"
        "👉 {ref_link}\n\n"
        "Пример рассылки:\n\n"
        "Бот для анонимного общения в Telegram! 🎭\n"
        "Поиск по полу, возрасту и стране 😻\n\n"
        "Скорее регистрируйся по моей ссылке, чтобы получить VIP статус!\n\n"
        "👉 {ref_link}"
    ),
    "exchange_not_enough": (
        "❌ Недостаточно баллов!\n\n"
        "У вас: {points} баллов\n"
        "Необходимо: 10 баллов\n\n"
        "Приглашайте друзей по реферальной ссылке: /ref"
    ),
    "exchange_success": (
        "✅ Обмен успешен!\n\n"
        "👑 VIP статус активирован до {until}\n"
        "🔮 Осталось баллов: {remaining}"
    ),
    "exchange_fail": "❌ Ошибка при обмене. Попробуйте позже.",

    # ─── Top ───
    "top_title": "🏆 Рейтинги чата\n\nВыберите вид рейтинга:",
    "top_karma": "👁️ По карме",
    "top_referrals": "🎪 По рефералам",
    "top_activity": "📧 По активности",
    "top_karma_title": "👁️ Топ-10 по карме",
    "top_referrals_title": "🎪 Топ-10 по рефералам",
    "top_activity_title": "📧 Топ-10 по активности",
    "top_empty": "Пока никого нет в рейтинге.",
    "top_karma_line": "{i}. {name}{vip} — 👍 {likes} 👎 {dislikes} (={karma})",
    "top_referrals_line": "{i}. {name}{vip} — {count} приглашённых",
    "top_activity_line": "{i}. {name}{vip} — {count} сообщений",
}


EN = {
    # ─── Main menu buttons ───
    "btn_find_girl": "Find 👩",
    "btn_random": "🎪 Random",
    "btn_find_boy": "Find 🧑",
    "btn_vip": "VIP status 🔥",
    "btn_rooms": "🏠 Rooms",
    "btn_profile": "👤 Profile",

    # ─── Gender ───
    "gender_male": "👨 Male",
    "gender_female": "👩 Female",
    "gender_any": "🔀 Any",
    "gender_male_short": "Male",
    "gender_female_short": "Female",

    # ─── Age keyboard ───
    "age_under_18": "under 18",
    "age_any": "🔀 Any",

    # ─── Countries ───
    "countries": [
        ("🇺🇸 USA", "USA"),
        ("🇬🇧 UK", "UK"),
        ("🇨🇦 Canada", "Canada"),
        ("🇩🇪 Germany", "Germany"),
        ("🇫🇷 France", "France"),
        ("🌍 Other", "Other"),
    ],
    "country_any": "🔀 Any",

    # ─── Interests ───
    "interests": [
        ("Chat", "💬"),
        ("Flirt", "❤️"),
        ("Gaming", "🎮"),
        ("Music", "🎵"),
        ("Books", "📚"),
        ("Movies", "🎬"),
        ("Sports", "⚽"),
        ("IT", "💻"),
        ("Travel", "✈️"),
        ("Food", "🍕"),
        ("Art", "🎨"),
        ("Science", "🔬"),
        ("Photo", "📷"),
        ("Fashion", "👗"),
        ("Cars", "🚗"),
        ("Nature", "🌿"),
    ],
    "interests_done": "✅ Done",
    "interests_none": "Not specified",

    # ─── Registration ───
    "welcome": (
        "👋 Welcome to Anonymous Chat!\n\n"
        "Let's fill in your profile.\n\n"
        "👫 Choose your gender:"
    ),
    "choose_age": "🔞 Choose your age:",
    "choose_country": "🌎 Choose your country:",
    "choose_interests": "🎯 Choose your interests (multiple allowed), then press ✅ Done:",
    "choose_interests_selected": "Selected: {selected}",
    "nothing_selected": "nothing selected",
    "interest_added": "✅ {name} added",
    "interest_removed": "❌ {name} removed",
    "reg_complete": (
        "✅ Registration complete!\n\n"
        "#️⃣ ID — {tid}\n"
        "👫 Gender — {gender}\n"
        "🔞 Age — {age_min} to {age_max}\n"
        "🌎 Country — {country}\n"
        "🎯 Interests — {interests}\n\n"
        "Use the menu buttons to navigate 👇"
    ),
    "reg_complete_btn": "✅ Registration complete!",
    "start_search_btn": "🔍 Press a button below to start searching!",
    "register_first": "❌ Please register first: /start",

    # ─── Profile ───
    "profile_title": "👤 Your Profile",
    "profile_text": (
        "👤 Your Profile\n\n"
        "#️⃣ ID — {tid}\n"
        "👫 Gender — {gender}\n"
        "🔞 Age — {age_min} to {age_max}\n"
        "🌎 Country — {country}\n"
        "🎯 Interests — {interests}\n\n"
        "📊 Stats:\n"
        "    💬 Chats: {chats}\n"
        "    📨 Messages: {messages}\n"
        "    👍 Likes: {likes}\n"
        "    👎 Dislikes: {dislikes}\n\n"
        "{vip_line}"
    ),
    "vip_active_line": "👑 VIP until {until}\n",
    "vip_inactive_line": "👑 VIP — no (buy: «VIP status 🔥»)\n",
    "edit_gender": "👫 Change gender",
    "edit_age": "🔞 Change age",
    "edit_country": "🌎 Change country",
    "edit_interests": "🎯 Change interests",
    "edit_search": "⚙️ Search settings",
    "gender_changed": "✅ Gender changed to: {g}",
    "age_changed": "✅ Age changed to: {age_min}-{age_max}",
    "country_changed": "✅ Country changed to: {country}",
    "interests_updated": "✅ Interests updated!\n\n🎯 {interests}",
    "saved": "✅ Saved!",

    # ─── Search ───
    "in_chat": "💬 You're already in a chat! Use /stop to end or /next for a new partner.",
    "searching": "🔍 Searching for a partner...\n👥 In queue: {count}\n\nPlease wait, we'll find you a match!",
    "search_cancelled": "🔍 Search cancelled.",
    "no_active_chat": "❌ You have no active chat.",
    "no_chat_idle": "💤 You have no active chat.\nPress /start to find a partner.",

    # ─── Chat connection ───
    "connected_title": "🟢 Partner found!",
    "partner_gender": "👫 Gender",
    "partner_age": "🔞 Age",
    "partner_country": "🌎 Country",
    "partner_interests": "🎯 Interests",
    "partner_vip_yes": "👑 VIP: Yes",
    "chat_stopped": "🔴 Chat ended.\n💬 Rate your partner:",
    "partner_left": "🔴 Your partner ended the chat.",
    "partner_left_next": "🔴 Your partner moved to the next chat.",
    "msg_not_delivered": "❌ Failed to deliver the message.",

    # ─── Media limit ───
    "media_limit": (
        "⏳ Media limit: {limit} per {window} sec.\n"
        "Please wait {wait} sec.\n"
        "👑 VIP users send media without limits!"
    ),
    "photo_fail": "❌ Failed to deliver photo.",
    "sticker_fail": "❌ Failed to deliver sticker.",
    "voice_fail": "❌ Failed to deliver voice message.",
    "video_fail": "❌ Failed to deliver video.",
    "videonote_fail": "❌ Failed to deliver video message.",
    "doc_fail": "❌ Failed to deliver document.",

    # ─── Rating ───
    "rate_like": "👍 Like",
    "rate_dislike": "👎 Dislike",
    "rate_skip": "⏭ Skip",
    "rate_done": "{emoji} You gave a {label} to your partner.",
    "rate_like_label": "like",
    "rate_dislike_label": "dislike",
    "already_rated": "You have already rated this chat.",

    # ─── Next ───
    "next_stop": "🔴 Previous chat ended. Searching for a new one...",

    # ─── VIP / Menu ───
    "gender_search_limit": (
        "🚫 Daily gender search limit reached ({limit}/{limit}).\n\n"
        "👑 VIP users search without limits!\n"
        "Press «VIP status 🔥» to purchase.\n\n"
        "Or use «🎪 Random» — no limits!"
    ),
    "gender_search_left": "🔍 Gender searches left today: {remaining}",
    "vip_title": (
        "👑 VIP Status\n\n"
        "VIP Benefits:\n"
        "• Unlimited gender search\n"
        "• Instant media sending\n"
        "• Detailed partner info\n"
        "• Access to /search (age, country)\n"
        "• Priority in search queue\n"
        "• 👑 badge in chat\n\n"
        "Choose a plan:"
    ),
    "vip_free_title": (
        "🎁 Get VIP for free\n\n"
        "Invite friends and earn points!\n"
        "Exchange 10 points for 1 day of VIP 👑 — /exchange\n\n"
        "Your referral link:\n👉 {ref_link}\n\n"
        "You can also pay with TON:\n"
        "💎 Wallet: <code>{wallet}</code>\n"
        "After transfer, contact support for activation."
    ),
    "vip_free_btn": "🎁 Get VIP for free",
    "vip_buy_success": (
        "✅ Payment successful!\n\n"
        "👑 VIP activated until {until}\n\n"
        "Enjoy your VIP benefits! 🎉"
    ),

    # ─── Rooms ───
    "rooms_title": "🏠 Rooms\n\nChoose a room to find a partner:",
    "no_rooms": "😔 Rooms are not available yet.",

    # ─── Search settings (VIP) ───
    "search_vip_only": (
        "🔒 /search is available for VIP users only!\n\n"
        "👑 Buy a VIP subscription to filter by age and country.\n"
        "Press «VIP status 🔥» to purchase."
    ),
    "search_settings_title": "⚙️ Search Settings",
    "search_current_prefs": "Current preferences:",
    "search_choose_gender": "👫 Choose preferred partner gender:",
    "search_choose_age": "🔞 Choose preferred partner age:",
    "search_choose_country": "🌎 Choose preferred partner country:",
    "search_saved": (
        "✅ Search settings saved!\n\n"
        "{summary}\n\n"
        "Press /start to start searching 🔍"
    ),
    "pref_gender_label": "👫 Gender",
    "pref_age_label": "🔞 Age",
    "pref_country_label": "🌎 Country",
    "any_label": "🔀 Any",
    "any_f_label": "🔀 Any",
    "any_age_label": "🔀 Any",

    # ─── Referral ───
    "ref_title": (
        "💼 Referral Dashboard\n\n"
        "    🔮 Points: {points}\n"
        "    🎪 Invited: {count}\n\n"
        "💱 Exchange points:\n"
        "Exchange 10 points for 1 day VIP 👑 — /exchange\n\n"
        "Share your personal link to earn points:\n"
        "👉 {ref_link}\n\n"
        "Sample message:\n\n"
        "Anonymous chat bot on Telegram! 🎭\n"
        "Search by gender, age and country 😻\n\n"
        "Register using my link to get VIP status!\n\n"
        "👉 {ref_link}"
    ),
    "exchange_not_enough": (
        "❌ Not enough points!\n\n"
        "You have: {points} points\n"
        "Required: 10 points\n\n"
        "Invite friends via referral link: /ref"
    ),
    "exchange_success": (
        "✅ Exchange successful!\n\n"
        "👑 VIP activated until {until}\n"
        "🔮 Points remaining: {remaining}"
    ),
    "exchange_fail": "❌ Exchange error. Please try again later.",

    # ─── Top ───
    "top_title": "🏆 Chat Rankings\n\nChoose a ranking:",
    "top_karma": "👁️ By karma",
    "top_referrals": "🎪 By referrals",
    "top_activity": "📧 By activity",
    "top_karma_title": "👁️ Top 10 by karma",
    "top_referrals_title": "🎪 Top 10 by referrals",
    "top_activity_title": "📧 Top 10 by activity",
    "top_empty": "No one in the rankings yet.",
    "top_karma_line": "{i}. {name}{vip} — 👍 {likes} 👎 {dislikes} (={karma})",
    "top_referrals_line": "{i}. {name}{vip} — {count} invited",
    "top_activity_line": "{i}. {name}{vip} — {count} messages",
}

T: dict = RU if LANG == "ru" else EN
