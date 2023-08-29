import argparse
from wakeonlan import send_magic_packet

def main(args):
    if args.work:
        send_magic_packet('64:1C:67:96:84:AD')
        send_magic_packet('3C:7C:3F:7A:E9:96')
    elif args.tm or args.desktop:
        send_magic_packet('3C:7C:3F:7A:E9:96')
    elif args.tvt or args.notebook:
        send_magic_packet('64:1C:67:96:84:AD')
    elif args.xeon:
        send_magic_packet('00:E9:9A:08:3B:E7')
    elif args.i3:
        send_magic_packet('00:E9:9A:08:3B:E7')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Envia um pacote mágico para ligar uma máquina.")

    # Adicionar argumentos
    parser.add_argument('--tm', action='store_true', help='Ligar a máquina TM.')
    parser.add_argument('--desktop', action='store_true', help='Ligar a máquina Desktop.')
    parser.add_argument('--tvt', action='store_true', help='Ligar a máquina TVT.')
    parser.add_argument('--notebook', action='store_true', help='Ligar o notebook.')
    parser.add_argument('--work', action='store_true', help='Ligar todas as máquinas.')
    parser.add_argument('--xeon', action='store_true', help='Ligar esxi xeon.')
    parser.add_argument('--i3', action='store_true', help='Ligar esxi i3.')

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.error('Nenhum argumento fornecido. Utilize --help para mais informações.')

    main(args)


'''
python script.py --tm       # para ligar a máquina TM
python script.py --desktop  # para ligar a máquina Desktop
python script.py --tvt      # para ligar a máquina TVT
python script.py --notebook # para ligar o notebook
python script.py --work     # para ligar todas as máquinas
python script.py --xeon     # Ligar esxi xeon
python script.py --i3       # Ligar esxi i3
'''
