import wikipedia
from anthropic import Anthropic
from dotenv import load_dotenv

MODEL_NAME = "claude-3-5-sonnet-20240620"


def get_article(search_term):
    results = wikipedia.search(search_term)
    first_result = results[0]
    page = wikipedia.page(first_result, auto_suggest=False)
    return page.content


article_search_tool = {
    "name": "get_article",
    "description": "A tool to retrieve an up to date Wikipedia article.",
    "input_schema": {
        "type": "object",
        "properties": {
            "search_term": {
                "type": "string",
                "description": "The search term to find a wikipedia article by title",
            },
        },
        "required": ["search_term"],
    },
}

load_dotenv()

client = Anthropic()


def answer_question(question):
    system_prompt = """
    You will be asked a question by the user.
    If answering the question requires data you were not trained on, you can use the get_article tool to get the contents of a recent wikipedia article about the topic.
    You can make multiple tool calls in the same request and the tool will return all requested information.
    If you can answer the question without needing to get more information, please do so.
    Only call the tool when needed.
    """
    prompt = f"""
    Answer the following question <question>{question}</question>
    When you can answer the question, keep your answer as short as possible and enclose it in <answer> tags
    """
    messages = [{"role": "user", "content": prompt}]

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        system=system_prompt,
        messages=messages,
        max_tokens=1000,
        tools=[article_search_tool],
    )

    while response.stop_reason == "tool_use":
        # Add Claude's tool use call to messages:
        messages.append({"role": "assistant", "content": response.content})
        for tool_use in response.content:
            if tool_use.type == "tool_use":
                tool_name = tool_use.name
                tool_input = tool_use.input

                if tool_name == "get_article":
                    search_term = tool_input["search_term"]
                    print(f"Claude wants to get an article for {search_term}")
                    wiki_result = get_article(
                        search_term
                    )  # get wikipedia article content
                    # construct our tool_result message
                    tool_response = {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": wiki_result,
                            }
                        ],
                    }
                    messages.append(tool_response)
                # respond back to Claude
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            system=system_prompt,
            messages=messages,
            max_tokens=1000,
            tools=[article_search_tool],
        )
    print("Claude's final answer:")
    print(response.content[0].text)


# answer_question(
#     """
#     How many Oscars does Christopher Nolan have?
#     Does he have more than the number of Emmy's that Ben Stiller has?
#     """
# )
while True:
    user_input = input("ask a question: ")
    answer_question(user_input)
