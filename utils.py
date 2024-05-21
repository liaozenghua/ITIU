
import pandas as pd
import json
from pandas import json_normalize
import json
import copy
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from openai import OpenAI





my_str='''| Some Title | Some Description             | Some Number |
|------------|------------------------------|-------------|
| Dark Souls | This is a fun game           | 5           |
| Bloodborne | This one is even better      | 2           |
| Sekiro     | This one is also pretty good | 110101      |'''

#markdown_table to json_table
def markdown2json(inp):
    lines = inp.split('\n')
    ret=[]
    keys=[]
    for i,l in enumerate(lines):
        if i==0:
            keys=[_i.strip() for _i in l.split('|')]
        elif i==1: continue
        else:
            ret.append({keys[_i]:v.strip() for _i,v in enumerate(l.split('|')) if  _i>0 and _i<len(keys)-1})
    if 'options' in ret[0].keys():
        for idj,j in enumerate(ret):
            if 'Examples:' in j['List of options']:
                ret[idj]['List of options']=j['List of options'].replace('Examples: ','')
            if 'e.g.,' in j['List of options']:
                ret[idj]['List of options']=j['List of options'].replace('e.g.,','')
            if ', etc.' in j['List of options']:
                ret[idj]['List of options']=j['List of options'].replace(', etc.','')
            ret[idj]['List of options'] = j['List of options'].split(',')
            ret[idj]['List of options'] = [x.strip() for x in ret[idj]['List of options']]
    return ret

def json2markdown(imp):
    inp=copy.deepcopy(imp)
    for idj,j in enumerate(inp):
        inp[idj]['List of options']=', '.join(j['List of options'])
    mark = ''
    data=[]
    heads=list(inp[0].keys())
    for id,i in enumerate(heads):
        data.append([i])
    for id,i in enumerate(inp):
        for idj,j in enumerate(heads):
            data[idj].append(i[data[idj][0]])
    for id,i in enumerate(heads):
        mark=mark+'| '+i+' '*(len(max(data[id], key=len))-len(i))+' '
    mark+='|\n'
    for id, i in enumerate(heads):
        mark += '|'+'-' * (len(max(data[id], key=len))+2)
    mark += '|\n'

    for id,i in enumerate(data[0][1:]):
        for idj,j in enumerate(data):
            mark = mark + '| ' + data[idj][id+1] + ' ' * (len(max(data[idj], key=len)) - len(data[idj][id+1])) + ' '
        mark += '|\n'


    return mark.strip()





#find the string in the middle of two string
def find_mid(string,start,end):

    start_index=string.find(start)+len(start)

    end_index=start_index+string[start_index:].find(end) if string[start_index:].find(end)!=-1 else -1

    return string[start_index:end_index].strip() if end_index!=-1 else string[start_index:].strip()


def structure(intent):

    vague = find_mid(intent, 'Vague:', '\n')
    thought = find_mid(intent, 'Thought:', '\n')
    if vague=='False':
        struct = {'vague': vague, 'thought': thought}
    else:
        explicit_intent = find_mid(intent, 'Explicit intent:', '\n')
        implicit_intent = markdown2json(intent[intent.find('|'):intent.rfind('|')+1])
        struct={'vague':vague,'thought':thought,'explicit_intent':explicit_intent,'implicit_intent':implicit_intent}
    return struct

def dump_json(obj, fname, indent=None):
    with open(fname, 'w', encoding='utf-8') as f:
        return json.dump(obj, f, indent=indent)

def split_en(string,sp):
    if sp in string:
        return string.split(sp)
    else:
        return string

def read_json(fname):
    with open(fname, encoding='utf-8') as f:
        return json.load(f)





@retry(wait=wait_random_exponential(min=3, max=8), stop=stop_after_attempt(6))
def chat(**kwargs):
    return client.chat.completions.create(**kwargs)


@retry(wait=wait_random_exponential(min=3, max=8), stop=stop_after_attempt(6))
def chat3(**kwargs):

    client = OpenAI(
        api_key='',
        base_url=''
    )
    return client.chat.completions.create(**kwargs)

# @retry(wait=wait_random_exponential(min=3, max=8), stop=stop_after_attempt(6))
def chat4(**kwargs):

    client = OpenAI(
        api_key='',
        base_url=''
    )
    return client.chat.completions.create(**kwargs)