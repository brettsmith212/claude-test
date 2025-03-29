import anthropic


def get_weather(location: str) -> str:
    # This is a mock implementation - replace with actual weather API call
    return f"The weather in {location} is sunny and 73°F"


client = anthropic.Anthropic()

# Define the tool
tools = [
    {
        "type": "custom",
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"],
        },
    }
]

# Keep track of conversation history
messages = [{"role": "user", "content": "What's the weather like in Seattle, WA?"}]

# Initial message to Claude
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

# Process the response and handle tool calls
while True:
    if len(response.content) > 1 and response.content[1].type == "tool_use":
        tool_name = response.content[1].name
        location = response.content[1].input["location"]
        tool_content = {
            "type": "tool_result",
            "tool_use_id": response.content[1].id,
            "content": "",
        }

        # Process each tool call
        if tool_name == "get_weather":
            # Parse the arguments and call the function
            weather_result = get_weather(location)
            tool_content["content"] = weather_result

        # Add assistant's response and tool outputs to conversation
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [tool_content]})

        # Continue the conversation with updated context
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

    else:
        # Print the final response and break
        print(response.content[0].text)
        break
