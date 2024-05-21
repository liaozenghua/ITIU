
import os
import copy
import json
from tqdm import tqdm
from utils import *




"""
1. vagueness_judgement_accuracy
"""
def vagueness_judgement(vague,label):
    return bool(vague) == bool(label)




"""
2. missing_details_recover_rate
"""
def missing_details_recover(question_list,label):
    SYS_PROMPT = """You are a helpful assistant and good at judging similarities between phrases. Given a QUESTION and a list of phrases, you should determine if the provided QUESTION semantically matches any of the entries in the list. Directly answer with the phrase in the list if there is any semantic match, and 'None of the above' otherwise. Do not include any explanations and additional information. Remember to strictly follow the format given in the following examples:

1. Example with a semantic match:

### QUESTION:
What is the time frame for the price predictions?

### List of phrases:
- Historical data timeframe and granularity
- Criteria for efficiency
- Specific stocks or market sectors
- Computational resources available
- Type of historical data

### Answer:
Historical data timeframe and granularity

2. Example without a semantic match:

### QUESTION:
What is the time frame for the price predictions?

### List of phrases:
- Metrics or sources to determine popularity
- User's personal style preferences
- Geographic region
- Specific fashion categories

### Answer:
None of the above"""

    USER_PROMPT = """Here is a QUESTION and a list of phrases:

### QUESTION:
{question}

### List of phrases:
{list_str}"""

    label_list=[x['description'].lower() for x in label]
    label_prompt=['- '+x['description'] for x in label]
    label_prompt='\n'.join(label_prompt)
    result={x:False for x in label_list}


    for id,i in enumerate(question_list):
        question = i['Query for user']
        msg = USER_PROMPT.format(question=question, list_str=label_prompt)
        resp = chat4(
            model="gpt-4-turbo-preview",
            messages=[
                {'role': 'system', 'content': SYS_PROMPT},
                {'role': 'user', 'content': msg}
            ],
            temperature=0.7,
            n=1).choices[0].message.content
        if resp != "None of the above":
            resp = resp.lower()
            if resp in label_list:
                result[resp] = True
            else:
                print(f"Error: {resp} not in human intention list:\n{label_prompt}")
    return result


"""
3. summary_intention_coverage_rate
"""
def summary_intention_coverage(question,response,summary):
    SYS_PROMPT = """You are a helpful assistant and good at judging whether a QUESTION-RESPONSE pair is represented in the SUMMARY. Given a QUESTION-RESPONSE pair and SUMMARY, you should determine whether the content of the QUESTION-RESPONSE pair is represented in the provided SUMMARY. If there is any semantic match, answer 'Yes', otherwise 'No'. Do not include any explanation or additional information. Remember to strictly follow the format given in the following examples:

1. Example with a semantic match:

### QUESTION: what type of diabetes research are you interested in?

### RESPONSE: no specific type

### SUMMARY: I need to find the most recent, comprehensive studies on diabetes treatment that are suitable for medical professionals and are not specific to a type of diabetes. The studies should be from the last year, globally relevant, at an intermediate technical level, and published in peer-reviewed journals.

### Answer: Yes

2. Example without a semantic match:

### QUESTION: what is the time frame for the price predictions?

### RESPONSE: historical data timeframe and granularity

### SUMMARY: I need to find the most recent, comprehensive studies on diabetes treatment that are suitable for medical professionals and are not specific to a type of diabetes. The studies should be from the last year, globally relevant, at an intermediate technical level, and published in peer-reviewed journals.

### Answer: No"""

    USER_PROMPT = """Here is a QUESTION-RESPONSE pair and SUMMARY:

### QUESTION: {question}

### RESPONSE: {response}

### SUMMARY: {summary}"""

    msg = USER_PROMPT.format(question=question, response=response,summary=summary)
    resp = chat4(
        model="gpt-4-turbo-preview",
        messages=[
            {'role': 'system', 'content': SYS_PROMPT},
            {'role': 'user', 'content': msg}
        ],
        temperature=0.7,
        n=1).choices[0].message.content


    return resp


