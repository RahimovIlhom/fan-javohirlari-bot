import xlsxwriter
import os


async def write_data_excel(columns, data, file_path='data'):
    directory_path = 'data/users'
    os.makedirs(directory_path, exist_ok=True)

    excel_file_path = os.path.join(directory_path, file_path+'.xlsx')
    workbook = xlsxwriter.Workbook(excel_file_path)
    sheet = workbook.add_worksheet()

    sheet.write_row(0, 0, columns)

    for row_num, row_data in enumerate(data, start=1):
        sheet.write_row(row_num, 0, row_data)

    workbook.close()

    return excel_file_path
