import ast

def list2dict(listvar):
    # print(type(listvar))
    dictvar=0
    # print(type(listvar)==list)
    if type(listvar) is list:
        strvar=str(listvar)
        # print(strvar)
        # print(pos2[0])
        # print(pos2[-1])
        if strvar[0]=='[' and strvar[-1]==']': # correcting format issues
            strvar=strvar[1:-1] #trim the string for [ ] characters
            # print(strvar)
            dictvar = ast.literal_eval(strvar)
            # print(type(dictvar))
            # print(dictvar)
    return dictvar