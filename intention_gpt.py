from openai import OpenAI
from utils import *




def initial_intent(task):
    my_function = [{"name": "get_intent",
"description": "Complete the intent understanding of the user's task goal by providing whether the user's task goal is vague, thought, explicit intent, and implicit intent.",
"parameters": {"type": "object",
                "properties": {"vague": {"type": "string", "description": "Whether the user's task goal is vague.","enum":["True", "False"]},
                                "thought": {"type": "string", "description": "Why do/don't you think users' task goal is vague, or what is the thought that you judge if it is vague?"},
                                "explicit_intent": {"type": "string", "description": "The explicit intent of the user. If there is no explicit intent, return an empty string."},
                                "implicit_intent": {"type": "array", "description": "An implicit intent table for the user's task goal with three attributes: Query for the user, List of options, User's response. If there is no implicit chart, return an empty list.",
                                                                "items":{"type": "object",
                                                                        "properties": {"Query for user":{"type": "string","description": "A query problems with each row in the implicit intent table."},
                                                                                        "List of options":{"type":"array",
                                                                                                    "description":"A list of options for query questions in each row of the implicit intent table.",
                                                                                                    "items":{"type":"string","description":"One of the options in the list of options for each query, making the options very short and specific (e.g. just using phrases)."}
                                                                                                    },
                                                                                        "User's response":{"type":"string","description": "The user's response to the query in each row of the implicit intent table is generally empty.","enum":[""]}
                                                                                        },
                                                                        "required": ["Query for user","List of options","User's response"]
                                                                        }
                                                                    }
                                },
                "required": ["thought","vague","explicit_intent","implicit_intent"]
                }
}]


    prompt_begin='''You are an agent trying to specify and understand the user's task goal. The user will ask you a query or ask you to execute a task. However, the user is unclear about the task or intention. You should generate a structured intention table to interact with the user and get more information to understand the user's intention.

Here are some rules to follow:
1. You will be given the user's task goal and you need to determine whether the user's task goal are vague. Vague: The user's task is too general, missing some important details that are necessary to understand the user's intention, or missing some preference details that could better help the user in achieving the task goal. Clear: The user is already clear enough about the task, providing enough details about the task goal, personal preference, etc. Generate thought about why this task goal is vague or clear. Please refer to the description of vague and clear in the system prompt.
2. If the user's task goal is vague, please first understand the explicit intention of the task goal, correct the spelling of the task goal, and improve the grammatical expression. This process makes the user's intention clearer and more accurate, but it is not allowed to include additional information.
3. Then perform an implicit intent understanding of the user's task goal. In this process, you need to generate an intent table with three attributes: the query for the user, the list of options that the user can choose, and the user's response (this attribute is left blank for the user to fill out). Please analyze what details are missing, there may be multiple missing details. For each missing piece of information, as a row in the table, ask for that missing piece of information. In the last row of the table, the first column lists the user's additional intent, the second column provides some examples of additional intent, and the third column is left blank for the user to fill in the intent that does not appear in the table.
4. The query for each row in the implicit intent table must be a complete question, do not use contextual referential relationships. For open-ended resonse questions, randomly generate several referential answers in the list of options.
5. Use a first-person tone, as you would with a user, and be friendly. User impatience, make your query more efficient! Remember, you don't need to ask for every detail!

If the task goal is clear, output in the following format: 
Vague: [determines whether the target is vague, True or False.]
Thought: [Reason for judgment.]

If the task goal is vague, output in the following format:
Vague: [determines whether the target is vague, True or False.]
Thought: [Reason for judgment.]
Explicit intent: [Improved task description.]
Implicit intent: [The implicit intent understanding table contains three attributes: Query for the user, List of options, User's respnse]

The user's original task is: '''

    prompt_end='''Begin the intent understanding process!'''
    prompt=prompt_begin+task+'\n\n'+prompt_end

    intent_response = chat4(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
        ],
        temperature=0.7,
        stream=False,
    )
    intent=intent_response.choices[0].message.content


    struct_response = chat3(
        model="gpt-4-0613",
        messages=[
            {
                "role": "user",
                "content": intent
            },
        ],
        functions=my_function,
        function_call='auto',
        stream=False,
    )

    struct=struct_response.choices[0].message
    return intent,struct

def get_intent(task):
    format=False
    i=0
    while format==False:
        intent, struct=initial_intent(task)
        if struct.function_call==None:
            print("intent_gpt again"+str(i))
            i=i+1
            continue
        try:
            struct_intent = json.loads(struct.function_call.arguments)
        except:
            print("intent_gpt again"+str(i))
            i=i+1
            continue
        if not ('vague' in struct_intent.keys() and 'thought' in struct_intent.keys() and 'explicit_intent' in struct_intent.keys() and 'implicit_intent' in struct_intent.keys()):
            print("intent_gpt again"+str(i))
            i=i+1
            continue
        new_implicit_intent = []
        bo=True
        for idr, row in enumerate(struct_intent['implicit_intent']):
            keys = list(row.keys())
            new_row = {}
            for idk, key in enumerate(keys):
                new_row[key.strip()] = row[key]
            new_keys = new_row.keys()
            if not ("Query for user" in new_keys and "List of options" in new_keys and "User's response" in new_keys):
                bo = False
                break
            else:
                new_implicit_intent.append(new_row)
        if bo==True:
            format=True
        else:
            print("intent_gpt again"+str(i))
            i=i+1
            continue
        try:
            if struct_intent['vague']==True:
                a=json2markdown(new_implicit_intent)
        except:
            print("json2markdow error")
            format =False
    struct_intent['implicit_intent']=new_implicit_intent
    return intent,struct_intent







