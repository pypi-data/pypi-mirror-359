import asyncio

from .build import chat_completion, execution_settings, get_chat_history, kernel

USER_PROMPT = "User:> "
AGENT_PROMPT = "Agent:> "


async def main() -> None:
    user_input: str
    chat_history = get_chat_history()

    while True:
        try:
            user_input = input(USER_PROMPT)
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ("q", "exit", "quit"):
            break

        chat_history.add_user_message(user_input)

        response = chat_completion.get_streaming_chat_message_content(
            kernel=kernel, chat_history=chat_history, settings=execution_settings
        )

        chunk_builder: list[str] = []

        print(AGENT_PROMPT, end="")
        async for chunk in response:
            print(str(chunk), end="")
            chunk_builder.append(str(chunk))

        print()

        full_response = "".join(chunk_builder)
        chat_history.add_assistant_message(full_response)

    print("\n\nExiting chat...")


if __name__ == "__main__":
    asyncio.run(main())
