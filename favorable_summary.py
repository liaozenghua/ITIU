
from openai import OpenAI
from utils import *

client = OpenAI(
    api_key='',
    base_url=''
)






def get_rubrics(patterns):
    prompt_begin = '''# Task
The intent table contains a number of queries and options for the user to better understand the intent of their initial task goal. You will get some good intent table patterns, which are extracted from the good intention table. Your job is to summarize some rubrics from the good intent table patterns that explain why an intent table is good. And provide a title for each rubric.

# Instruction
Your task is to summarize some rubrics to identify whether an intent table is helpful in understanding the user's true intent, and to summarize a title for each rubric. Requirements:
1. Provide your answers as a numbered list of up to 10 items.
2. Rubrics should be user-centric, concise, and mutually exclusive.

# Example of good intent table patterns:'''

    prompt_end='''# Now summarize these examples of good intent table patterns into rubrics to identify if an intent table is helpful in understanding the user's true intent. Requirements:
1. Provide your answer as a numbered list of up to 10 bullet items.
2. The number of items in the rubrics is 10.
3. The rubric should be user-centric, concise, and mutually exclusive.
4. Provide your answer as a numbered list of bullet items in <Rubric></Rubric>.
5. Each point includes a title and a description, with the description detailing the rubric details and the title summarizing the rubric in a phrase.

The output format is as follows:
# Output
<Rubric>
1. Title: [The title of rubric 1]
Description:[The description of rubric 1]
2. Title: [The title of rubric 2]
Description:[The description of rubric 2]
2. Title: [The title of rubric 3]
Description:[The description of rubric 3]
...
</Rubric>'''

    prompt=prompt_begin+'\n'+patterns+'\n\n'+prompt_end

    rubrics_response = client.chat.completions.create(
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

    return rubrics_response.choices[0].message.content





data=[]
data=read_json(f'./output/patterns/patterns_0_94.json')
patterns=''
for id,i in enumerate(data):
    patterns=patterns+'Good intent table patterns {}:\n'.format(str(id+1))+i['good_patterns']+'\n\n'

patterns=patterns.strip()

good_rubrics=get_rubrics(patterns)