"""
5. options_reasonable_rate
"""
def options_reasonable(question,option):
    SYS_PROMPT = """You are a helpful assistant who is good at judging whether the OPTIONS for a QUESTION are reasonable. Given a QUESTION and a List of OPTIONS, you should determine whether each of the OPTIONS in the List of OPTIONS is reasonable. Directly answer with the options in the List of OPTIONS if there is reasonable, and 'None of the above' otherwise. Remember to strictly follow the format given in the following examples:

1. Examples with some reasonable options:

### QUESTION: what type of diabetes research are you interested in?

### List of OPTIONS:
- type 1 diabetes
- type 2 diabetes
- academics and scientists
- gestational diabetes
- medical professionals
- other
- policy makers
- no specific type

### Answer:
- type 1 diabetes
- type 2 diabetes
- gestational diabetes
- other
- no specific type

2. Examples without reasonable options:

### QUESTION: what type of diabetes research are you interested in?

### List of OPTIONS:
- fiction
- non-fiction
- fantasy
- sci-fi
- romance
- historical fiction
- mystery
- thriller
- young adult

### Answer:
None of the above"""

    USER_PROMPT = """Here is a QUESTION and List of OPTIONS:

### QUESTION: {question}

### List of OPTIONS: {option}"""

    option_prompt=['- '+x for x in option]
    option_prompt='/n'.join(option_prompt)

    msg = USER_PROMPT.format(question=question, option=option_prompt)
    resp = chat4(
        model="gpt-4-turbo-preview",
        messages=[
            {'role': 'system', 'content': SYS_PROMPT},
            {'role': 'user', 'content': msg}
        ],
        temperature=0.7,
        n=1).choices[0].message.content
    if resp != "None of the above":
        try:
            resp = [x.replace('- ','') for x in resp.split('\n')]
        except:
            resp=resp.replace('- ','')
        result={}
        for i in resp:
            if i in option:
                result[i] = True
            else:
                result[i] = False

    return result











generate_data=read_json(f"../data/ITIU/finetune_data_test.json")
label_data=[]



struct_data=[]
for id,i in enumerate(generate_data):
    struct= {}
    question_list = []
    user_resonse=[]
    options= []
    miss=[]
    for jd,j in enumerate(i[1:]):

        if jd==0:
            vague=find_mid(j['content'],'[VAGUE] ','\n\n')
            struct["vague"]=vague


        if j['role']=="USER":
            question_list+=markdown2json(j['content'])

        if i[jd]['role']=="USER":
            user_resonse.append({"question":[x["Query for user"].lower() for x in markdown2json(i[jd]['content'])],"response":[x["User's response"].lower() for x in markdown2json(i[jd]['content'])],"summary":find_mid(j['content'],'[SUMMARY] ','\n\n')})

        if i[jd]['role']=="USER":
            options.append({"question":[x["Query for user"].lower() for x in markdown2json(i[jd]['content'])],"option":[x["List of options"].lower() for x in markdown2json(i[jd]['content'])]})

        if i[jd]['role']=="USER":
            miss.append({"question":[x["Query for user"].lower() for x in markdown2json(i[jd]['content'])],"option":[x["List of options"].lower() for x in markdown2json(i[jd]['content'])]})

    struct["question_list"]=question_list
    struct["user_resonse"] = user_resonse
    struct["options"] = options
    struct["misses"] = miss
    struct_data.append(struct)






TASK_NUM = len(generate_data)
results = {}


a = []
align_cnt = 0
for i in range(TASK_NUM):
    if vagueness_judgement(struct_data[i]['vague'],label_data[i]['vague']):
        align_cnt += 1
    if bool(struct_data[i]['vague']) == True:
        a.append(bool(struct_data[i]['vague']))
vagueness_judgement_accuracy = align_cnt / TASK_NUM



miss_list=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True and bool(label_data[i]['vague'])==True:
        miss_list.append(missing_details_recover(struct_data[i]['question_list'],label_data[i]['missing_details']))
totol=0
hit=0
for id,i in enumerate(miss_list):
    t=0
    for grade in i.values():
        if grade==True:
            h=h+1
        t=t+1
    hit=hit+h/t
    totol=totol+1
missing_details_recover_rate=hit/totol



response_list=[]
rate=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True and bool(label_data[i]['vague'])==True:
        for jd,j in enumerate(struct_data[i]['user_resonse']):
            response_list.append(j)
