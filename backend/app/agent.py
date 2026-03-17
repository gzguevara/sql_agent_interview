import os
from pathlib import Path
from typing import Any, AsyncIterator

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, ToolMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

from app.config import Settings
from app.schemas import ChatMessage


def _resolve_sqlite_path(database_url: str) -> Path | None:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return None
    path_value = database_url[len(prefix) :]
    path = Path(path_value)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


class AgentService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

        sqlite_path = _resolve_sqlite_path(settings.database_url)
        if sqlite_path is not None and not sqlite_path.exists():
            raise FileNotFoundError(f"SQLite database not found at: {sqlite_path}")

        os.environ["GOOGLE_API_KEY"] = settings.google_api_key
        self._model = init_chat_model(settings.model_name)
        self._db = SQLDatabase.from_uri(settings.database_url)
        self._tools = SQLDatabaseToolkit(db=self._db, llm=self._model).get_tools()

        system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
            dialect=self._db.dialect,
            top_k=5,
        )

        self._agent = create_agent(
            self._model,
            self._tools,
            system_prompt=system_prompt,
        )

    async def stream_events(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[dict[str, Any]]:
        input_payload = {"messages": [message.model_dump() for message in messages]}
        async for chunk in self._agent.astream(
            input_payload,
            stream_mode="updates",
            version="v2",
        ):
            if chunk["type"] != "updates":
                continue

            for step, data in chunk["data"].items():
                message = data["messages"][-1]

                if isinstance(message, AIMessage) and message.tool_calls:
                    for call in message.tool_calls:
                        yield {
                            "event": "tool_call",
                            "data": {
                                "tool": call["name"],
                                "args": call["args"],
                                "step": step,
                            },
                        }

                elif isinstance(message, ToolMessage):
                    yield {
                        "event": "tool_result",
                        "data": {
                            "tool": message.name,
                            "content": str(message.content),
                            "step": step,
                        },
                    }

                elif isinstance(message, AIMessage) and message.text:
                    yield {
                        "event": "final",
                        "data": {
                            "text": message.text,
                            "step": step,
                        },
                    }
