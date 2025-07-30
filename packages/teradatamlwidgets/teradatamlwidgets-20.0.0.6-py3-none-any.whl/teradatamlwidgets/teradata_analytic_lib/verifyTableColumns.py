# -*- coding: utf-8 -*-
'''
Copyright © 2024 by Teradata.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


def verifyTableName(tableName, single_quotes=False):
    # Must not be empty
    # Must not contain a any for of quote
    # Return with quotes around : double quotes (default) for identifiers or single quotes for use for literals
    # Otherwise raise exception
    if tableName and ('"' not in tableName) and ("'" not in tableName):
        if single_quotes:
            return "'"+tableName+"'"
        else:
            return '"'+tableName+'"'
    else:
        raise Exception('Illegal Table Name', tableName)

def verifyDatabaseName(databaseName, single_quotes=False):
    # Must not be empty
    # Must not contain a any for of quote
    # Return with quotes around : double quotes (default) for identifiers or single quotes for use for literals
    if databaseName and ('"' not in databaseName) and ("'" not in databaseName):
        if single_quotes:
            return "'"+databaseName+"'"
        else:
            return '"'+databaseName+'"'
    else:
        raise Exception('Illegal Database Name', databaseName)

def verifyColumnName(columnName, single_quotes=False):
    # Must not be empty
    # Must not contain a any for of quote
    # Return with quotes around : double quotes (default) for identifiers or single quotes for use for literals
    if columnName and ('"' not in columnName) and ("'" not in columnName):
        if single_quotes:
            return "'"+columnName+"'"
        else:
            return '"'+columnName+'"'
    else:
        raise Exception('Illegal Column Name', columnName)


def verifyModelName(modelName):
    # Model names should not be empty
    # Model names should never have any form of quotes
    # Return with single quotes as used as literal expression
    if modelName and ('"' not in modelName) and ("'" not in modelName):
        return "'"+modelName+"'"
    else:
        raise Exception('Illegal Model Name', modelName)

def verifyAttribute(attributeValue):
    # Attributes should never have single quotes
    if (not attributeValue) or ("'" not in attributeValue):
        return attributeValue
    else:
        raise Exception('Illegal Attribute Value', attributeValue)

def verifyQueryExpr(attributeValue):
    # Expressions should not have new statements
    if (";" not in attributeValue):
        return attributeValue
    else:
        raise Exception('Illegal Attribute Value', attributeValue)


def verifyLocation(locationValue):
    # Location names should not be empty
    # Location names should never have any form of quotes
    # Return with single quotes as used as literal expression
    if locationValue and ('"' not in locationValue) and ("'" not in locationValue):
        return "'"+locationValue+"'"
    else:
        raise Exception('Illegal Location Name', locationValue)


def verifyQualifiedTableName(databaseName, tableName):
    # verify full qualified name with optional databaseName and table name
    if not databaseName:
        return verifyTableName(tableName)
    return verifyDatabaseName(databaseName) + "." + verifyTableName(tableName)


