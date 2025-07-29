"""OpenAPI MCP Server."""

import contextlib
import logging
from enum import Enum
from typing import AsyncIterator, List

import anyio
import uvicorn
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import FileUrl, GetPromptResult, Prompt, Resource, TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send
from zmp_openapi_helper import ZmpAPIWrapper

logger = logging.getLogger(__name__)


class TransportType(str, Enum):
    """Transport type for MCP and Gateway."""

    SSE = "sse"
    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"


class OpenAPIMCPServer:
    """OpenAPI MCP Server."""

    def __init__(
        self,
        name: str = "axmp-openapi-mcp-server",
        transport_type: TransportType = TransportType.STREAMABLE_HTTP,
        port: int = 9999,
        zmp_openapi_helper: ZmpAPIWrapper = None,
    ):
        """Initialize the server."""
        self.name = name
        self.port = port
        self.transport_type = transport_type
        self.zmp_openapi_helper = zmp_openapi_helper
        self.operations = (
            self.zmp_openapi_helper.get_operations() if zmp_openapi_helper else None
        )
        self.app = Server(self.name)
        self._initialize_app()

    def _initialize_app(self):
        """Initialize the app."""

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Call the tool with the given name and arguments from llm."""
            logger.debug("-" * 100)
            logger.debug(f"::: tool name: {name}")
            logger.debug("::: arguments:")
            for key, value in arguments.items():
                logger.debug(f"\t{key}: {value}")
            logger.debug("-" * 100)

            operation = next((op for op in self.operations if op.name == name), None)
            if operation is None:
                # raise ValueError(f"Unknown tool: {name}")
                logger.error(f"Unknown tool: {name}")
                return [TextContent(type="text", text=f"Error: Unknown tool: {name}")]

            path_params = (
                operation.path_params(**arguments) if operation.path_params else None
            )
            query_params = (
                operation.query_params(**arguments) if operation.query_params else None
            )
            request_body = (
                operation.request_body(**arguments) if operation.request_body else None
            )

            logger.debug(f"path_params: {path_params}")
            logger.debug(f"query_params: {query_params}")
            logger.debug(f"request_body: {request_body}")

            try:
                result = self.zmp_openapi_helper.run(
                    operation.method,
                    operation.path,
                    path_params=path_params,
                    query_params=query_params,
                    request_body=request_body,
                )

                return [TextContent(type="text", text=f"result: {result}")]
            except Exception as e:
                logger.error(f"Error: {e}")
                return [TextContent(type="text", text=f"Error: {e}")]

        @self.app.list_tools()
        async def list_tools() -> list[Tool]:
            """List all the tools available."""
            tools: List[Tool] = []
            for operation in self.operations:
                tool: Tool = Tool(
                    name=operation.name,
                    description=operation.description,
                    inputSchema=operation.args_schema.model_json_schema(),
                )
                tools.append(tool)

                logger.debug("-" * 100)
                logger.debug(f"::: tool: {tool.name}\n{tool.inputSchema}")

            return tools

        @self.app.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """List all the prompts available."""
            prompts: List[Prompt] = []
            return prompts

        @self.app.get_prompt()
        async def get_prompt(
            name: str, arguments: dict[str, str] | None = None
        ) -> GetPromptResult:
            """Get the prompt with the given name and arguments."""
            return None

        @self.app.list_resources()
        async def list_resources() -> list[Resource]:
            """List all the resources available."""
            resources: List[Resource] = []
            return resources

        @self.app.read_resource()
        async def read_resource(uri: FileUrl) -> str | bytes:
            """Read the resource with the given URI."""
            return None

    def run(self):
        """Run the server."""
        if self.transport_type == TransportType.SSE:
            sse = SseServerTransport("/messages/")

            async def handle_sse(request: Request):
                logger.info(f"::: SSE connection established - request: {request}")
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await self.app.run(
                        streams[0], streams[1], self.app.create_initialization_options()
                    )

            starlette_app = Starlette(
                debug=True,
                routes=[
                    Route("/sse", endpoint=handle_sse),
                    Mount("/messages/", app=sse.handle_post_message),
                ],
            )

            uvicorn.run(starlette_app, host="0.0.0.0", port=self.port)
        elif self.transport_type == TransportType.STREAMABLE_HTTP:
            # Create the session manager with true stateless mode
            session_manager = StreamableHTTPSessionManager(
                app=self.app,
                event_store=None,
                json_response=False,
                stateless=True,
            )

            async def handle_streamable_http(
                scope: Scope, receive: Receive, send: Send
            ) -> None:
                logger.info(f"Application starting...{scope}")
                logger.info("-" * 100)
                headers: list[tuple[bytes, bytes]] = scope.get("headers")
                logger.info(f"Headers: {headers}")
                for header in headers:
                    name, value = header
                    logger.info(f"Header {name.decode()}: {value.decode()}")
                logger.info("-" * 100)

                await session_manager.handle_request(scope, receive, send)

            @contextlib.asynccontextmanager
            async def lifespan(app: Starlette) -> AsyncIterator[None]:
                """Context manager for session manager."""
                # TODO: retrieve the mcp-server-tool configuration from the agent studio
                # 1. get the agent studio url, credentials from the environment variable
                # 2. get the agent studio tool configuration from the agent studio
                # 3. get openapi spec from the agent studio
                # 4. save the tool configuration to the file into the filesystem attached to the mcp server container
                # 5. save the openapi spec to the file into the filesystem attached to the mcp server container
                # 6. set the api-key for each backend server from the client's request header
                # 7. start the mcp server with the tool configuration and openapi spec

                async with session_manager.run():
                    logger.info(
                        "Application started with StreamableHTTP session manager!"
                    )
                    try:
                        yield
                    finally:
                        logger.info("Application shutting down...")

            # Create an ASGI application using the transport
            starlette_app = Starlette(
                debug=True,
                routes=[
                    Mount("/mcp", app=handle_streamable_http),
                ],
                lifespan=lifespan,
            )

            uvicorn.run(starlette_app, host="0.0.0.0", port=self.port)
        else:
            async def arun():
                async with stdio_server() as streams:
                    await self.app.run(
                        streams[0], streams[1], self.app.create_initialization_options()
                    )

            anyio.run(arun)
