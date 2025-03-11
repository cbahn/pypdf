from fpdf import FPDF
import argparse
import os
import sys
import re

## PDF Helper class ##

class PDFBuilder:

    # These values define how many pixels away from the corner each
    # image should be placed on the page (vertically and horizontally)
    X_OFFSETS = [20,80,139,198.5]
    Y_OFFSETS = [17,114.5]

    def __init__(self):
        # Create the pdf and initialize a page
        self.pdf = FPDF('L','mm','Letter')
        self.pdf.set_font('Arial','',16)

    def add_page(self):
        self.pdf.add_page()

        # I'm not totally sure, but it seems the PDF prints differently
        # based on the leftmost and topmost item placed on the page.
        # Putting this "_" in the upper left seems to fix it.
        self.pdf.text(0,0,"_")

    def add_image(self, filename, location):
        if location < 0 or location > 7:
            raise ValueError("location syntax out of range")
    
        if location <= 3:
            y = self.Y_OFFSETS[0]
        else:
            y = self.Y_OFFSETS[1]
            location -= 4
        
        x = self.X_OFFSETS[location]
        self.pdf.image(filename, x, y, 50, 75)

    def draw_coordinates(self):
        # For putting coordinates all over the page for troubleshooting purposes
        for x in range (0,300,23):
            for y in range(0,300,8):
                self.pdf.text(x,y,f"{x}x{y}")


    def output(self, filename):
        self.pdf.output(filename, "F")

class LayoutCalculator:
    def __init__(self, layout):
        if layout == "-":
            self.layout = []
            self.page_count = 0
            self.overflow_allowed = True
            return
        

        if not bool(re.fullmatch(r"[0-7-]+", layout)):
            raise ValueError("Layout string contains invalid characters")

        # Ending with a dash indicates that overflow should be allowed
        self.overflow_allowed = False
        if layout.endswith("-"):
            self.overflow_allowed = True
            layout = layout[:-1]

        pages_layout = layout.split("-")

        layout_lookup = []
        page_number = 0
        for page in pages_layout:
            # Sort the layout numbers
            page = "".join(sorted(page))
            for position in page:
                layout_lookup.append( (page_number, int(position)) )

            page_number += 1
        
        self.layout = layout_lookup
        self.page_count = page_number

    def position(self, n: int):
        if n < len(self.layout):
            return self.layout[n]
        
        if not self.overflow_allowed:
            return (None, None)

        n = n - len(self.layout)
        page_number = int( n / 8 ) + self.page_count
        position = n % 8
        return (page_number, position)

def main():
    parser = argparse.ArgumentParser(description="Sticker sheet image templating utility")
    parser.add_argument("-o", "--output", type=str, help="Output file name")
    parser.add_argument("-f", "--folder", type=str, help="Specify a folder with images")
    parser.add_argument("-l", "--layout", type=str, help="Which locations to place images. See manual.")
    
    args = parser.parse_args()

    # Validate settings
    if not args.folder:
        print("Error: You must either specify a file or a folder as input")
        sys.exit(1)

    if args.output:
        if not args.output.lower().endswith(".pdf"):
            print("Error: output file name must end with .pdf")
            sys.exit(1)

    layout_string = "-"
    if args.layout:
        layout_string = args.layout

    layout = LayoutCalculator(layout_string)

    # Create the pdf and initialize a page
    pdf = PDFBuilder()
    pdf.add_page()


    """
    Page Layout is:
    0 1 2 3
    4 5 6 7

    Images should be 510x770

    When the paper is put into the paper tray, it should be placed sticker-side down.
    The upper left corner of the pdf will be printed to the corner of the page deepest in the printer on the left side.
    """

    folder_path = args.folder

    page_number = 0
    image_number = 0
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            (page, pos) = layout.position(image_number)
            if page is None:
                break # No further images should be added
            if page > page_number:
                pdf.add_page()
                page_number += 1

            pdf.add_image(file_path, pos)
            image_number += 1

    # Save the PDF
    output_file = "output.pdf"
    if args.output:
        output_file = args.output

    pdf.output(output_file)
    print(f"Successfully created {output_file}")


if __name__ == "__main__":
   main()