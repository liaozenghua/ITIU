from openai import OpenAI
from utils import *



def get_response(task,table):

    my_function=[{"name": "answer",
"description": "Complete the intent understanding of the user's task goal by providing the implicit intent table.",
"parameters": {"type": "object",
                "properties": {"implicit_intent": {"type": "array", "description": "An implicit intent table for the user's task goal with three attributes: Query for the user, List of options, User's response. If there is no implicit chart, return an empty list.",
                                                                "items":{"type": "object",
                                                                        "properties": {"Query for user":{"type": "string","description": "A query problems with each row in the implicit intent table."},
                                                                                        "List of options":{"type":"array",
                                                                                                    "description":"A list of options for query questions in each row of the implicit intent table.",
                                                                                                    "items":{"type":"string","description":"The options in the list of options for the query, making the options very short and specific (e.g. just using phrases)."}
                                                                                                    },
                                                                                        "User's response":{"type":"string","description": "The user's response to the query in each row of the implicit intent table."}
                                                                                        },
                                                                        "required": ["Query for user","List of options","User's response"]
                                                                        }
                                                    }
                                },
                "required": ["implicit_intent"]
                }
}]

    prompt_begin='''You are an assistant who pretends to be the user's friend and responds to the user. The user is trying to understand your specific needs, and the user has summarized your intent information, including whether vague, thought, explicit intent, and implicit intent table. You are asked some questions in the implicit intent table. You should provide the information to the user in one sentence and fill in the blank of the table.

Here are some tips during chatting to make your response more real.
[Passionate User Tone Version]
1. Respond naturally, and you are passionate. You can provide more if you are happy with it. Keep your tone friendly and positive.
[Succinct User Tone Version]
1. Respond succinctly, and you are lazy. You should respond more often with short phrases. Make your responses short and effective.
2. When you are asked about some personal preference, information, or address, please make up some information and preference and provide it to the user. Make sure to be specific and as real as possible. Please fill in the blank section of the user's implicit intent table and only output the user's implicit intent table.

This is what you'd like to ask or do: '''

    prompt_end='''Please fill in the blank section of the implicit intent table provided by the user. When you are asked about some personal preference, information, or address, please make up some information and preference and provide it to the user. Be as specific and truthful as possible, and try to express a preference as much as possible without answering "Any" or "All" or "None". Output only the user's implicit intent table.'''
    prompt=prompt_begin+task+'\n'+prompt_end

    i=0
    format=False
    while format==False:
        user_response = chat4(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": table
                }

            ],
            temperature=0.7,
            stream=False,
        )
        answer = user_response.choices[0].message.content


        struct_answer_response = chat3(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "user",
                    "content": answer
                },
            ],
            functions=my_function,
            # function_call='auto',
            stream=False,
        )
        struct = struct_answer_response.choices[0].message

        if struct.function_call == None:
            print("answer again" + str(i))
            i = i + 1
            continue
        try:
            struct_answer = json.loads(struct.function_call.arguments)
        except:
            print("answer again"+str(i))
            i=i+1
            continue
        if not ('implicit_intent' in struct_answer.keys()):
            print("answer again" + str(i))
            i = i + 1
            continue
        new_implicit_answer = []
        bo = True
        for idr, row in enumerate(struct_answer['implicit_intent']):
            keys = list(row.keys())
            new_row = {}
            for idk, key in enumerate(keys):
                new_row[key.strip()] = row[key]
            new_keys = new_row.keys()
            if not ("Query for user" in new_keys and "List of options" in new_keys and "User's response" in new_keys):
                bo = False
                break
            else:
                new_implicit_answer.append(new_row)
        if bo == True:
            format = True
        else:
            print("answer again" + str(i))
            i = i + 1
            continue
    struct_answer['implicit_intent'] = new_implicit_answer
    return json2markdown(struct_answer["implicit_intent"]),struct_answer["implicit_intent"]

