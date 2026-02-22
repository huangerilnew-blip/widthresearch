import json

from langchain_core.messages import AIMessage

from agents.planneragent import PlannerAgent, PlannerState


def extract_json_from_text(content: str):
    cleaned = content.strip()
    lower = cleaned.lower()
    fence_start = lower.find("```json")
    if fence_start != -1:
        fence_open = cleaned.find("```", fence_start)
        if fence_open != -1:
            fence_open += 3
            newline = cleaned.find("\n", fence_open)
            if newline != -1:
                fence_open = newline + 1
        fence_end = cleaned.find("```", fence_open)
        if fence_end != -1:
            fenced_content = cleaned[fence_open:fence_end].strip()
            if fenced_content:
                return json.loads(fenced_content)

    opens = [index for index, ch in enumerate(cleaned) if ch == "{"]
    closes = [index for index, ch in enumerate(cleaned) if ch == "}"]
    for start in opens:
        for end in closes:
            if end <= start:
                continue
            snippet = cleaned[start : end + 1].strip()
            if not snippet:
                continue
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                continue
    raise ValueError("No JSON object found in content")


def main() -> None:
    mixed_content = (
        "Here is a brief analysis before the json.\n\n"
        "{\n"
        "  \"tasks\": [\n"
        "    \"Subquestion one\",\n"
        "    \"Subquestion two\",\n"
        "    \"Subquestion three\"\n"
        "  ]\n"
        "}\n"
    )
    state: PlannerState = {
        "planner_messages": [AIMessage(content=mixed_content)],
        "planner_result": AIMessage(content=""),
        "epoch": 0,
    }

    planner = PlannerAgent.__new__(PlannerAgent)
    route = PlannerAgent._condition_router(planner, state)
    parsed = extract_json_from_text(mixed_content)

    print(f"route={route}")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
