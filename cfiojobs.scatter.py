#!/usr/bin/env python
# coding=utf-8

import re 
import os
import sys
import cfiojobsutil.utils as cu
from openpyxl import Workbook
from openpyxl.chart import (
        BubbleChart,
        ScatterChart,
        Reference,
        Series,
)

#print(sys.argv)
#csv              = sys.argv[1]
# column nuber(Natural number)
key_column_num   = 3
data_columns     = [8,10,11]

key_column_index = key_column_num -1
key_column       = cu.decimal2alphabet(key_column_num)
outputfile       = './' + cu.get_file_name(sys.argv[1])[1][0:30] + '-ScatterChart' + '.xlsx'

wb  = Workbook()
ws  = wb.active 
ws.title = 'ScatterChart'


def count_column_uniq(col_name,work_sheet):
    #skip title 
    start_cell = col_name + '2'
    end_cell   = col_name + str(work_sheet.max_row)
    cell_range = str(start_cell) + ':' + str(end_cell)
#    print(cell_range)
    pattern_name_row_range = dict()
    for t in work_sheet[cell_range]:
        for c in t:
            if c.value in pattern_name_row_range.keys() :
                pattern_name_row_range[c.value].append(c.row)
            else :
                pattern_name_row_range[c.value] = list()
                pattern_name_row_range[c.value].append(c.row)
    return pattern_name_row_range 

# plot ScatterChart
def draw_pattern_scatterchart(data_work_sheet, data_rows_seq, data_columns_list, chart_position, chart_title):
    chart = ScatterChart()
    chart.title = str(chart_title)
    #chart.style = 13
    #chart.layout = 
    chart.legend.position = 't' 
    #chart.graphical_properties = 
    #chart.varyColors = 'blue' 
    #chart.scatterStyle = 'marker'
    chart.x_axis.title = data_work_sheet.title[0:15] + '... samples'
    chart.y_axis.title = 'lantency(ms)'
    # x ray values, get min and max row from pattern_col 
    xvalues = Reference(data_work_sheet, min_col=1, min_row=data_rows_seq[0], max_row=data_rows_seq[-1])
    for i in data_columns_list :
        #print(data_work_sheet.cell(row=1,column=i).value)
        Chart_title = data_work_sheet.cell(row=1,column=i).value
        yvalues = Reference(data_work_sheet, min_col=i, min_row=data_rows_seq[0], max_row=data_rows_seq[-1])
        series  = Series(yvalues, xvalues, title=Chart_title)
        chart.series.append(series)
    #print(chart.series[0])
    # Style the lines
    for i in range(len(data_columns_list)) :
        s1 = chart.series[i]
        #s1.marker.symbol = "triangle"
        s1.marker.symbol = "circle"
        #s1.marker.graphicalProperties.solidFill = "FF0000" # Marker filling
        #s1.marker.graphicalProperties.line.solidFill = "FF0000" # Marker outline
        s1.graphicalProperties.line.noFill = True 
#    print(wb.chartsheets)
    wb['ScatterChart'].add_chart(chart, chart_position)

# plot BubbleChart 
def draw_pattern_bubblechart(data_work_sheet, data_rows_seq, data_columns_list, chart_position, chart_title):
    chart = BubbleChart()
    chart.title = str(chart_title)
    chart.style = 18
    chart.x_axis.title = data_work_sheet.title[0:15] + '... samples'
    chart.y_axis.title = 'lantency(ms)'
    xvalues = Reference(data_work_sheet, min_col=1, min_row=data_rows_seq[0], max_row=data_rows_seq[-1])
    for i in data_columns_list :
        BubbleChart_title = data_work_sheet.cell(row=1,column=i).value
        yvalues = Reference(data_work_sheet, min_col=i, min_row=data_rows_seq[0], max_row=data_rows_seq[-1])
        size    = Reference(data_work_sheet, min_col=i, min_row=data_rows_seq[0], max_row=data_rows_seq[-1])
        series  = Series(values=yvalues, xvalues=xvalues, zvalues=size, title=BubbleChart_title)
        chart.series.append(series)
    wb['ScatterChart'].add_chart(chart, chart_position)

csv_num=0
for csv in sys.argv[1:]:
    # one sheet one column 
    #global chart_column_num 
    chart_column_position = cu.decimal2alphabet(csv_num * 8 + 1)
    csv_num = csv_num + 1
    # add row to Workbook
    tmp_sheet_name = cu.get_file_name(csv)[1][0:30]
    #print(cu.load_csv(csv))
    wb.create_sheet(title=tmp_sheet_name)
    for row in cu.load_csv(csv, sort_sheet=True, sort_column_index=key_column_index):
        wb[tmp_sheet_name].append(row)
    # get pattern_rows_list 
    pattern_rows_list = count_column_uniq(key_column, wb[tmp_sheet_name])
    #print(pattern_rows_list.keys())
    chart_num = 0
    #print(cu.pattern_filter(pattern_rows_list.keys()))
    for pattern_name in cu.pattern_filter(pattern_rows_list.keys()):
        #global chart_num 
        # count chart number
    #    chart_num=len(wb.chartsheets) * 10 + 1
        # chart default width(8 columns) 15 height 7.5(16cells) 
        chart_row_position   = str(chart_num * 16 + 1)
        chart_num = chart_num + 1
        chart_position  = chart_column_position + chart_row_position 
    #    print(position)
        draw_pattern_scatterchart(wb[tmp_sheet_name], pattern_rows_list[pattern_name], data_columns, chart_position, pattern_name)

wb.save(outputfile)
