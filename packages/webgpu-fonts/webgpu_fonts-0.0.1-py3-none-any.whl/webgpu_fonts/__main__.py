import argparse
from .generate_font_file import generate_msdf_font

def main():
    parser = argparse.ArgumentParser(description="Generate font atlas from TTF file.")
    parser.add_argument("font_file", type=str, help="Path to the TTF font file.")
    parser.add_argument("output_file", type=str, help="Output image file for the font atlas.")
    parser.add_argument("--size", type=float, help="Size of the font in pixels.", default=32.0)
    parser.add_argument("--ascii", help="Generate only ASCII character set.", action='store_true', default=False)
    
    args = parser.parse_args()
    characters = ''.join([chr(i) for i in range(33, 127)]) if args.ascii else None
    atlas = generate_msdf_font(args.font_file, size=args.size, characters=characters)
    atlas.save(args.output_file)

if __name__ == "__main__":
    main()
