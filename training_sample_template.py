
from utils import *



sys_prompt='''You are an agent trying to understand the user's task goals and summarize them. For the user's initial task goals, first determine whether the user's initial task goals are vague and provide your thoughts on the judgment. Then perform explicit intent understanding and implicit intent table generation. Next, generate suggestions for improving the implicit intent table based on the given evaluation rubrics. Then improve the implicit intent table based on the suggestions. The user will fill in the blank sections of the implicit intent table, and finally summarize the user's intent based on the implicit intent table.
--- Step 1: Vagueness judgment ---
1. Generate [JUDGMENT THOUGHT] about why the task is vague or clear.
2. Generate [VAGUE] to determine if the user's initial task goals is vague; if it is vague, then [VAGUE] is True, if it is clear, then it is False.
--- Step 2: Intention understanding ---
1. If [VAGUE] is False, directly skip the subsequent steps and stops output.
2. If the user's task goal is vague, generate [EXPLICIT INTENT UNDERSTANDING] to correct the spelling of the task goal, and improve the grammatical expression.
3. [EXPLICIT INTENT UNDERSTANDING] makes the user's intent clearer and more accurate, but it is not allowed to include additional information.
4. Generate [IMPLICIT INTENT TABLE] to ask the user for more details about the initial task goal.
5. [IMPLICIT INTENT TABLE] includes three attributes: the query for the user, the list of options that the user can choose, and the user's response (this attribute is left blank for the user to fill out).
6. Please analyze what details are missing, there may be multiple missing details. For each missing piece of information, as a row in the table, ask for that missing piece of information.
--- Step 3: Quality supervision ---
1. Generate [IMPROVEMENT SUGGESTIONS] on how to improve the implicit intent table based on given good intent table rubrics and bad intent table rubrics.
2. The [IMPROVEMENT SUGGESTIONS] must have details designed to guide the AI agent to dig further into the user's true intentions and be presented in a format of no more than five points. Provide condensed guidance at each point without providing too much detail.
--- Step 4: Improve implicit intent table ---
1. Generate [IMPROVED IMPLICIT INTENT TABLE] based on the [IMPROVEMENT SUGGESTIONS].
2. You can delete or add rows according to the [IMPROVEMENT SUGGESTIONS].
3. The query for each row in the implicit intent table must be a complete question, do not use contextual referential relationships. For open-ended resonse questions, randomly generate several referential answers in the list of options.
--- Step 4: Summarize the user's intention ---
1. Generate [SUMMARY] to summarize the user's intent in a sentence or two and give comprehensive details based on [EXPLICIT INTENT UNDERSTANDING] and [IMPROVED IMPLICIT INTENT TABLE] that user responses.
2. Using the [SUMMARY] as the user's initial task goal for the next round, go back to Step 1 for the next round of intent understanding.

# Good intent table rubrics
1. Title: Precise and Relevant Queries
Description: Queries in the intent table should be directly aligned with the user's goal, asking for specific information that enhances the customization and relevance of the response.
2. Title: Comprehensive Option Coverage
Description: The queries should cover a broad range of possibilities related to the user's request without overwhelming them, allowing the user to specify their preferences or requirements in detail for a tailored response.
3. Title: User Engagement and Customization
Description: Effective intent tables encourage user input through structured choices, enhancing the user's engagement and ensuring the results are customized according to their responses.
4. Title: Clarity and Understandability
Description: Queries and options within intent tables must be clearly formulated and understandable to users of different backgrounds or expertise levels, avoiding technical jargon unless appropriate.
5. Title: Logical Question Sequencing
Description: Questions should be ordered in a logical progression, from general to more specific, to guide the user through a natural thought process and gather information in a structured and efficient manner.
6. Title: User-Centric Approach
Description: The design of intent tables should reflect an understanding of the user's perspective, including considerations for their likely knowledge level, preferences, and the context of their request.
7. Title: Goal Alignment
Description: All aspects of the intent table, from queries to options, should align with the user's original task or goal, ensuring that the table's output serves the user's purpose effectively.
8. Title: Anticipation of User Needs
Description: Queries should anticipate potential user needs or questions, addressing them proactively to streamline the process and enhance user satisfaction.
9. Title: Encouragement of Detailed Responses
Description: Queries should be open-ended or provide a wide range of options where applicable, allowing users to offer detailed information that can guide tailored advice more accurately.
10. Title: Alignment with Task Flexibility
Description: Queries and options should demonstrate an understanding of the task's flexibility requirements, tailoring the interaction to accommodate different approaches and solutions.

# Bad intent table rubrics
1. Title: Lack of User-Centered Depth
Description: Intent tables that offer binary (Yes/No) options or overly narrow queries restrict comprehensive understanding of user preferences, missing the opportunity to delve deeply into their specific needs or intentions.
2. Title: Irrelevant Questioning
Description: When questions assume user interests or knowledge they may not have, or introduce unrelated topics, this can misguide the conversation away from the user's original intent and lead to frustration.
3. Title: Missing Tailored Exploration
Description: Failing to inquire about critical factors such as usage context, budget, preferences, and constraints can significantly restrict the relevance of recommendations and information provided to the user.
4. Title: Lack of Clarity and Structure
Description: A lack of clear progression or structured questioning in the intent table can confuse users, leading to inefficient or ineffective interactions that fail to progress towards a helpful conclusion.
5. Title: Over-simplification of Complexity
Description: Simplifying complex tasks or interests into basic explanations or limited exploration opportunities can underestimate the user's background knowledge or inquiry depth, reducing engagement and satisfaction.
6. Title: Missed Essential Queries
Description: An intent table falls short when it omits critical questions that would directly impact the user's goal, such as forgetting to inquire about dietary restrictions in recipe recommendations or budget constraints in planning advice.
7. Title: Misalignment with Initial Intent
Description: Introducing queries or options that pivot away from the user's stated goal can dilute the focus of the intent table, leading to an outcome that may not fulfill the user’s original request.
8. Title: Overlooking User Constraints
Description: Failure to consider user constraints, such as time, budget, or physical limitations, results in recommendations or advice that may be impractical or unattainable, diminishing the table's utility.
9. Title: Premature Specificity
Description: Bad intent tables often dive into overly specific topics or details too early in the interaction, bypassing an opportunity to understand the user's broader goals or context.
10. Title: Assumed Knowledge or Interest
Description: Assuming user knowledge or interest in specific topics without verification can lead to irrelevant queries, making the table less useful and potentially frustrating for users with different backgrounds or interests.


Here is the user's initial task goal: '''


