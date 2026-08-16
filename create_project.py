from pathlib import Path

ROOT = Path(__file__).parent

directories = [
    "app/bot/handlers",
    "app/bot/keyboards",
    "app/bot/states",
    "app/telegram",
    "app/extractor",
    "app/classifier",
    "app/workers",
    "app/database/migrations",
    "app/database/repositories",
    "app/export",
    "app/utils",
    "tests/unit",
    "tests/integration",
    "tests/fixtures",
    "data",
    "exports",
    "sessions",
]

files = [
    "app/__init__.py",
    "app/main.py",
    "app/config.py",

    "app/bot/__init__.py",
    "app/bot/router.py",

    "app/bot/handlers/__init__.py",
    "app/bot/handlers/start.py",
    "app/bot/handlers/sources.py",
    "app/bot/handlers/scan.py",
    "app/bot/handlers/results.py",
    "app/bot/handlers/export.py",
    "app/bot/handlers/settings.py",

    "app/bot/keyboards/__init__.py",
    "app/bot/keyboards/main.py",
    "app/bot/keyboards/sources.py",
    "app/bot/keyboards/scan.py",
    "app/bot/keyboards/results.py",
    "app/bot/keyboards/export.py",

    "app/bot/states/__init__.py",
    "app/bot/states/scan_states.py",

    "app/telegram/__init__.py",
    "app/telegram/userbot_manager.py",
    "app/telegram/source_reader.py",
    "app/telegram/message_reader.py",
    "app/telegram/entity_resolver.py",
    "app/telegram/invite_resolver.py",

    "app/extractor/__init__.py",
    "app/extractor/url_extractor.py",
    "app/extractor/telegram_parser.py",
    "app/extractor/whatsapp_parser.py",
    "app/extractor/normalizer.py",
    "app/extractor/deduplicator.py",

    "app/classifier/__init__.py",
    "app/classifier/link_classifier.py",
    "app/classifier/telegram_classifier.py",
    "app/classifier/whatsapp_classifier.py",

    "app/workers/__init__.py",
    "app/workers/scan_worker.py",
    "app/workers/resolver_worker.py",

    "app/database/__init__.py",
    "app/database/database.py",
    "app/database/models.py",
    "app/database/migrations/001_initial_schema.sql",

    "app/database/repositories/__init__.py",
    "app/database/repositories/user_repo.py",
    "app/database/repositories/source_repo.py",
    "app/database/repositories/scan_repo.py",
    "app/database/repositories/link_repo.py",
    "app/database/repositories/result_repo.py",

    "app/export/__init__.py",
    "app/export/txt_exporter.py",
    "app/export/csv_exporter.py",
    "app/export/json_exporter.py",
    "app/export/xlsx_exporter.py",

    "app/utils/__init__.py",
    "app/utils/logger.py",
    "app/utils/rate_limiter.py",
    "app/utils/retry.py",
    "app/utils/hashing.py",

    "tests/unit/test_url_extractor.py",
    "tests/unit/test_telegram_parser.py",
    "tests/unit/test_whatsapp_parser.py",
    "tests/unit/test_normalizer.py",
    "tests/unit/test_deduplicator.py",
    "tests/unit/test_classifier.py",
    "tests/unit/test_hashing.py",

    "tests/integration/test_database.py",
    "tests/integration/test_scan_pipeline.py",
    "tests/integration/test_export.py",

    "tests/fixtures/sample_messages.json",

    "data/.gitkeep",
    "exports/.gitkeep",
    "sessions/.gitkeep",

    "requirements.txt",
    ".env.example",
    ".gitignore",
    "README.md",
    "pytest.ini",
]

for directory in directories:
    path = ROOT / directory
    path.mkdir(parents=True, exist_ok=True)

for filename in files:
    path = ROOT / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()

print()
print("========================================")
print(" Project structure created successfully")
print("========================================")
print()
print(f"Project: {ROOT}")
print(f"Directories: {len(directories)}")
print(f"Files:       {len(files)}")
print()
print("Existing files were NOT overwritten.")
print("Missing files were created.")

