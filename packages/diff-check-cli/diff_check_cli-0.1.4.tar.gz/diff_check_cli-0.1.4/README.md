# diff-check-cli

Уникальный CLI-инструмент для сравнения, патчинга и интерактивного применения изменений между файлами, директориями и git-объектами.

## Системные требования
- **Python** версии >= 3.7
- **pip** (установится автоматически при необходимости)
- Для цветного вывода: терминал с поддержкой ANSI-цветов

## Установка

1. Скачайте установочный скрипт:
   ```bash
   wget https://raw.githubusercontent.com/shelovesuastra/diff-check-cli/main/install_diff_check_cli_pip.sh
   # или
   curl -O https://raw.githubusercontent.com/shelovesuastra/diff-check-cli/main/install_diff_check_cli_pip.sh
   ```
2. Запустите скрипт:
   ```bash
   bash install_diff_check_cli_pip.sh
   ```
3. После установки команда будет доступна как:
   ```bash
   diff-check --help
   ```
   Если команда не найдена, перезапустите терминал или добавьте в PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

---

## Возможности
- Мини-карта изменений и резюме (summary)
- Генерация и применение патчей
- Интерактивный режим с Undo/Redo
- Генерация markdown-отчёта о различиях
- Сравнение директорий с древовидным выводом
- Сравнение git-объектов (файлов, коммитов, веток)

## Примеры использования

### Сравнение файлов (side-by-side по умолчанию)
```bash
diff-check file1.txt file2.txt
```

### Мини-карта изменений и резюме
```bash
diff-check file1.txt file2.txt -m
```

### Генерация markdown-отчёта
```bash
diff-check file1.txt file2.txt -r diff.md
```

### Генерация патча
```bash
diff-check file1.txt file2.txt -p > changes.patch
```

### Применение патча
```bash
diff-check file1.txt changes.patch -a
```

### Интерактивный режим с Undo/Redo
```bash
diff-check file1.txt file2.txt -i
```

### Сравнение директорий с древовидным выводом
```bash
diff-check dir1 dir2 -t
```

### Сравнение git-объектов
```bash
diff-check file.py HEAD -g
# или
# diff-check HEAD~1 HEAD -g -- file.py
```

## Флаги и опции

- `-m`, `--summary` — мини-карта изменений и резюме.
  Показывает краткую статистику изменений (добавлено, удалено, изменено) и мини-карту различий.
  Пример:
  ```bash
  diff-check file1.txt file2.txt -m
  ```

- `-p`, `--patch` — сгенерировать патч (diff) между двумя файлами.
  Выводит unified diff, который можно сохранить и применить позже.
  Пример:
  ```bash
  diff-check file1.txt file2.txt -p > changes.patch
  ```

- `-a`, `--apply` — применить патч к файлу.
  Применяет изменения из патч-файла к исходному файлу.
  Пример:
  ```bash
  diff-check file1.txt changes.patch -a
  ```

- `-i`, `--interactive` — интерактивный режим применения изменений с Undo/Redo.
  Позволяет вручную выбирать, какие изменения применять, а какие — пропускать. Можно отменять и повторять действия (Undo/Redo).
  Пример:
  ```bash
  diff-check file1.txt file2.txt -i
  ```

- `-r`, `--report <файл>` — сохранить отчёт о различиях в markdown-файл.
  Генерирует отчёт в формате Markdown для просмотра или отправки коллегам.
  Пример:
  ```bash
  diff-check file1.txt file2.txt -r diff.md
  ```

- `-t`, `--tree` — сравнить директории с древовидным выводом различий.
  Показывает структуру директорий и файлы, которые были добавлены, удалены или изменены, в виде дерева.
  Пример:
  ```bash
  diff-check dir1 dir2 -t
  ```

- `-g`, `--git` — сравнить git-объекты (файлы, коммиты, ветки).
  Позволяет сравнивать содержимое файлов между разными коммитами, ветками или рабочим деревом git-репозитория.
  Примеры:
  ```bash
  diff-check file.py HEAD -g
  diff-check HEAD~1 HEAD -g -- file.py
  ```

### Как работает diff-check-cli без флагов?
Если не указан ни один из специальных флагов (`-p`, `-a`, `-i`, `-r`, `-t`, `-g`), diff-check сравнивает два файла в режиме side-by-side (две колонки) с цветовой подсветкой различий.

### Совместимость флагов
- `-a` несовместим с `-p` и `-i` (нельзя одновременно применять патч и генерировать патч/работать в интерактивном режиме).
- Остальные флаги можно комбинировать, например, `-m` для мини-карты вместе с side-by-side.

## Автор
[@shelovesuastra](https://github.com/shelovesuastra)