import PyPDF2 as pypdf
import pikepdf
import uuid 
import sys
from pathlib import Path
import os
import csv


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def readform(fname):
 
    pdf = pikepdf.open(fname)
    tempfile = f"TEMP_{uuid.uuid4().hex[:6].upper()}.pdf"
    pdf.save(tempfile)

    pdfobject=open(tempfile,'rb')
    pdf=pypdf.PdfFileReader(pdfobject)
    os.remove(tempfile)
    a = pdf.getFields()

    info_dict = {}

    extension = "[0]" if 'usersign[0]' in a.keys() else ""
    try:
        person_name = a[f"username{extension}"]['/V']['/Name']
    except:
        person_name = ""

    try:
        person_id = a[f"usersign{extension}"]['/V']['/Name']
    except:
        person_id = ""

    try:
        sec_man_id = a[f"sec_mgr_sign{extension}"]['/V']['/Name']
    except:
        sec_man_id = ""

    try:
        supv_id = a[f"supvsign{extension}"]['/V']['/Name']
    except:
        supv_id = ""

    try:
        user_id = a[f"userid{extension}"]['/V']
    except:
        user_id = ""

    try:
        reqorg = a[f"reqorg{extension}"]['/V']
    except:
        reqorg = ""

    try:
        reqsymb = a[f"reqsymb{extension}"]['/V']
    except:
        reqsymb = ""

    try:
        reqemail = a[f"reqemail{extension}"]['/V']
    except:
        reqemail = ""

    try:
        trngdate = a[f"trngdate{extension}"]['/V']
    except:
        trngdate = ""

    try:
        name = a[f"name{extension}"]['/V']
    except:
        name = ""

    info_dict['name'] = name

    info_dict['user_id'] = user_id
    info_dict['reqorg'] = reqorg
    info_dict['reqsymb'] = reqsymb
    info_dict['reqemail'] = reqemail
    info_dict['trngdate'] = trngdate

    info_dict['User ID'] = person_id
    info_dict['Sec Man ID'] = sec_man_id
    info_dict['SupV ID'] = supv_id
    info_dict['DD 2875 Filename'] = str(fname)

    if RepresentsInt(person_id.split(".")[-1]):
        info_dict['User EDIPI sgn'] = int(person_id.split(".")[-1])
    else:
        info_dict['User EDIPI sgn'] = None

    if RepresentsInt(sec_man_id.split(".")[-1]):
        info_dict['Sec Man EDIPI'] = int(sec_man_id.split(".")[-1])
    else:
        info_dict['Sec Man EDIPI'] = None

    if RepresentsInt(supv_id.split(".")[-1]):
        info_dict['SupV EDIPI'] = int(supv_id.split(".")[-1])
    else:
        info_dict['SupV EDIPI'] = None

    return info_dict

def process_dir(pathname):

    meta_list = [
        readform(doc)
        for doc in list(pathname.glob('**/*'))
        if doc.is_file() and doc.suffix == '.pdf'
    ]


    write_to_file(meta_list)

    return True

def process_file(fname):
    if fname.suffix == '.pdf':
        item = readform(fname)
    
    write_to_file([item])
    return True

def write_to_file(data):

    csv_columns = list(data[0].keys())
    outfile = f"Report_{uuid.uuid4().hex[:6].upper()}.csv"
    with open(outfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for item in data:
            writer.writerow(item)


if __name__ == "__main__":
    
    pathname = Path(sys.argv[1])
    
    if pathname.is_dir():
        process_dir(pathname)
    elif pathname.is_file():
        process_file(pathname)
    else:
        print("No File or Directory found!")