from argparse import ArgumentParser
from pathlib import Path

from razerdraw import Frame
from razerdraw.effects import effects
from razerdraw.rows import get_rows

import sys

SYS_DEVICES = Path('/sys/bus/hid/drivers/razerkbd/')


def draw_image(args):
    frame = Frame()
    for i, row in enumerate(get_rows(args.image)):
        frame.set_row(i, row)
    frame.draw(args.device)


def play_effect(args):
    effects.get(args.effect).play(args.device)


def arg_device(val):
    value = Path(val)
    if not value.exists():
        value = SYS_DEVICES / val
    if not value.exists():
        raise FileNotFoundError(value)
    return value


def arg_path(val):
    value = Path(val)
    if not value.exists():
        raise FileNotFoundError(value)
    return value


def main():
    parser = ArgumentParser('razerdraw', description='Draws on the Razer keyboard.')
    parser.add_argument('device', type=arg_device,
                        help='The path to the device. May just be the device identifier.')
    subparsers = parser.add_subparsers()

    image = subparsers.add_parser('image')  # type: ArgumentParser
    image.add_argument('image', type=arg_path,
                       help='The image to draw on the keyboard. Should be 22x6, may be JPEG, PNG, or CSV.')
    image.set_defaults(func=draw_image)

    effect = subparsers.add_parser('effect')  # type: ArgumentParser
    effect.add_argument('effect', choices=list(effects.keys()), help='The effect to play on the keyboard.')
    effect.set_defaults(func=play_effect)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == '__main__':
    main()
