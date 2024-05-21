from openai import OpenAI
from utils import *

client = OpenAI(
    api_key='Ly3ochmyDMguw',  # this is also the default, it can be omitted
    base_url='https://ai.liaobots.work/v1'
)


def refine(task,old_table,thought):
    prompt_begin='''# task
The current implicit intent table are not of high enough quality. In order to better understand the user's true intentions regarding the initial task goal, you need to improve the implicit intent table. I have summarized some thoughts that you can use to improve the implicit intent table.

# Instruction
1. You need to go through the current intent table and the user's initial task goal, and improve the intent table according to the suggestions in the thought.
2. You can delete or add rows according to the thought.
3. You just need to output the improved implicit intent table.'''


    prompt_end='''# Current implicit intent table score is 74 out of 100. Now refine current implicit intent table according to thought.

# Improved implicit intent table'''


    prompt=prompt_begin+'\n\n# Thought about improving implicit intent table:\n'+thought+'\n\n'+prompt_end


    supervise_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an agent trying to specify and understand the user's task goal. The user will ask you a query or ask you to execute a task. However, the user is unclear about the task or intention. You should generate a structured intention table to interact with the user and get more information to understand the user's intention.\nHere are some rules to follow:\n1. You will be given the user's task goal and you need to determine whether the user's task goal are vague. Vague: The user's task is too general , missing some important details that are necessary to understand the user's intention, or missing some preference details that could better help the user in achieving the task goal. Clear: The user is already clear enough about the task, providing enough details about the task goal, personal preference, etc. Generate thought about why this task goal is vague or clear. Please refer to the description of vague and clear in the system prompt.\n2. If the user's task goal is vague, please first understand the explicit intention of the task goal, correct the spelling of the task goal, and improve the grammatical expression. This process makes the user's intention clearer and more accurate, but it is not allowed to include additional information.\n3. Then perform an implicit intent understanding of the user's task goal. In this process, you need to generate an intent table with three attributes: the query for the user, the list of options that the user can choose, and the user's response (this attribute is left blank for the user to fill out). Please analyze what details are missing, there may be multiple missing details. For each missing piece of information, as a row in the table, ask for that missing piece of information.In the last row of the table, the first column lists the user's additional intent, the second column provides some examples of additional intent, and the third column is left blank for the user to fill in the intent that does not appear in the table.\n4. Use a first-person tone, as you would with a user, and be friendly. User impatience, make your query more efficient! Remember, you don't need to ask for every detail!\nIf the task goal is clear, output in the following format: \nVague: determines whether the target is vague, True or False.\nThought: Reason for judgment.\nIf the task goal is vague, output in the following format:\nVague: determines whether the target is vague, True or False.\nThought: Reason for judgment.\nExplicit intent: Improved task description.\nImplicit intent: Implicit intent understands the table.\nThe user's original task is: I would like to plan a trip to Paris next month.\nBegin the intent understanding process!"
            },
            {
                "role": "assistance",
                "content": '''Explicit intent: Plan a trip to Paris for next month.

Implicit intent:
| Query for the user                                                   | List of options                                             | User's response |
|----------------------------------------------------------------------|-------------------------------------------------------------|-----------------|
| What is the purpose of your trip?                                    | Leisure, Business, Visiting Friends or Family, Other        |                 |
| How long will your trip be?                                          | Number of days                                              |                 |
| What is your budget for the trip?                                    | Under $1000, $1000-$3000, $3000-$5000, Over $5000, Not sure |                 |
| What type of accommodation do you prefer?                            | Hotel, Hostel, Airbnb, Other                                |                 |
| Are you looking for recommendations on what to do in Paris?          | Yes, No                                                     |                 |
| Please list any additional intents or preferences not covered above. | Examples: Dietary restrictions, Mobility considerations     |                 |'''
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=False,
    )

    return supervise_response.choices[0].message.content

task='I would like to plan a trip to Paris next month.'

old_table='''| Query for the user                                                   | List of options                                               | User's response |
|----------------------------------------------------------------------|---------------------------------------------------------------|-----------------|
| What is the purpose of your trip?                                    | Leisure, Business, Visiting Friends or Family, Other          |                 |
| How long will your trip be?                                          | Number of days                                                |                 |
| What is your budget for the trip?                                    | Under $1000, $1000-$3000, $3000-$5000, Over $5000, Not sure   |                 |
| What type of accommodation do you prefer?                            | Hotel, Hostel, Airbnb, Other                                  |                 |
| Are you looking for recommendations on what to do in Paris?          | Yes, No                                                       |                 |
| Please list any additional intents or preferences not covered above. | Examples: Dietary restrictions, Mobility considerations       |                 |'''


thought='''1. Integrate contextual considerations: Include queries about the time of year and potential weather conditions in Paris to tailor activities suggestions or necessary preparations.
2. Enhance budget exploration: Instead of fixed budget ranges, ask users to specify areas where they prefer to splurge or save (e.g., accommodations, dining, attractions), accommodating more nuanced financial planning.
3. Incorporate travel companions information: Add queries regarding traveling alone, with a partner, family, or friends, to customize activities and accommodation recommendations.
4. Expand on travel interests: Instead of a binary choice for recommendations on what to do, provide categories (e.g., culture, art, dining, history) for users to select their interests, offering more targeted suggestions.
5. Address concerns and limitations: Include direct queries about mobility issues, dietary restrictions, or other specific needs upfront to ensure all recommendations are practical and inclusive.'''


new_table=refine(task,old_table,thought)
new_table=json2markdown(markdown2json(new_table))






print(1)