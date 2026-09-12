"""OOXML protection, a capability absent from the artifact renderer API.

This is legacy Excel editing protection, NOT encryption or authentication.
"""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
ET.register_namespace('', NS)
def tag(name):
    return '{' + NS + '}' + name


def password_hash(password):
    value = 0
    for index, char in enumerate(password, 1):
        part = ord(char) << index
        value ^= (part & 0x7fff) | (part >> 15)
    return format(value ^ len(password) ^ 0xce4b, 'X')


def protect(path, password, editable=False):
    path = Path(path)
    with ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    styles = ET.fromstring(parts['xl/styles.xml'])
    xfs = styles.find(tag('cellXfs'))
    unlocked = {}
    for name in parts:
        if not name.startswith('xl/worksheets/sheet') or not name.endswith('.xml'):
            continue
        sheet = ET.fromstring(parts[name])
        # Renderer always writes Summary first and Detail second for review books.
        is_detail = editable and name == 'xl/worksheets/sheet2.xml'
        for cell in sheet.iter(tag('c')):
            coordinate = cell.attrib['r']
            if is_detail and coordinate.startswith('R') and coordinate[1:].isdigit() and int(coordinate[1:]) >= 2:
                style = int(cell.get('s', '0'))
                if style not in unlocked:
                    xf = deepcopy(xfs[style])
                    xf.set('applyProtection', '1')
                    prior = xf.find(tag('protection'))
                    if prior is not None:
                        xf.remove(prior)
                    ET.SubElement(xf, tag('protection'), locked='0')
                    unlocked[style] = len(xfs)
                    xfs.append(xf)
                cell.set('s', str(unlocked[style]))
        protection = ET.Element(tag('sheetProtection'), password=password_hash(password), sheet='1', objects='1', scenarios='1', selectLockedCells='0', selectUnlockedCells='0')
        children = list(sheet)
        insert_at = next((i for i, c in enumerate(children) if c.tag in {tag(n) for n in ['protectedRanges','scenarios','autoFilter','sortState','dataConsolidate','customSheetViews','mergeCells','phoneticPr','conditionalFormatting','dataValidations','hyperlinks','printOptions','pageMargins','pageSetup','headerFooter','drawing','tableParts','extLst']}), len(children))
        sheet.insert(insert_at, protection)
        if is_detail:
            count = len(sheet.find(tag('sheetData')))
            dv = ET.Element(tag('dataValidations'), count='1')
            validation = ET.SubElement(dv, tag('dataValidation'), type='custom', allowBlank='0', showErrorMessage='1', errorStyle='stop', errorTitle='Invalid adjustment', error='Use two decimal percent precision, configured limits and protected floor.', sqref=f'R2:R{count}')
            ET.SubElement(validation, tag('formula1')).text = 'AND(ISNUMBER(R2),R2>=INDIRECT("Summary!B13"),R2<=INDIRECT("Summary!B14"),ROUND(R2,4)=R2,ROUND(P2+R2,4)>=W2,ROUND(H2*(1+ROUND(P2+R2,4)),-2)>=X2)'
            children = list(sheet)
            dv_index = next((i for i, c in enumerate(children) if c.tag in {tag(n) for n in ['hyperlinks','printOptions','pageMargins','pageSetup','headerFooter','drawing','tableParts','extLst']}), len(children))
            sheet.insert(dv_index, dv)
        parts[name] = ET.tostring(sheet, encoding='utf-8', xml_declaration=True)
    xfs.set('count', str(len(xfs)))
    parts['xl/styles.xml'] = ET.tostring(styles, encoding='utf-8', xml_declaration=True)
    workbook = ET.fromstring(parts['xl/workbook.xml'])
    sheets = workbook.find(tag('sheets'))
    workbook.insert(list(workbook).index(sheets), ET.Element(tag('workbookProtection'), workbookPassword=password_hash(password), lockStructure='1'))
    calc = workbook.find(tag('calcPr'))
    if calc is None:
        calc = ET.SubElement(workbook, tag('calcPr'))
    calc.set('calcMode', 'auto')
    calc.set('fullCalcOnLoad', '1')
    parts['xl/workbook.xml'] = ET.tostring(workbook, encoding='utf-8', xml_declaration=True)
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
