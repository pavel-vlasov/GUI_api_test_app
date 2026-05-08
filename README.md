# GUI API Test App

Приложение для автономного запуска API тестов через MCP-источники (MuleSoft + Confluence), генерацию команд через Claude CLI и формирование HTML отчета.

## Что улучшено для prod-ready GUI

- Неблокирующий запуск оркестратора в фоне (GUI не зависает).
- Валидация обязательных полей перед стартом.
- Управление состоянием кнопок Start/Stop во время выполнения.
- Потокобезопасный вывод логов в интерфейс.
- Обработка ошибок рантайма с выводом в лог.
- Открытие готового HTML отчета из GUI.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка окружения

Создайте `.env` файл:

```env
TOKEN_URL=
CLIENT_ID=
CLIENT_SECRET=
SCOPES=
API_TOKEN=
API_KEY=
MULESOFT_USERNAME=
MULESOFT_PASSWORD=
CONFLUENCE_USER=
CONFLUENCE_API_TOKEN=
```

## Запуск GUI

```bash
python -m ui.gui_runner
```

В UI заполните:
- **MuleSoft URL**
- **Confluence URL**
- **Auth mode** (`oauth` или `static`)
- **Max iterations** (положительное целое)

Затем нажмите **Start**.

## Запуск CLI (альтернатива)

```bash
python -m cli_interface.cli_runner --config .env --auth-mode oauth --output-dir storage
```

## Артефакты после запуска

Все файлы пишутся в `storage/`:
- `api_spec.json`
- `iteration_results.json`
- `session_journal.json`
- `report.html`

## Рекомендации для production

- Храните секреты только в секрет-менеджере (Vault/AWS Secrets Manager/K8s Secrets), а не в git.
- Запускайте GUI под отдельным пользователем с ограниченными правами.
- Настройте ротацию и бэкап `storage/`.
- Добавьте мониторинг падений процесса (systemd/supervisor).
- Используйте фиксированные версии зависимостей и регулярный dependency scan.
