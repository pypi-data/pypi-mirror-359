import click
from .diff import show_diff

@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--interactive', '-i', is_flag=True, help='Интерактивный режим применения изменений')
@click.option('--patch', '-p', is_flag=True, help='Сгенерировать патч между двумя файлами')
@click.option('--apply', '-a', is_flag=True, help='Применить патч file2 к file1')
@click.option('--side-by-side', '-s', is_flag=True, help='Сравнение в две колонки (side-by-side)')
@click.option('--report', '-r', type=click.Path(), help='Сохранить отчёт о различиях в файл (markdown)')
@click.option('--summary', '-m', is_flag=True, help='Показать мини-карту изменений и резюме')
@click.option('--tree', '-t', is_flag=True, help='Сравнить директории с древовидным выводом различий')
@click.option('--git', '-g', is_flag=True, help='Сравнить git-объекты (файлы, коммиты, ветки)')
def main(file1, file2, interactive, patch, apply, side_by_side, report, summary, tree, git):
    """
    diff-check — CLI для сравнения, патчинга и интерактивного применения изменений между файлами, директориями и git-объектами.

    Примеры использования:

      diff-check dir1 dir2 -t
          Сравнить директории с древовидным выводом различий.

      diff-check file1.txt file2.txt -m
          Сравнить два файла с подсветкой изменений и мини-картой изменений.

      diff-check file1.txt file2.txt -s -m
          Сравнить два файла в две колонки с мини-картой изменений.

      diff-check file1.txt file2.txt -r diff.md
          Сохранить отчёт о различиях в файл (markdown).

      diff-check file1.txt file2.txt -p
          Сгенерировать патч (diff) между двумя файлами.

      diff-check file1.txt file2.txt -i
          Интерактивно применить изменения из file2 к file1.

      diff-check file1.txt file2.txt -p -i
          Показать diff и затем интерактивно применить изменения.

      diff-check file1.txt patchfile -a
          Применить патч patchfile к file1.

      diff-check file.py HEAD -g
          Сравнить рабочий файл с версией из последнего коммита.

      diff-check HEAD~1 HEAD -g -- файл.py
          Сравнить файл между двумя коммитами.

    Флаги несовместимы: -a нельзя использовать с -p или -i одновременно.
    """
    if apply and (patch or interactive):
        raise click.UsageError('Флаг -a/--apply несовместим с -p/--patch и -i/--interactive')
    if patch and interactive:
        from .diff import generate_patch, interactive_apply
        patch_text = generate_patch(file1, file2)
        click.echo(patch_text)
        click.echo('\n[ИНТЕРАКТИВНЫЙ РЕЖИМ]')
        interactive_apply(file1, file2)
    elif patch:
        from .diff import generate_patch
        patch_text = generate_patch(file1, file2)
        click.echo(patch_text)
    elif apply:
        from .diff import apply_patch
        apply_patch(file1, file2)
    elif interactive:
        from .diff import interactive_apply
        interactive_apply(file1, file2)
    elif side_by_side:
        from .diff import show_diff_side_by_side
        show_diff_side_by_side(file1, file2, summary=summary)
    elif report:
        from .diff import generate_markdown_report
        report_text = generate_markdown_report(file1, file2)
        with open(report, 'w', encoding='utf-8') as f:
            f.write(report_text)
        click.echo(f'Отчёт сохранён в {report}')
    elif tree:
        from .diff import compare_directories_tree
        compare_directories_tree(file1, file2)
    elif git:
        from .diff import git_diff
        git_diff(file1, file2)
        return
    else:
        show_diff(file1, file2, summary=summary)

@main.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
def patch(file1, file2):
    """Сгенерировать патч между двумя файлами."""
    from .diff import generate_patch
    patch_text = generate_patch(file1, file2)
    click.echo(patch_text)

@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('patch_file', type=click.Path(exists=True))
def apply(file, patch_file):
    """Применить патч к файлу."""
    from .diff import apply_patch
    apply_patch(file, patch_file)

if __name__ == '__main__':
    main() 