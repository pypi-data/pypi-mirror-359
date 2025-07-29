# print(strategy("CoT") | context("my-resume") | pattern("summarize"))
# from mps.fetcher import context
from mps.fetcher import context

# print(
#     # context(
#     #     "https://medium.com/@rameshkannanyt0078/10-hidden-gem-libraries-to-supercharge-your-fastapi-projects-249f6decba05"
#     # )
## pattern("summarize")
#     context("https://docs.pydantic.dev/latest/concepts/validators/#model-validators")
# )
# context("https://docs.pydantic.dev/latest/concepts/validators/#model-validators")
# context("my-resume")


def main() -> None:
    # print(get_miniature_kind_from_path("/home/mghali/mps/didi/my-resume.pdf"))
    # print(get_miniature_name_from_path("/home/mghali/mps/context/my-resume.pdf"))
    # print(get_miniature_name_from_path("/home/mghali/mps/strategy/cot.json"))
    # print(get_miniature_name_from_path("/home/mghali/mps/pattern/translate/system.md"))
    # print(get_miniature_name_from_path("/home/mghali/mps/meta/teacher-assistant"))
    # print(pattern("summarize"))
    # print(strategy("CoT"))
    # print(context("my-resume"))
    # print(meta("teacher-assistant"))
    # print(context("https://docs.pydantic.dev/latest/concepts/alias/#validation_1"))
    print(
        context(
            "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Keep-Alive"
        )
    )

    # print(MiniatureKind.extensions()[0])
    # context("https://docs.pydantic.dev/latest/concepts/alias/#serialization_1")
    # print(
    #     pattern(
    #         "https://docs.pydantic.dev/latest/concepts/alias/#serialization_1"
    #     ).source_path
    # )


if __name__ == "__main__":
    main()
