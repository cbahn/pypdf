from fpdf import FPDF
import argparse
import os
import sys


#Original Values
# x_values = [23,81,140,199]
# y_values = [15,114]
x_values = [20,80,139,198.5]
y_values = [17,114.5]

def add_image(pdf_object, filename, location):
    if location < 0 or location > 7:
        raise ValueError("location syntax out of range")
    
    if location <= 3:
        y = y_values[0]
    else:
        y = y_values[1]
        location -= 4
    
    x = x_values[location]
    pdf_object.image(filename, x, y, 50, 75)

def main():
    parser = argparse.ArgumentParser(description="Sticker sheet image templating utility")
    parser.add_argument("-o", "--output", type=str, help="Output file name", required=False)
    parser.add_argument("-f", "--folder", type=str, help="Specify a folder with images")
    args = parser.parse_args()

    
    # Create the pdf and initialize a page
    pdf = FPDF('L','mm','Letter')
    pdf.set_font('Arial','',16)
    pdf.add_page()

    # I'm not totally sure, but it seems the PDF prints differently based on the leftmost and topmost 
    # item placed on the page. Putting this "_" in the upper left seems to fix it.
    pdf.text(0,0,"_")


    # This code is for putting coordinates all over the page for troubleshooting purposes
    # for x in range (0,300,23):
    #     for y in range(0,300,8):
    #         pdf.text(x,y,f"{x}x{y}")


    """
    Page Layout is:
    0 1 2 3
    4 5 6 7

    Images should be 510x770

    When the paper is put into the paper tray, it should be placed sticker-side down.
    The upper left corner of the pdf will be printed to the corner of the page deepest in the printer on the left side.
    """

    if not args.folder:
        print("You must either specify a file or a folder as input")
        sys.exit(1)

    folder_path = args.folder
    pos_iter = 0

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            if pos_iter > 7:
                pdf.add_page()
                pdf.text(0,0,"_")
                pos_iter = 0

            add_image(pdf,file_path, pos_iter)
            pos_iter += 1

    output_file = "output.pdf"
    if args.output:
        output_file = args.output

    pdf.output(output_file, "F")


if __name__ == "__main__":
    main()