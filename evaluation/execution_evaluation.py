import os
import copy
import json
from tqdm import tqdm
from utils import *










def evaluation(question,intention,answer_a,answer_b):
    SYS_PROMPT = """Please act as an impartial judge and evaluate the quality of the responses provided by two AI assistants to the user question displayed below. You should choose the assistant that follows the user's instructions and answers the user's question better. Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of their responses. Begin your evaluation by comparing the two responses and provide a short explanation. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your final verdict by strictly following this format: "[[A]]" if assistant A is better, "[[B]]" if assistant B is better, and "[[C]]" for a tie."""

    USER_PROMPT = """Here is User Question and a list of phrases:

[User Question] 
{question}

[User Intention] 
{intention}

[The Start of Assistant A's Answer]
{answer_a}
[The End of Assistant A's Answer]

[The Start of Assistant B's Answer]
{answer_b}
[The End of Assistant B's Answer]"""



    msg = USER_PROMPT.format(question=question, intention=intention,answer_a=answer_a,answer_b=answer_b)
    resp = chat4(
        model="gpt-4-turbo-preview",
        messages=[
            {'role': 'system', 'content': SYS_PROMPT},
            {'role': 'user', 'content': msg}
        ],
        temperature=0.7,
        n=1).choices[0].message.content
        # if resp != "None of the above":
        #     resp = resp.lower()
        #     if resp in label_list:
        #         result[resp] = True
        #     else:
        #         print(f"Error: {resp} not in human intention list:\n{label_prompt}")
    return resp


question='''How should I prepare for a job interview?'''
intention='''The user wants to prepare for their first job interview for a school basketball team position happening today afternoon. They are looking for specific tips and common interview questions for this role. Additionally, they need advice on attire preparation. Please provide your answer in a short paragraph.
'''
answer_a='''To prepare for a job interview, research the company thoroughly to understand its culture, values, and recent developments. Practice answering common interview questions and prepare questions to ask the interviewer. Review the job description to align your skills and experiences with the position requirements. Dress appropriately for the company's culture, and plan your travel to arrive on time. Finally, bring copies of your resume, a list of references, and a notepad for taking notes.
'''
answer_b='''To excel in your interview for the school basketball team position, focus on demonstrating your passion for basketball, your understanding of coaching strategies, and your ability to motivate and guide students. Common questions might include your coaching philosophy, experience with team management, and strategies for improving player performance. For attire, opt for a smart-casual look, such as a well-fitted polo or button-down shirt with chinos or smart trousers, ensuring you appear professional yet approachable. Good luck in your interview!
'''
a=evaluation(question,intention,answer_a,answer_b)










generate_data=read_json(f"../data/ITIU/finetune_data_test.json")
label_data=[]
with open(f'../data/IN3/test.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        label_data.append(json.loads(line))


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





