# Press the green button in the gutter to run the script.

from pdf_extractor.extractor import PDFExtractor

if __name__ == '__main__':
    save_dir = "temp/result"
    pdf_path = 'assets/sh_chi_bo.pdf'

    extractor = PDFExtractor(save_dir)
    result = extractor.extract(pdf_path, target_shape=(20, 1), confidence_threshold=0.7)
    print(result)