for id,i in enumerate(response_list):
    t=0
    h=0
    for j in range(len(i['question'])):
        hit=summary_intention_coverage(i['question'][j],i['response'][j],i['summary'])
        t=t+1
        h=h+1 if hit.lower()=="yes" else h
    rate.append(h/t)
summary_intention_coverage_rate=sum(rate)/len(rate)



options_list=[]
options_rate=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True:
        for jd,j in enumerate(struct_data[i]['options']):
            options_list.append(j)

for i in range(len(options_list)):
    t=0
    h=0
    for j in range(len(options_list[i]['option'])):
        if options_list[i]['option'][j]!='':
            h=h+1
        t=t+1
    options_rate.append(h/t)
options_presenting_rate=sum(options_rate)/len(options_rate)





reasonable_list=[]
reasonable_rate=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True and bool(label_data[i]['vague'])==True:
        for jd,j in enumerate(struct_data[i]['options']):
            for kd,k in enumerate(j['option']):
                j['option'][kd]=[x.lower().strip() for x in j['option'][kd].split(',')]
            reasonable_list.append(j)

results=[]
start=0
for i in range(start,len(reasonable_list)):
    t=0
    h=0
    for j in range(len(reasonable_list[i]['option'])):
        result=options_reasonable(reasonable_list[i]['question'][j], reasonable_list[i]['option'][j])
        for k in result.keys():
            if result[k]==True:
                h=h+1
            t=t+1
        reasonable_rate.append(h/t)
        results.append(result)
    dump_json(results,'../output/evaluation/reasonable_rate_{}_{}.json'.format(str(start),str(i)))
options_reasonable_rate=sum(reasonable_rate)/len(reasonable_rate)








option_list=[]
option_rate=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True:
        for jd,j in enumerate(struct_data[i]['options']):
            for kd,k in enumerate(j['option']):
                j['option'][kd]=[x.lower().strip() for x in j['option'][kd].split(',')]
            option_list.append(j)
for i in range(len(option_list)):
    t=0
    h=0
    for j in range(len(option_list[i]['option'])):
        t=t+1
        new_option_list = list(filter(None, option_list))
        h=h+len(new_option_list[i]['option'][j])
    option_rate.append(h/t)
average_provided_options=sum(option_rate)/len(option_rate)
results['average_provided_options'] = average_provided_options




miss_list=[]
miss_rate=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True:
        # for jd,j in enumerate(struct_data[i]['misses']):
        miss_list.append(struct_data[i]['misses'])
for i in range(len(miss_list)):
    t = 0
    h = 0
    t=t+1
    for j in range(len(miss_list[i])):
        h=h+len(miss_list[i][j]['question'])
    miss_rate.append(h/t)
average_inquired_missing_details=sum(miss_rate)/len(miss_rate)
results['average_inquired_missing_details'] = average_inquired_missing_details



rounds_list=[]
rounds_rate=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True:
        # for jd,j in enumerate(struct_data[i]['misses']):
        rounds_list.append(struct_data[i]['misses'])
for i in range(len(rounds_list)):
    t = 0
    h = 0
    t=t+1
    h=h+len(rounds_list[i])
    rounds_rate.append(h/t)
average_conversation_rounds=sum(rounds_rate)/len(rounds_rate)
results['average_conversation_rounds'] = average_conversation_rounds



miss_list=[]
miss_rate=[]
for i in range(TASK_NUM):
    if bool(struct_data[i]['vague'])==True:
        for jd,j in enumerate(struct_data[i]['misses']):
            miss_list.append(struct_data[i]['misses'][jd])
for i in range(len(miss_list)):
    t = 0
    h = 0
    t=t+1
    h=h+len(miss_list[i]['question'])
    miss_rate.append(h/t)
average_inquired_missing_details_per_round=sum(miss_rate)/len(miss_rate)
results['average_inquired_missing_details_per_round'] = average_inquired_missing_details_per_round

results['vagueness_judgement_accuracy'] = vagueness_judgement_accuracy
results['missing_details_recover_rate'] = missing_details_recover_rate
results['summary_intention_coverage_rate'] = summary_intention_coverage_rate
results['options_presenting_rate'] = options_presenting_rate
results['options_reasonable_rate'] = options_reasonable_rate






















