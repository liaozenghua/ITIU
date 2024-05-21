from openai import OpenAI
from utils import *


def get_summary(explicit_intent,table):
    my_function=[{"name": "summary",
"description": "Complete the summary by listing user preferences and constraints, and providing a detailed summary. Respond naturally and succinctly.",
"parameters": {"type": "object",
                "properties": {"constraints":{"type":"array","description":"A list of user preferences and constraints based on the summary. The number of items should be equal to the number of implicit intent queries.",
                                            "items":{"type":"string","description":"The user's preference or constraint in the summary. Summarize and list them one by one. Make it detailed and succinct."}
                                            },
                                "summary": {"type": "string", "description": "Summary of user's intent. Summarize the user's task goal and the constraints in a detailed, efficient, and succinct way within two sentences. Do not provide not mentioned or unnecessary information.",
                                            }
                                },
                "required": ["constraints","summary"]
                }
}]

    prompt='''You are an agent trying to summarize the user's intent and provide a detailed summary. You need a detailed summary based on the explicit intent description and implicit meaning diagram provided by the user, including the task objectives and all user constraints and preferences. You should summarize naturally in two sentences and in the first person (to make your language concise, concise, and effective).'''
    over_intent='''Explicit intent: {}

Implicit intent:
{}'''.format(explicit_intent,table)
    i=0
    format=False
    while format==False:
        summary_response = chat4(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": over_intent
                }
            ],
            temperature=0.7,
            stream=False,
        )

        summary = summary_response.choices[0].message.content



        struct_summary_response = chat3(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "user",
                    "content": over_intent+'\n\nSummary: '+summary
                },
            ],
            functions=my_function,
            # function_call='auto',
            stream=False,
        )

        struct = struct_summary_response.choices[0].message

        if struct.function_call==None:
            print("summary again"+str(i))
            i=i+1
            continue
        try:
            struct_summary = json.loads(struct.function_call.arguments)
        except:
            print("summary again"+str(i))
            i=i+1
            continue
        if not ('constraints' in struct_summary.keys() and 'summary' in struct_summary.keys()):
            print("summary again"+str(i))
            i=i+1
            continue
        format = True
    return struct_summary




