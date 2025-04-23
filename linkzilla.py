#!/usr/bin/env python3
import sys
import argparse
import curses
import re
import os
from collections import defaultdict
from urllib.parse import urlparse

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

# Cores e estilos
def col(text, color, background=None, bold=False):
    if not COLOR: return text
    result = f"{color}{text}{Style.RESET_ALL}"
    if background:
        result = f"{background}{result}"
    if bold:
        result = f"{Style.BRIGHT}{result}"
    return result

def organizar_saida(caminho_arquivo):
    grupos = defaultdict(list)
    try:
        with open(caminho_arquivo, encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                partes = [p.strip() for p in linha.split(' - ')]
                url = partes[-1] if partes[-1].startswith('http') else None
                
                if url:
                    parsed_url = urlparse(url)
                    path = parsed_url.path
                    segmento = path.split('/')[1] if path.startswith('/') and len(path.split('/')) > 1 else ''
                    grupo = '/' + segmento if segmento else '/'
                    
                    # Adicione informações de domínio para melhor organização
                    dominio = parsed_url.netloc
                    info_completa = {'url': url, 'linha_original': linha, 'dominio': dominio}
                    grupos[grupo].append(info_completa)
    except Exception as e:
        print(col(f"Erro ao ler o arquivo: {str(e)}", Fore.RED, bold=True))
        sys.exit(1)
    return grupos

def imprimir_grupos(grupos):
    sep = col('━'*80, Fore.CYAN)
    print(sep)
    total_urls = sum(len(items) for items in grupos.values())
    print(col(f"┏━━ Total de Grupos: {len(grupos)}", Fore.GREEN, bold=True))
    print(col(f"┣━━ Total de URLs: {total_urls}", Fore.GREEN, bold=True))
    print(sep)
    
    for grupo in sorted(grupos):
        # Contar quantos domínios únicos em cada grupo
        dominios = set(item['dominio'] for item in grupos[grupo])
        
        print(col(f"┏━━ Grupo: {grupo}", Fore.BLUE, bold=True))
        print(col(f"┣━━ URLs: {len(grupos[grupo])}", Fore.BLUE))
        print(col(f"┗━━ Domínios únicos: {len(dominios)}", Fore.BLUE))
        print(col("─"*70, Fore.CYAN))
        
        for idx, item in enumerate(grupos[grupo]):
            # Destacar partes importantes da URL
            url_parts = re.match(r'(https?://[^/]+)(/.*)', item['url'])
            if url_parts:
                dominio, caminho = url_parts.groups()
                formatted_url = f"{col(dominio, Fore.YELLOW)}{col(caminho, Fore.GREEN)}"
            else:
                formatted_url = col(item['url'], Fore.GREEN)
                
            print(f"  {col(str(idx+1), Fore.WHITE, bold=True)}. {formatted_url}")
            
            # Mostrar info adicional se existir
            if item['linha_original'] != item['url']:
                info_adicional = item['linha_original'].replace(item['url'], '').strip(' -')
                if info_adicional:
                    print(f"     {col('↳', Fore.CYAN)} {col(info_adicional, Fore.WHITE)}")
        
        print()

def visual_menu(grupos):
    def main(stdscr):
        curses.use_default_colors()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, -1)  # Grupos
        curses.init_pair(2, curses.COLOR_CYAN, -1)   # Separadores
        curses.init_pair(3, curses.COLOR_YELLOW, -1) # URLs/Domínios
        curses.init_pair(4, curses.COLOR_WHITE, -1)  # Texto normal
        curses.init_pair(5, curses.COLOR_BLUE, -1)   # Detalhes
        curses.init_pair(6, curses.COLOR_MAGENTA, -1) # Destaques
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Seleção
        
        curses.curs_set(0)
        stdscr.keypad(True)
        folder_names = sorted(grupos.keys())
        current = 0
        offset = 0
        viewing = False
        viewing_offset = 0
        
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            
            # Menu de grupos
            if not viewing:
                title = "LinkZilla: Grupos Encontrados"
                stdscr.addstr(0, 0, title, curses.A_BOLD)
                stdscr.addstr(1, 0, "↑/↓: Navegar | Enter: Ver URLs | q: Sair", curses.color_pair(2))
                stdscr.addstr(2, 0, "━" * (w-1), curses.color_pair(2))
                
                # Estatísticas gerais
                total_urls = sum(len(items) for items in grupos.values())
                stdscr.addstr(3, 0, f"Grupos: {len(grupos)} | URLs: {total_urls}", curses.color_pair(5) | curses.A_BOLD)
                stdscr.addstr(4, 0, "─" * (w-1), curses.color_pair(2))
                
                # Lista de grupos
                for i, folder in enumerate(folder_names[offset:offset + h - 6]):
                    url_count = len(grupos[folder])
                    # Formatação elegante para os nomes dos grupos
                    folder_display = f"{folder} ({url_count} URLs)"
                    
                    if i + offset == current:
                        stdscr.attron(curses.color_pair(7) | curses.A_BOLD)
                        stdscr.addstr(i+5, 0, f" {folder_display} ".ljust(w-1))
                        stdscr.attroff(curses.color_pair(7) | curses.A_BOLD)
                    else:
                        stdscr.addstr(i+5, 0, f" {folder_display}", curses.color_pair(1))
                
            # Visualização de URLs em um grupo
            else:
                selected_group = folder_names[current]
                items = grupos[selected_group]
                
                # Cabeçalho
                stdscr.addstr(0, 0, f"Grupo: ", curses.A_BOLD)
                stdscr.addstr(f"{selected_group}", curses.color_pair(1) | curses.A_BOLD)
                stdscr.addstr(f" ({len(items)} URLs)", curses.color_pair(5))
                stdscr.addstr(1, 0, "↑/↓: Navegar | b: Voltar | q: Sair", curses.color_pair(2))
                stdscr.addstr(2, 0, "━" * (w-1), curses.color_pair(2))
                
                # Lista de URLs
                row = 3
                for i, item in enumerate(items[viewing_offset:]):
                    if row >= h - 1:  # Evitar estouro da tela
                        break
                    
                    # URL formatada
                    url_parts = re.match(r'(https?://[^/]+)(/.*)', item['url'])
                    if url_parts:
                        dominio, caminho = url_parts.groups()
                        
                        # Número do item
                        stdscr.addstr(row, 0, f"{i+viewing_offset+1}. ", curses.A_BOLD)
                        
                        # Domínio e caminho com cores diferentes
                        col_pos = len(f"{i+viewing_offset+1}. ")
                        stdscr.addstr(row, col_pos, dominio, curses.color_pair(3))
                        col_pos += len(dominio)
                        
                        # Verificar se o caminho é muito longo
                        if col_pos + len(caminho) >= w - 1:
                            caminho_display = caminho[:w-col_pos-4] + "..."
                        else:
                            caminho_display = caminho
                            
                        stdscr.addstr(row, col_pos, caminho_display, curses.color_pair(1))
                    else:
                        stdscr.addstr(row, 0, f"{i+viewing_offset+1}. {item['url'][:w-4]}", curses.color_pair(3))
                    
                    row += 1
                    
                    # Informações adicionais, se existirem
                    if item['linha_original'] != item['url']:
                        info_adicional = item['linha_original'].replace(item['url'], '').strip(' -')
                        if info_adicional:
                            # Verificar se a info adicional é muito longa
                            if len(info_adicional) > w - 8:
                                info_adicional = info_adicional[:w-12] + "..."
                                
                            stdscr.addstr(row, 4, f"↳ {info_adicional}", curses.color_pair(4))
                            row += 1
                    
                    # Espaçamento entre itens
                    if i < len(items) - 1:
                        stdscr.addstr(row, 0, "· " * ((w-2)//2), curses.color_pair(2))
                        row += 1
            
            # Barra de status na parte inferior
            status = f"LinkZilla | Total: {sum(len(items) for items in grupos.values())} URLs"
            if viewing:
                status += f" | Mostrando: {viewing_offset+1}-{min(viewing_offset+h-3, len(grupos[selected_group]))}/{len(grupos[selected_group])}"
            stdscr.addstr(h-1, 0, status.ljust(w-1), curses.color_pair(2) | curses.A_REVERSE)
            
            stdscr.refresh()
            c = stdscr.getch()
            
            # Controles globais
            if c in (ord('q'), 27):  # q ou ESC
                break
            
            # Controles quando visualizando URLs
            if viewing:
                if c == ord('b'):  # Voltar para a lista de grupos
                    viewing = False
                    viewing_offset = 0
                elif c == curses.KEY_DOWN:  # Rolar para baixo nas URLs
                    if viewing_offset < len(grupos[folder_names[current]]) - 1:
                        viewing_offset += 1
                elif c == curses.KEY_UP:  # Rolar para cima nas URLs
                    if viewing_offset > 0:
                        viewing_offset -= 1
            
            # Controles no menu de grupos
            else:
                if c == curses.KEY_DOWN and current < len(folder_names)-1:
                    current += 1
                    if current - offset >= h - 6:
                        offset += 1
                elif c == curses.KEY_UP and current > 0:
                    current -= 1
                    if current < offset:
                        offset -= 1
                elif c in (10, 13):  # Enter
                    viewing = True
                    viewing_offset = 0
    
    try:
        curses.wrapper(main)
    except Exception as e:
        print(col(f"Erro no modo visual: {e}", Fore.RED, bold=True))
        print("Voltando para modo texto...")
        imprimir_grupos(grupos)

def main():
    parser = argparse.ArgumentParser(description='LinkZilla: Organiza e exibe resultados do gospider')
    parser.add_argument('arquivo', help='Arquivo de saída do gospider (.txt)')
    parser.add_argument('--visual', action='store_true', help='Menu visual interativo')
    args = parser.parse_args()

    # Verificar se o arquivo existe
    if not os.path.isfile(args.arquivo):
        print(col("Erro: Arquivo não encontrado!", Fore.RED, bold=True))
        sys.exit(1)

    print(col("╔════════════════════════╗", Fore.CYAN))
    print(col("║ LinkZilla By Thome07   ║", Fore.CYAN, bold=True))
    print(col("╚════════════════════════╝", Fore.CYAN))
    print(f"\n{col('✓ Modo', Fore.GREEN)} {'Visual' if args.visual else 'Textual'}")
    print(f"{col('✓ Arquivo de entrada', Fore.GREEN)} {args.arquivo}")
    print()

    grupos = organizar_saida(args.arquivo)
    
    if not grupos:
        print(col("⚠ Nenhum URL encontrado no arquivo.", Fore.YELLOW, bold=True))
        sys.exit(0)

    if args.visual:
        visual_menu(grupos)
    else:
        imprimir_grupos(grupos)

if __name__ == '__main__':
    main()
