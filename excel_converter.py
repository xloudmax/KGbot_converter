# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from xlrd import open_workbook
import uuid
import csv
import sys, getopt

import xlsxwriter


def readBiDictionRelations(excelPath):
    wb = open_workbook(excelPath)
    sheet_birelations = wb.sheets()[2]
    bdRelationDict = {}

    for row in range(1, sheet_birelations.nrows):
        bdRelation = {}
        bdRelation["orig"]= sheet_birelations.cell_value(row, 0)
        bdRelation["forward"] = sheet_birelations.cell_value(row, 1)
        bdRelation["backward"] = sheet_birelations.cell_value(row, 2)
        bdRelationDict[bdRelation["orig"]] = bdRelation

    return bdRelationDict

def convertFile(excelPath, withBiDirection):
    wb = open_workbook(excelPath)
    sheet_entities = wb.sheets()[0]
    nameIdMap = {}

    nodes = []
    for row in range(1, sheet_entities.nrows):
        node = {}
        node["node_id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS,sheet_entities.cell_value(row, 0)))
        node["node_name"] = sheet_entities.cell_value(row, 0)

        nameIdMap[node["node_name"]] = node["node_id"]

        node["node_type"] = sheet_entities.cell_value(row, 1)
        properties = []

        for col in range(2, sheet_entities.ncols):
            pName = sheet_entities.cell_value(0, col)
            pValue = sheet_entities.cell_value(row, col)

            if not pValue:
                continue

            property = {}
            property["name"] = pName
            property["value"] = pValue

            properties.append(property)

        node["properties"] = properties

        nodes.append(node)

    bdRelationDict = readBiDictionRelations(excelPath)

    sheet_edges = wb.sheets()[1]
    relations = []
    for row in range(1, sheet_edges.nrows):
        rType = sheet_edges.cell_value(row, 0)
        sName = sheet_edges.cell_value(row, 1)

        if not sName in nameIdMap:
            continue

        sId = nameIdMap[sName]

        tName = sheet_edges.cell_value(row, 2)

        if not tName in nameIdMap:
            continue

        tId = nameIdMap[tName]

        if not withBiDirection:
            relation = {}
            relation["type"] = rType
            relation["source_id"] = sId
            relation["target_id"] = tId

            relations.append(relation)
        else:
            if not rType in bdRelationDict.keys():
                relation = {}
                relation["type"] = rType
                relation["source_id"] = sId
                relation["target_id"] = tId

                relations.append(relation)
            else:
                bdRelation = bdRelationDict[rType]

                fr = {}
                fr["type"] = bdRelation["forward"]
                fr["source_id"] = sId
                fr["target_id"] = tId

                relations.append(fr)

                br = {}
                br["type"] = bdRelation["backward"]
                br["source_id"] = tId
                br["target_id"] = sId

                relations.append(br)

    return nodes, relations


def genNewDoc(newPath, nodes, relations):
    workbook = xlsxwriter.Workbook(newPath)
    vertexes_sheet = workbook.add_worksheet("Vertexes")

    vertexes_column_names = ["实体id","实体名","实体标签","引导词","属性名_1","属性值_1","属性名_2","属性值_2","属性名_3", "属性值_3","属性名_4","属性值_4","属性名_5", "属性值_5", "属性名_6", "属性值_6", "属性名_7", "属性值_7", "属性名_8", "属性值_8"]

    col = 0
    for cName in vertexes_column_names:
        vertexes_sheet.write(0, col, cName)
        col += 1

    row = 1
    for node in nodes:
        vertexes_sheet.write(row, 0, node["node_id"])
        vertexes_sheet.write(row, 1, node["node_name"])
        vertexes_sheet.write(row, 2, node["node_type"])

        col = 4
        for property in node["properties"]:
            vertexes_sheet.write(row, col, property["name"])
            vertexes_sheet.write(row, col + 1, property["value"])
            col += 2

        row += 1

    edges_sheet = workbook.add_worksheet("Edges")

    edges_column_names = ["关系类型", "源实体id", "目标实体id"]
    col = 0
    for cName in edges_column_names:
        edges_sheet.write(0, col, cName)
        col += 1

    row = 1
    for relation in relations:
        edges_sheet.write(row, 0, relation["type"])
        edges_sheet.write(row, 1, relation["source_id"])
        edges_sheet.write(row, 2, relation["target_id"])

        row += 1

    workbook.close()

if __name__ == '__main__':

    argv = sys.argv[1:]
    inputfile = r'C:\Users\23038\Desktop\Converter\input.xls'
    outputfile = r'C:\Users\23038\Desktop\Converter\output.xlsx'
    nodes, relations = convertFile(inputfile, True)
    genNewDoc(outputfile, nodes, relations)

    print("Finished! " + outputfile + " is generated based on " + inputfile + ".")