# 🚀 Настройка GitHub Pages для Web App

## ✅ Шаг 1: Файлы уже загружены

Я уже создал и загрузил необходимые файлы в папку `/docs`:
- `docs/index.html` - главная страница
- `docs/map_location_picker.html` - Web App для выбора локации

## 📋 Шаг 2: Включить GitHub Pages

1. Откройте репозиторий на GitHub: https://github.com/mikwiseman/wai-city-bot

2. Перейдите в **Settings** (Настройки)

3. В левом меню найдите раздел **Pages**

4. В разделе **Source** выберите:
   - **Deploy from a branch**
   
5. В разделе **Branch** выберите:
   - Branch: `main`
   - Folder: `/docs`
   
6. Нажмите **Save**

## ⏳ Шаг 3: Подождать публикации

GitHub Pages обычно публикуется в течение 1-10 минут. Вы увидите зеленую галочку ✅ и сообщение:

> ✅ Your site is published at https://mikwiseman.github.io/wai-city-bot/

## 🔗 Шаг 4: Проверить ссылки

После публикации ваши страницы будут доступны по адресам:

- **Главная страница**: https://mikwiseman.github.io/wai-city-bot/
- **Web App карты**: https://mikwiseman.github.io/wai-city-bot/map_location_picker.html

## 🤖 Шаг 5: Проверить в боте

1. Запустите бота
2. Нажмите кнопку "🗺️ Выбрать место на карте"
3. Должен открыться Web App с картой

## 🔧 Если не работает

### Проверьте статус GitHub Pages:
1. Settings → Pages
2. Посмотрите есть ли ошибки публикации

### Проверьте доступность ссылки:
Откройте в браузере: https://mikwiseman.github.io/wai-city-bot/map_location_picker.html

### Обновите переменную окружения (если нужно):
Добавьте в `.env`:
```
WEBAPP_URL=https://mikwiseman.github.io/wai-city-bot
```

## 📝 Дополнительно

URL по умолчанию уже настроен в коде:
```python
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://mikwiseman.github.io/wai-city-bot")
```

Так что даже без `.env` файла все должно работать после включения GitHub Pages!