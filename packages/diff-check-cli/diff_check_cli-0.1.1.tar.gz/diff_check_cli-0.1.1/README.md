# diff-check-cli

Уникальный CLI-инструмент для сравнения, патчинга и интерактивного применения изменений между файлами, директориями и git-объектами.

## Возможности
- Сравнение файлов с цветной подсветкой изменений
- Сравнение в две колонки (side-by-side)
- Мини-карта изменений и резюме (summary)
- Генерация и применение патчей
- Интерактивный режим с Undo/Redo
- Генерация markdown-отчёта о различиях
- Сравнение директорий с древовидным выводом
- Сравнение git-объектов (файлов, коммитов, веток)

## Установка

```bash
pip install .
```

## Примеры использования

### Сравнение файлов
```bash
diff-check file1.txt file2.txt
```

### Сравнение в две колонки
```bash
diff-check file1.txt file2.txt -s
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
- `-s`, `--side-by-side` — сравнение в две колонки
- `-m`, `--summary` — мини-карта изменений и резюме
- `-p`, `--patch` — сгенерировать патч
- `-a`, `--apply` — применить патч
- `-i`, `--interactive` — интерактивный режим с Undo/Redo
- `-r`, `--report` — сохранить отчёт о различиях в markdown-файл
- `-t`, `--tree` — сравнить директории с древовидным выводом
- `-g`, `--git` — сравнить git-объекты (файлы, коммиты, ветки)

## Совместимость флагов
- `-a` несовместим с `-p` и `-i`
- Можно комбинировать, например, `-s -m`, `-p -i`

## Автор
[@shelovesuastra](https://github.com/shelovesuastra)