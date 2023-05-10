import xlsxwriter

expenses = (
    ['Rent', 1000 , 'wayne'],
    ['Gas',   100, 'Tommy' ],
    ['Food',  300, ' Jenny'],
    ['Gym',    50, 'Harry'],
)

workbook = xlsxwriter.Workbook('Expenses01.xlsx')
worksheet = workbook.add_worksheet()
worksheet2 = workbook.add_worksheet('TEST FOR NEW TAB')
bold = workbook.add_format({'bold': True})
money = workbook.add_format({'num_format': '$#,##0'})
worksheet.write('A1', 'Item', bold)
worksheet.write('B1', 'Cost', bold)
row = 0
col = 0

for item, cost, name  in (expenses):
    worksheet.write(row, col,     item)
    worksheet.write(row, col + 2, cost)
    worksheet.write(row, col + 3, name)
    row += 1

worksheet.write(row, 0, 'Total', bold)
worksheet.write(row, 1, '=SUM(B1:B4)', money)

workbook.close()