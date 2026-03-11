## Objectify-AI iOS (SwiftUI)

Это простой SwiftUI‑клиент под твой FastAPI backend.

Структура:
- `ObjectifyAIApp.swift` — точка входа приложения.
- `AppViewModel.swift` — логика авторизации, подписки и identify.
- `APIClient.swift` — HTTP‑клиент, работа с токенами и multipart.
- `Views/AuthView.swift` — экран регистрации/логина (через /register).
- `Views/MainView.swift` — главный экран, подписка и загрузка картинки.
- `Views/ImagePicker.swift` — выбор картинки через Photos.

### 1. Настройка проекта в Xcode

1. Открой Xcode → **File → New → Project…**
2. Шаблон: **iOS → App**.
3. Product Name: `ObjectifyAI` (любое имя).
4. Interface: **SwiftUI**, Language: **Swift**.
5. Сохрани проект (например, в `frontend-ios/xcode-project` или рядом с репо).

Дальше есть два варианта:

#### Вариант A (рекомендуемый): скопировать файлы

1. В Finder открой папку `frontend-ios`.
2. Скопируй содержимое файлов:
   - `ObjectifyAIApp.swift`
   - `AppViewModel.swift`
   - `APIClient.swift`
   - `Views/AuthView.swift`
   - `Views/MainView.swift`
   - `Views/ImagePicker.swift`
3. В Xcode:
   - Замени содержимое автоматически созданного `App` файла своим кодом из `ObjectifyAIApp.swift`.
   - Создай новые Swift‑файлы с теми же именами и вставь соответствующий код.

#### Вариант B: добавить файлы в проект

1. В Xcode кликни по синему корню проекта (в Project navigator).
2. **File → Add Files to "ObjectifyAI"…**
3. Выбери файлы из `frontend-ios` и `frontend-ios/Views`.
4. Убедись, что стоит галочка **Add to targets** для iOS‑таргета.

### 2. Настройка доступа к backend

Открой `APIClient.swift` и найди `APIConfig`:

- `baseURL` — URL твоего backend’а:
  - для локального: `http://127.0.0.1:8081` (на реальном устройстве нужен адрес в сети, не `localhost`).
- `apiKey` — значение переменной окружения `api` на backend.
- `signatureSecret` — значение переменной окружения `signature` на backend.

Также при необходимости скорректируй модель `IdentifyResult` под фактический JSON, который возвращает `/identify`.

### 3. Запуск

1. Убедись, что FastAPI backend запущен и слушает тот порт, который указан в `baseURL`.
2. В Xcode выбери:
   - таргет приложения,
   - схему (Device / Simulator).
3. Нажми **Run** (Cmd+R).

Флоу в приложении:
- На первом экране введи `username` и `password` (минимум 8 символов) и нажми **Register & Login**.
- Клиент отправит `/register` с HMAC‑подписью, получит `access_token` и `refresh_token`, сохранит их.
- Затем на главном экране:
  - увидишь дату окончания trial/subscription,
  - статус подписки (`is_subbed`),
  - можешь нажать **Subscribe** для вызова `/subscribe`,
  - выбрать картинку и отправить её на `/identify`.

Токены автоматически обновляются через `/refresh`, если `access_token` протух (при ответе 401).

