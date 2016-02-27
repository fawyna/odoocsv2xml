# -*- coding: utf-8 -*-
# based on these codes
# http://code.activestate.com/recipes/577423-convert-csv-to-xml/
# https://gist.github.com/bealdav/0d6f4ff4cda4b8820b22

# convert csv files from Odoo into xml files
# csv is easy to maintain but xml data have noupdate feature
# customer fills up the .xls sheet, then we turn it into .csv
# then we use this script to convert it to .xml

### HOW TO USE: ###
# Export CSV from any Odoo list view
# Put this python script in the same folder as the csv file
# The csv file MUST be named with the model and end with .csv, e.g. sale.order.csv
# The headers for the csv file & model MUST be the same as the actual Odoo export
# This is because this script reads the field type from the way Odoo generates it in the .csv
# csv should have 'id' as first column - you can set this id to your requirement
# ambiguous columns: if column is char type but contains float string, should have special suffix on column name '|char'

### Relational fields ###
# Automatic relation field One2many is NOT supported
# In order to use One2many relation field, edit the csv file and enter the IDs to relate to (do not use purely numbers)

# relational fields notation in csv should be: myfield_id/id for m2o or myfield_ids/id for m2m

# v0.1

import csv
import glob

NOUPDATE = 1
BOOLEAN = ('True', 'False')
ERP_HEADER = """<?xml version="1.0"?>
<openerp>
    <data noupdate="%s">"""

ERP_FOOTER = """
    </data>
</openerp>
"""

# this script will run for as many .csv files in the same folder as this .py script
# for data that should have noupdate = 0 instead of the default noupdate = 1, add
#   the name of the file in this array
FILES_WITH_UPDATE = ('product.product.csv')

def convert_relational_field2xml(tag, value):
    mytag = tag
    for elm in ['/ids', '/id', ':id']:
        mytag = mytag.replace(elm, '')
    if tag[-6:] == 'ids/id':
        # many2many
        line = '%s" eval="[(6, 0, [%s])]"/>\n' % (mytag, value)
    else:
        # many2one
        line = '%s" ref="%s"/>\n' % (mytag, row[i])
    return line


for csv_file in glob.glob('*.csv'):
    no_update = NOUPDATE
    if csv_file in FILES_WITH_UPDATE:
        no_update = 0
    xml_file = csv_file.replace('.', '_').replace('_csv', '_data.xml')
    csv_data = csv.reader(open(csv_file))
    xml_data = open(xml_file, 'w')
    xml_data.write(ERP_HEADER % NOUPDATE + "\n\n\n")
    row_num = 0
    print csv_file
    for row in csv_data:
        if row_num == 0:
            tags = row
            for i in range(len(tags)):
                tags[i] = tags[i].replace(' ', '_')
        else:
            for i in range(len(tags)):
                char = False
                # ambiguous column (char type but contains float string)
                # should be mark by suffix |char
                if tags[i][-5:] == '|char':
                    char = True
                numeric = False
                begin = '    <field name="'
                try:
                    float(row[i])
                    numeric = True
                except Exception:
                    pass
                if tags[i] == 'id':
                    # 'id' column is supposed to be the first left
                    line = ('<record id="%s" model="%s">\n'
                            % (row[i], csv_file[:-4]))
                elif '/' in tags[i] or ':' in tags[i]:
                    # relational fields
                    xml_suffix = convert_relational_field2xml(tags[i], row[i])
                    line = '%s%s' % (begin, xml_suffix)
                elif char:
                    # numeric ghar field
                    line = '%s%s">%s</field>\n' % (begin, tags[i][:-5], row[i])
                elif numeric or row[i] in BOOLEAN:
                    line = '%s%s" eval="%s"/>\n' % (begin, tags[i], row[i])
                else:
                    # basic fields
                    line = '%s%s">%s</field>\n' % (begin, tags[i], row[i])
                if row[i] or tags[i] == 'id':
                    xml_data.write(line)
            xml_data.write('</record>' + "\n\n")
        row_num += 1
    xml_data.write(ERP_FOOTER)
    xml_data.close()