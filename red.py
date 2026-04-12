"""
RED-Python — Remove Empty Directories
======================================
Entry point with dual mode:
  • No arguments  → launches the GUI
  • With arguments → runs in CLI mode

CLI usage:
  python red.py --scan <path> [<path2> ...] [options]

Options:
  --dry-run            Simulate: list what would be deleted, delete nothing
  --permanent          Delete permanently (default: send to Recycle Bin)
  --max-depth N        Maximum recursion depth (0 = unlimited)
  --min-age N          Only delete dirs older than N hours
  --no-empty-files     Do NOT treat 0-byte files as empty
  --scan-hidden        Include hidden and system folders
  --follow-symlinks    Follow symbolic links
  --export FILE        Save results to FILE (.csv or .txt)
  --quiet              Suppress per-item output, show only summary
"""

import sys
import os


def _run_gui():
    from app import App
    App().mainloop()


def _run_cli(args):
    import argparse
    import csv
    from config import Settings
    from core import Scanner, ScanResult

    parser = argparse.ArgumentParser(
        prog='red',
        description='Remove Empty Directories — find and delete empty folders.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--scan', metavar='PATH', nargs='+', required=True,
                        help='One or more root directories to scan')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate; do not delete anything')
    parser.add_argument('--permanent', action='store_true',
                        help='Delete permanently (default: Recycle Bin)')
    parser.add_argument('--max-depth', type=int, default=0, metavar='N')
    parser.add_argument('--min-age', type=int, default=0, metavar='HOURS')
    parser.add_argument('--no-empty-files', action='store_true')
    parser.add_argument('--scan-hidden', action='store_true')
    parser.add_argument('--follow-symlinks', action='store_true')
    parser.add_argument('--export', metavar='FILE')
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(args)

    settings = Settings().load()
    if ns.dry_run:
        settings['delete_mode'] = 'simulate'
    elif ns.permanent:
        settings['delete_mode'] = 'permanent'
    else:
        settings['delete_mode'] = 'recycle'

    settings['max_depth']       = ns.max_depth
    settings['min_age_hours']   = ns.min_age
    settings['ignore_empty_files'] = not ns.no_empty_files
    settings['scan_hidden']     = ns.scan_hidden
    settings['follow_symlinks'] = ns.follow_symlinks

    results = []
    done_event = __import__('threading').Event()

    def on_found(r: ScanResult):
        results.append(r)
        if not ns.quiet:
            tag = {'empty': '[VACÍA]', 'protected': '[PROT.]', 'error': '[ERROR]'}.get(
                r.status, r.status)
            print(f'{tag} {r.path}')

    def on_log(msg):
        if not ns.quiet:
            print(msg)

    def on_done(count):
        done_event.set()

    scanner = Scanner(settings=settings, on_found=on_found,
                      on_log=on_log, on_done=on_done)
    scanner.scan(ns.scan)
    done_event.wait()

    empty = [r for r in results if r.status == 'empty']
    print(f'\n{len(empty)} carpetas vacías encontradas.')

    if not empty:
        return

    if ns.export:
        _export_results(results, ns.export)
        print(f'Resultados exportados a: {ns.export}')

    if ns.dry_run:
        print('Modo simulación — no se eliminó nada.')
        return

    # Delete
    import threading
    del_done = threading.Event()
    total_bytes = [0]

    def on_deleted(r):
        pass

    def on_del_done(count, freed):
        total_bytes[0] = freed
        del_done.set()

    from core import Cleaner
    cleaner = Cleaner(settings=settings, on_deleted=on_deleted,
                      on_log=on_log, on_done=on_del_done)
    cleaner.delete(empty)
    del_done.wait()

    mb = total_bytes[0] / (1024 * 1024)
    print(f'\nEliminación completada. {mb:.2f} MB liberados.')


def _export_results(results, path):
    import csv
    try:
        if path.lower().endswith('.csv'):
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['Ruta', 'Estado', 'Nivel'])
                for r in results:
                    w.writerow([r.path, r.status, r.depth])
        else:
            with open(path, 'w', encoding='utf-8') as f:
                for r in results:
                    f.write(f'{r.status}\t{r.path}\n')
    except Exception as e:
        print(f'Error al exportar: {e}')


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    if cli_args:
        _run_cli(cli_args)
    else:
        _run_gui()
