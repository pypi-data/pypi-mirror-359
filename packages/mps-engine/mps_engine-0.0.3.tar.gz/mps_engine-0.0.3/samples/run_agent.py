from semantic_kernel.agents import ChatCompletionAgent

USER_PROMPT = ">> "
AGENT_PROMPT = "Agent> "


async def run_agent(agent: ChatCompletionAgent) -> None:
    user_input: str

    thread = None

    while True:
        try:
            user_input = input(USER_PROMPT)
        except (KeyboardInterrupt, EOFError):
            break

        if user_input == "q":
            break

        response = agent.invoke_stream(
            messages=user_input,
            thread=thread,
        )

        print(AGENT_PROMPT, end="")
        async for chunk in response:
            thread = chunk.thread
            print(str(chunk), end="")

        print()

    print("\n\nExiting chat...")

    await thread.delete() if thread else None
