import json
import pandas as pd
import xml.etree.ElementTree as ET

INPUT_FILE = "final_output.json"
EXCEL_FILE = "PID_Bill_of_Materials.xlsx"
XML_FILE = "PID_Data.xml"

def main():
    # 1. Load Data
    try:
        with open(INPUT_FILE, 'r') as f:
            data = json.load(f)
    except:
        print("❌ No data found. Run pipeline first.")
        return

    # 2. Flatten Data for Excel
    rows = []
    for tile in data:
        for symbol in tile['symbols']:
            rows.append({
                "Tile_Name": tile['tile'],
                "Symbol_Type": symbol['final_label'],
                "Confidence": symbol['confidence'],
                "AI_Original_Guess": symbol['original_ai_label'],
                "Coordinates": str(symbol['bbox'])
            })
    
    if not rows:
        print("⚠️ No symbols were found in the JSON file.")
        return

    # 3. Save to Excel
    df = pd.DataFrame(rows)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"✅ Excel Generated: {EXCEL_FILE}")

    # 4. Save to XML (Interchange Format)
    root = ET.Element("PID_Extraction")
    for row in rows:
        item = ET.SubElement(root, "Component")
        ET.SubElement(item, "Type").text = row['Symbol_Type']
        ET.SubElement(item, "Location").text = row['Coordinates']
        ET.SubElement(item, "Source").text = row['Tile_Name']
        ET.SubElement(item, "Confidence").text = row['Confidence']

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)
    print(f" XML Generated: {XML_FILE}")

if __name__ == "__main__":
    # Install pandas if missing
    # pip install pandas openpyxl
    main()