#!/usr/bin/env python3
import sys
import argparse
import curses
from collections import defaultdict
from urllib.parse import urlparse

def organizar_saida(caminho_arquivo):
    grupos = defaultdict(list)
    with open(caminho_arquivo, encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            partes = [p.strip() for p in linha.split(' - ')]
            url = partes[-1] if partes[-1].startswith('http') else None
            path = urlparse(url).path if url else ''
            segmento = path.split('/')[1] if path.startswith('/') and len(path.split('/')) > 1 else ''
            grupo = '/' + segmento if segmento else '/'
            grupos[grupo].append(linha)
    return grupos

def imprimir_grupos(grupos):
    for grupo in sorted(grupos):
        print(grupo)
        for item in grupos[grupo]:
            print(f"  {item}")
        print()

def visual_menu(grupos):
    def main(stdscr):
        curses.curs_set(0)
        stdscr.keypad(True)
        folder_names = sorted(grupos.keys())
        current = 0
        offset = 0
        viewing = False
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            title = (
                "Folders (↑/↓, Enter to open, q to quit)" if not viewing else
                f"Links in {folder_names[current]} (b to go back)"
            )
            stdscr.addstr(0, 0, title[:w-1])
            content = (
                folder_names if not viewing else grupos[folder_names[current]]
            )
            for idx, line in enumerate(content[offset:offset + h - 2]):
                y = idx + 1
                if not viewing and idx + offset == current:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(y, 0, line[:w-1])
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 0, line[:w-1])
            stdscr.refresh()
            k = stdscr.getch()
            if k in (ord('q'), 27):
                break
            if viewing:
                if k == ord('b'):
                    viewing = False
                    offset = 0
            else:
                if k == curses.KEY_DOWN and current < len(folder_names) - 1:
                    current += 1
                    if current - offset >= h - 2:
                        offset += 1
                elif k == curses.KEY_UP and current > 0:
                    current -= 1
                    if current < offset:
                        offset -= 1
                elif k in (curses.KEY_ENTER, 10, 13):
                    viewing = True
                    offset = 0
    curses.wrapper(main)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Organiza e exibe output do gospider.')
    parser.add_argument('arquivo', help='Arquivo de saída do gospider (.txt)')
    parser.add_argument('--visual', action='store_true', help='Menu visual interativo')
    args = parser.parse_args()

    grupos = organizar_saida(args.arquivo)
    if args.visual:
        visual_menu(grupos)
    else:
        imprimir_grupos(grupos)
