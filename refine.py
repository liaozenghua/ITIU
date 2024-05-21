from openai import OpenAI
from utils import *



def get_refine(task,old_table,thought,score):

    my_function=[{"name": "refine",
"description": "Complete the intent understanding of the user's task goal by providing the implicit intent table.",
"parameters": {"type": "object",
                "properties": {"implicit_intent": {"type": "array", "description": "An implicit intent table for the user's task goal with three attributes: Query for the user, List of options, User's response. If there is no implicit chart, return an empty list.",
                                                                "items":{"type": "object",
                                                                        "properties": {"Query for user":{"type": "string","description": "A query problems with each row in the implicit intent table."},
                                                                                        "List of options":{"type":"array",
                                                                                                    "description":"A list of options for query questions in each row of the implicit intent table.",
                                                                                                    "items":{"type":"string","description":"One of the options in the list of options for each query, making the options very short and specific (e.g. just using phrases)."}
                                                                                                    },
                                                                                        "User's response":{"type":"string","description": "The user's response to the query in each row of the implicit intent table is generally empty string.","enum":["",""]}
                                                                                        },
                                                                        "required": ["Query for user","List of options","User's response"]
                                                                        }
                                                    }
                                },
                "required": ["implicit_intent"]
                }
}]

    prompt_begin='''# task
The current implicit intent table are not of high enough quality. In order to better understand the user's true intentions regarding the initial task goal, you need to improve the implicit intent table. I have summarized some thoughts that you can use to improve the implicit intent table.

# Instruction
1. You need to go through the current intent table and the user's initial task goal, and improve the intent table according to the suggestions in the thought.
2. You can delete or add rows according to the thought.
3. You just need to output the improved implicit intent table.
4. The query for each row in the implicit intent table must be a complete question, do not use contextual referential relationships. For open-ended resonse questions, randomly generate several referential answers in the list of options.

# User's initial task goal: '''


    prompt_end='''# Current implicit intent table score is {} out of 100. Now refine current implicit intent table according to thought.

# Improved implicit intent table'''.format(str(score))


    prompt=prompt_begin+task+'\n\n# Current implicit intent table:\n'+old_table+'\n\n# Thought about improving implicit intent table:\n'+thought+'\n\n'+prompt_end

    i=0
    format=False
    while format==False:
        refine_response = chat4(
            model="gpt-4-turbo-preview",
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
            temperature=0.7,
            stream=False,
        )
        refine = refine_response.choices[0].message.content


        struct_refine_response = chat3(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "user",
                    "content": refine
                },
            ],
            functions=my_function,
            # function_call='auto',
            stream=False,
        )

        struct = struct_refine_response.choices[0].message
        if struct.function_call == None:
            print("refine again" + str(i))
            i = i + 1
            continue
        try:
            struct_refine = json.loads(struct.function_call.arguments)
        except:
            print("refine again"+str(i))
            i=i+1
            continue
        if not ('implicit_intent' in struct_refine.keys()):
            print("refine again" + str(i))
            i = i + 1
            continue
        new_implicit_refine = []
        bo = True
        for idr, row in enumerate(struct_refine['implicit_intent']):
            keys = list(row.keys())
            new_row = {}
            for idk, key in enumerate(keys):
                new_row[key.strip()] = row[key]
            new_keys = new_row.keys()
            if not ("Query for user" in new_keys and "List of options" in new_keys and "User's response" in new_keys):
                bo = False
                break
            else:
                new_implicit_refine.append(new_row)
        if bo == True:
            format = True
        else:
            print("refine again" + str(i))
            i = i + 1
            continue
    struct_refine['implicit_intent'] = new_implicit_refine
    return json2markdown(struct_refine["implicit_intent"]),struct_refine["implicit_intent"]







