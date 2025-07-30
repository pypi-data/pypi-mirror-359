
def parseJsonWithPlaceholders(inputFile):
    '''
    [Description]
        Parse a parameters json file which may not be json compilant due to placeholders.
        Placeholders are converted to strings so that the resulting json file is compliant, e.g. "heel":#heel# -> "heel":"#heel#"
        If the placeholder is already a string, an "s" is added so that the quotes are not droped when
        converting back the file (see rebuildPlaceholders()), e.g. "heel":"#heel#" -> "heel":"s#heel#".
    [Arguments]
        inputFile (str): Path to json file to be parsed.
        ->return (str): Parsed json file as a string.
    '''
    with open(inputFile,'r') as f:
        parameters = [row.strip() for row in f.readlines() if len(row.split('//')) == 1]
        for i,row in enumerate(parameters):
            if '#' in row:
                parsedRow = row.replace(': ',':').replace(' :',':')
                start,end = [pos for pos, char in enumerate(parsedRow) if char == '#'] # ! This will fail if there is more than 1 value with placeholders in the row.
                if len(parsedRow.split(':')) > 1 and '#'+'"' in parsedRow.split(':')[1]:
                    parsedRow = parsedRow[:start]+'s'+parsedRow[start:]
                    if parsedRow[-1] == ',':
                        parsedRow = parsedRow[:-1] + ','
                else:
                    parsedRow = parsedRow[:start]+'"'+parsedRow[start:]
                    parsedRow = parsedRow[:end+2] +'"'+parsedRow[end+2:]
                parameters[i] = parsedRow
    return '\n'.join(parameters)