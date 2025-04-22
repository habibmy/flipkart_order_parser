import PyPDF2
import re

def extract_info(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def parse_info(text):
    order_id = extract_info(r"(OD[0-9]{18})", text) 
    invoice_no = extract_info(r"Invoice No:\s+([^,]+)", text)
    invoice_date = extract_info(r"Invoice Date:\s+([^,]+)", text)
    courier_awb_no = extract_info(r"Courier AWB No:\s+([^,]+)", text)
    total_qty = extract_info(r"TOTAL QTY:\s+(\d+)", text)
    total_price = extract_info(r"TOTAL PRICE:\s+(\d+\.\d+)", text)
    awb_no = extract_info(r"AWB No\.?\s*([A-Z0-9]+)", text)
    sku = extract_info(r"SKU ID\s*\|\s*Description.*?\n(?:.*\n){2}([^\s|]+)\s*\|", text)

    data = {
        "Invoice No": invoice_no.split('\n')[0] if invoice_no else None,
        "Order ID": order_id.split('\n')[0].strip() if order_id else None,
        "SKU": sku,
        "Total Price": total_price,
        "Invoice Date": invoice_date,
        "Total Qty": total_qty,
        "Courier AWB No": (courier_awb_no or awb_no or '').split('\n')[0]
    }
    return data

def extract_details_from_pdf(file_stream):
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        results = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                parsed_data = parse_info(text)
                results.append(parsed_data)
        return results
    except Exception as e:
        print("PDF parsing error:", e)
        return []
