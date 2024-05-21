import json
from intention_gpt import *
from supervisor import *
from refine import *
from user_gpt import *
from summary import *
import time








data=read_json(f"./data/BPO/train.json")


generate=[]
begin=0
end=2500
for id,i in enumerate(data[begin:end],start=begin):
    detail=[]
    task=i['prompt']
    vague=True
    while True:
        d={}

        print(str(id)+': get_intent')
        while True:
            try:
                intent, struct_intent = get_intent(task)
                if struct_intent['vague'] == 'True':
                    mark_old_table = json2markdown(struct_intent['implicit_intent'])
                    break
                elif struct_intent['vague'] == 'False':
                    break
            except Exception as e:
                print(e)
                print("Error")
                time.sleep(3)
        vague=struct_intent['vague']
        initial_thought=struct_intent['thought']
        if vague=='False':
            d['struct_intent'] = struct_intent
            detail.append(d)
            break
        explicit_intent=struct_intent['explicit_intent']
        json_old_table=struct_intent['implicit_intent']
        mark_old_table=json2markdown(json_old_table)
        d['struct_intent']=struct_intent



        print(str(id) + ': supervise')
        while True:
            try:
                thought_text,struct_thought=supervise(explicit_intent,mark_old_table)
                break
            except Exception as e:
                print(e)
                print("Error")
                time.sleep(3)
        thought=initial_thought+'\n\n'+struct_thought['thought']
        score=sum(struct_thought['good_score'])-sum(struct_thought['bad_score'])
        d['struct_thought'] = struct_thought


        print(str(id) + ': get_refine')
        while True:
            try:
                new_table,struct_new_table=get_refine(explicit_intent,mark_old_table,thought,score)
                break
            except Exception as e:
                print(e)
                print("Error")
                time.sleep(3)
        d['struct_new_table']=struct_new_table



        print(str(id) + ': get_response')
        while True:
            try:
                answer,struct_answer=get_response(explicit_intent,new_table)
                break
            except Exception as e:
                print(e)
                print("Error")
                time.sleep(3)
        d['struct_answer']=struct_answer


        print(str(id) + ': get_summary')
        while True:
            try:
                struct_summary=get_summary(explicit_intent,answer)
                break
            except Exception as e:
                print(e)
                print("Error")
                time.sleep(3)
        d['struct_summary']=struct_summary



        detail.append(d)
        task=struct_summary['summary']


    generate.append(detail)

    dump_json(generate, './output/generate/generate_BPO_train_{}_{}.json'.format(str(begin), str(id)))



print(1)