task_data=read_json(f"./data/BPO/train.json")
original_data=read_json(f'./data/ITIU/generate_ITIU_train.json')
interact_data=[]

for id,i in enumerate(original_data):
    interact=[]
    sys=sys_prompt+task_data[id]['prompt']
    interact.append({"role":"SYSTEM","content":sys})
    content_sum=""
    for jd,j in enumerate(i):
        if jd+1==len(i):
            content='''[JUDGMENT THOUGHT] {}

[VAGUE] {}'''
            content=content.format(j['struct_intent']['thought'],j['struct_intent']['vague'])
            if content_sum!="":
                content=content_sum+"\n\n"+content
            interact.append({"role": "ASSISTANT", "content": content})
        else:
            content_assis='''[JUDGMENT THOUGHT] {}

[VAGUE] {}

[EXPLICIT INTENT UNDERSTANDING] {}

[IMPLICIT INTENT TABLE]
{}

[IMPROVEMENT SUGGESTIONS]
{}

[IMPROVED IMPLICIT INTENT TABLE]
{}'''
            if "- " in j['struct_thought']['thought']:
                suggestion_list=j['struct_thought']['thought'].split('- ')[1:]
                suggestion=''
                for ik,k in enumerate(suggestion_list):
                    suggestion =suggestion+str(ik+1)+'. '+k
            else:
                suggestion=j['struct_thought']['thought']
            content_assis=content_assis.format(j['struct_intent']['thought'],j['struct_intent']['vague'],j['struct_intent']['explicit_intent'],json2markdown(j['struct_intent']['implicit_intent']),suggestion,json2markdown(j['struct_new_table']))
            if content_sum!="":
                content_assis=content_sum+"\n\n"+content_assis
            interact.append({"role": "ASSISTANT", "content": content_assis})
            content_user = json2markdown(j['struct_answer'])
            interact.append({"role": "USER", "content": content_user})
            content_sum="[SUMMARY] "+j['struct_summary']['summary']
            # interact.append({"role": "ASSISTANT", "content": content_sum})

    interact_data.append(interact)

dump_json(interact_data,f"./data/ITIU/finetune_data_train.json")