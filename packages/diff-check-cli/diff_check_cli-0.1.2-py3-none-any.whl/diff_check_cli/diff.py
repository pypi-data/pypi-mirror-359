from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from difflib import unified_diff
from rich.table import Table
from pathlib import Path
from rich.tree import Tree
import subprocess

console = Console()

def show_diff(file1, file2, summary=False):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    diff = list(unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm=''))
    if summary:
        add, delete, change = 0, 0, 0
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                add += 1
            elif line.startswith('-') and not line.startswith('---'):
                delete += 1
            elif line.startswith('@@'):
                change += 1
        console.print(f'[bold magenta]Summary:[/bold magenta] [green]+{add}[/green] [red]-{delete}[/red] [yellow]~{change}[/yellow]')
        console.print('-' * 60)
    if not diff:
        console.print('[green]Файлы идентичны[/green]')
        return
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            console.print(Text(line, style='bold green'))
        elif line.startswith('-') and not line.startswith('---'):
            console.print(Text(line, style='bold red'))
        elif line.startswith('@@'):
            console.print(Text(line, style='yellow'))
        else:
            console.print(line, end='')

def generate_patch(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    diff = unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm='')
    return ''.join(diff)

def apply_patch(file, patch_file):
    import difflib
    import shutil
    from pathlib import Path
    with open(file, 'r', encoding='utf-8') as f:
        original = f.readlines()
    with open(patch_file, 'r', encoding='utf-8') as pf:
        patch = pf.read()
    patched = list(difflib.restore(patch.splitlines(), 2))
    backup = Path(file).with_suffix('.bak')
    shutil.copy(file, backup)
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(patched)
    console.print(f'[green]Патч применён. Оригинал сохранён как {backup}[/green]')

def interactive_apply(file1, file2):
    from difflib import SequenceMatcher
    from prompt_toolkit.shortcuts import yes_no_dialog, button_dialog
    import shutil
    from pathlib import Path

    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    matcher = SequenceMatcher(None, lines1, lines2)
    opcodes = list(matcher.get_opcodes())
    result = []
    history = []
    redo_stack = []
    idx = 0
    while idx < len(opcodes):
        tag, i1, i2, j1, j2 = opcodes[idx]
        if tag == 'equal':
            result.extend(lines1[i1:i2])
            idx += 1
            continue
        console.print(f'Изменение {idx+1}/{len(opcodes)}: {tag}')
        if tag != 'insert':
            console.print('[red]-' + ''.join(lines1[i1:i2]) + '[/red]')
        if tag != 'delete':
            console.print('[green]+' + ''.join(lines2[j1:j2]) + '[/green]')
        action = button_dialog(
            title='Применить изменение?',
            text='Выберите действие:',
            buttons=[('Применить', 'apply'), ('Пропустить', 'skip'), ('Undo', 'undo'), ('Redo', 'redo'), ('Выйти', 'exit')]
        ).run()
        if action == 'apply':
            history.append((idx, list(result)))
            result.extend(lines2[j1:j2])
            redo_stack.clear()
            idx += 1
        elif action == 'skip':
            history.append((idx, list(result)))
            if tag != 'insert':
                result.extend(lines1[i1:i2])
            redo_stack.clear()
            idx += 1
        elif action == 'undo':
            if history:
                last_idx, last_result = history.pop()
                redo_stack.append((idx, list(result)))
                result = list(last_result)
                idx = last_idx
            else:
                console.print('[yellow]Нет изменений для отмены[/yellow]')
        elif action == 'redo':
            if redo_stack:
                next_idx, next_result = redo_stack.pop()
                history.append((idx, list(result)))
                result = list(next_result)
                idx = next_idx
            else:
                console.print('[yellow]Нет изменений для повтора[/yellow]')
        elif action == 'exit':
            break
    backup = Path(file1).with_suffix('.bak')
    shutil.copy(file1, backup)
    with open(file1, 'w', encoding='utf-8') as f:
        f.writelines(result)
    console.print(f'[green]Изменения применены. Оригинал сохранён как {backup}[/green]')

def show_diff_side_by_side(file1, file2, summary=False):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    max_len = max(len(lines1), len(lines2))
    add, delete, change = 0, 0, 0
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column(file1, style="dim", width=50)
    table.add_column(file2, style="dim", width=50)
    for i in range(max_len):
        l1 = lines1[i].rstrip('\n') if i < len(lines1) else ""
        l2 = lines2[i].rstrip('\n') if i < len(lines2) else ""
        if l1 == l2:
            table.add_row(l1, l2)
        else:
            if l1 and not l2:
                delete += 1
            elif l2 and not l1:
                add += 1
            else:
                change += 1
            table.add_row(f'[red]{l1}[/red]', f'[green]{l2}[/green]')
    if summary:
        console.print(f'[bold magenta]Summary:[/bold magenta] [green]+{add}[/green] [red]-{delete}[/red] [yellow]~{change}[/yellow]')
        console.print('-' * 60)
    console.print(table)

def generate_markdown_report(file1, file2):
    from difflib import unified_diff
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    diff = list(unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm=''))
    if not diff:
        return f'# Diff report\n\n**{file1}** и **{file2}** идентичны.'
    md = f'# Diff report\n\n**{file1}** vs **{file2}**\n\n'
    md += '```diff\n' + ''.join(diff) + '\n```\n'
    return md

def compare_directories_tree(dir1, dir2):
    dir1 = Path(dir1)
    dir2 = Path(dir2)
    tree = Tree(f"[bold]{dir1}[/bold] vs [bold]{dir2}[/bold]", guide_style="bold bright_blue")
    def walk(d1, d2, node):
        d1_files = {p.relative_to(d1) for p in d1.rglob('*')}
        d2_files = {p.relative_to(d2) for p in d2.rglob('*')}
        all_files = sorted(d1_files | d2_files)
        for rel_path in all_files:
            p1 = d1 / rel_path
            p2 = d2 / rel_path
            if p1.exists() and not p2.exists():
                node.add(f"[red]- {rel_path}")
            elif p2.exists() and not p1.exists():
                node.add(f"[green]+ {rel_path}")
            elif p1.is_dir() and p2.is_dir():
                sub = node.add(f"[bold]{rel_path}/[/bold]")
                walk(p1, p2, sub)
            elif p1.is_file() and p2.is_file():
                with open(p1, 'r', encoding='utf-8', errors='ignore') as f1, open(p2, 'r', encoding='utf-8', errors='ignore') as f2:
                    if f1.read() != f2.read():
                        node.add(f"[yellow]~ {rel_path}")
    walk(dir1, dir2, tree)
    console.print(tree)

def git_diff(obj1, obj2):
    """Сравнить git-объекты (файлы, коммиты, ветки)."""
    try:
        result = subprocess.run([
            'git', 'diff', f'{obj1}', f'{obj2}'
        ], capture_output=True, text=True, check=True)
        diff = result.stdout
        if not diff:
            console.print('[green]Нет различий между git-объектами[/green]')
            return
        for line in diff.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                console.print(Text(line, style='bold green'))
            elif line.startswith('-') and not line.startswith('---'):
                console.print(Text(line, style='bold red'))
            elif line.startswith('@@'):
                console.print(Text(line, style='yellow'))
            else:
                console.print(line)
    except subprocess.CalledProcessError as e:
        console.print(f'[red]Ошибка git diff: {e}[/red]') 