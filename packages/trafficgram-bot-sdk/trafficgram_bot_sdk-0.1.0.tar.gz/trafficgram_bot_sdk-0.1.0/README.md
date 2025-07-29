
## 🚀 Trafficgram Bot SDK

**Trafficgram Bot SDK** — это простой встраиваемый модуль для Telegram-ботов, который позволяет **автоматически показывать рекламу** пользователям при входе и **проверять подписку** на обязательные каналы.

Поддерживается `aiogram 3.x`.

---

## 🧩 Что делает SDK

SDK перехватывает `/start` и:

* Показывает рекламу **одного из 3 типов**
* Проверяет, подписан ли пользователь на нужные каналы
* Повторно инициирует `/start` после успешной подписки

---

## 📦 Типы рекламы

SDK автоматически работает с тремя типами рекламных форматов:

| Тип  | Назначение                  | Поведение                                                   |
| ---- | --------------------------- | ----------------------------------------------------------- |
| `H`  | **Header-реклама**          | Отображается сразу при старте. Может содержать медиа/кнопки |
| `NS` | **Необязательная подписка** | Показываются каналы, подписка не обязательна                |
| `OS` | **Обязательная подписка**   | Блокирует дальнейшие действия до подписки                   |

---

## 🔧 Быстрый старт

### 1. Подключение SDK в боте

```python
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sdk import SubscriptionMiddleware

# Базовая настройка бота
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Интеграция SDK
middleware = SubscriptionMiddleware(
    sdk_key="your_project_key",   # Ключ доступа к рекламе
    max_channels=3,               # Максимум каналов на проверку
    dispatcher=dp
)

# Включение middleware
dp.message.middleware(middleware)
dp.callback_query.middleware(middleware)

# Обработка кнопки "🔄 Проверить подписку"
middleware.register_check_subscription_handler(dp)
```

---

### 2. Добавление обычных обработчиков

```python
router_main = Router()

@router_main.message(CommandStart())
async def cmd_start(msg: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Тест", callback_data="test_button")]
    ])
    await msg.answer("Добро пожаловать! Нажмите на кнопку ниже:", reply_markup=keyboard)

@dp.callback_query(F.data == "test_button")
async def test_button_handler(call: types.CallbackQuery):
    await call.answer("Тестовая кнопка сработала!")

dp.include_router(router_main)
```

---

### 3. Запуск бота

```python
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## ✅ Что SDK делает сам

* Вызывает API и получает рекламу
* Отображает контент и кнопки
* Проверяет подписку (если реклама типа NS/OS)
* Повторно отправляет `/start` после рекламы
* Блокирует доступ к функционалу до подписки (если требуется)
* Показывает кнопку "🔄 Проверить подписку"

---

## ⚙️ Дополнительные настройки

При необходимости вы можете изменить стандартное сообщение:

```python
SubscriptionMiddleware(
    sdk_key="your_key",
    dispatcher=dp,
    not_subscribed_message="Подпишитесь на все каналы для доступа к боту!"
)
```