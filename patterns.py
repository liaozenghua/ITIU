
from openai import OpenAI
from utils import *

client = OpenAI(
    api_key='',  # this is also the default, it can be omitted
    base_url=''
)






def get_patterns(task,good_table,bad_table):
    prompt = '''Your job is to understand and elaborate the reasons why the AI agent's response to the user's intent understanding is good or bad. You will be given a user's initial task goal and the response of the AI agent attempting to understand the user's intent, which is an intent table containing three attributes: query for the user, optional list that the user can choose, and user's response. For a user's initial task goal, you are given a good intent table and a bad intent table. Your task is to first think about what is good in the good intent table and what is bad in the bad intent table, , and then summarize the good table patterns and the bad table patterns respectively.

Instructions:
1. Return NONE if you can't think of any good or bad reasons in the intent table.
2. The patterns you summarized should be based on the connection between the intent table and the user's initial task goals. Determine whether the information in the intent table is helpful in understanding the user's intent.
3. You should extrapolate, imagine, or hallucinate beyond the text of the conversation that is given.
4. The patterns should be mutually exclusive.
5. You should refer to the fact that there was a like in your summary.
6. Your summary should be concise, use bullet points, each bullet point is no more than 50 tokens in length, and provide no more than 3 bullet points.
7. Provide the reasons for the good intent table and the reasons for the bad intent table, respectively.

You should output in the following format:
Thought: [Your thought]
Good table patterns: [Points summarize the reason why the good intent table is good]
Bad table patterns: [Points summarize the reason why the bad intent table is bad]

User's initial task goals: 
'''
    prompt=prompt+task+'\nGood intention table:\n'+good_table+'\n\nBad intention table:\n'+bad_table

    patterns_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            # {
            #     "role": "user",
            #     "content": ""
            # }

        ],
        stream=False,
    )

    return patterns_response.choices[0].message.content





data=[]
data=read_json(f'./output/contrast/contrast_details.json')




patterns=[]
begin=0
end=len(data)
for id,i in enumerate(data):
    pattern=get_patterns(data[id]['task'],data[id]['in3_table'],data[id]['llama_table'])

    thought=find_mid(pattern,'Thought: ','\n')
    good_patterns=find_mid(pattern,'Good table patterns:','\n\n')
    bad_patterns=find_mid(pattern,'Bad table patterns:','$$$')
    patterns.append({'good_patterns':good_patterns,'bad_patterns':bad_patterns,'thought':thought,'task':data[id]['task']})
    dump_json(patterns, './output/patterns/patterns_{}_{}.json'.format(str(begin), str(id)))






