import xlsxwriter
import os


async def write_data_excel(columns, data, file_path='data'):
    directory_path = 'data/users'
    os.makedirs(directory_path, exist_ok=True)

    excel_file_path = os.path.join(directory_path, file_path+'.xlsx')
    workbook = xlsxwriter.Workbook(excel_file_path)
    sheet = workbook.add_worksheet()

    bold_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFFF00'})
    header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#00BFFF', 'font_color': '#FFFFFF'})
    data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

    for col_num, header_text in enumerate(columns):
        sheet.write(0, col_num, header_text, header_format)

    for row_num, row_data in enumerate(data, start=1):
        for col_num, cell_data in enumerate(row_data):
            sheet.write(row_num, col_num, cell_data, data_format)

    workbook.close()
    return excel_file_path
