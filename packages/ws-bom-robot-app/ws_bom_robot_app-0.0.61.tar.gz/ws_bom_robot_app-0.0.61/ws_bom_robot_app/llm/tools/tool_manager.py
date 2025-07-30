from asyncio import Queue
from typing import  Optional, Type, Callable
from ws_bom_robot_app.llm.models.api import LlmAppTool
from ws_bom_robot_app.llm.providers.llm_manager import LlmInterface
from ws_bom_robot_app.llm.vector_store.db.manager import VectorDbManager
from ws_bom_robot_app.llm.tools.utils import getRandomWaitingMessage, translate_text
from ws_bom_robot_app.llm.tools.models.main import NoopInput,DocumentRetrieverInput,ImageGeneratorInput,LlmChainInput,SearchOnlineInput,EmailSenderInput
from pydantic import BaseModel, ConfigDict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class ToolConfig(BaseModel):
    function: Callable
    model: Optional[Type[BaseModel]] = NoopInput
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

class ToolManager:
    """
    ToolManager is responsible for managing various tools used in the application.

    Attributes:
        app_tool (LlmAppTool): The application tool configuration.
        api_key (str): The API key for accessing external services.
        callbacks (list): A list of callback functions to be executed.

    Methods:
        document_retriever(query: str): Asynchronously retrieves documents based on the query.
        image_generator(query: str, language: str = "it"): Asynchronously generates an image based on the query.
        get_coroutine(): Retrieves the coroutine function based on the tool configuration.
    """

    def __init__(
        self,
        llm: LlmInterface,
        app_tool: LlmAppTool,
        callbacks: list,
        queue: Optional[Queue] = None
    ):
        self.llm = llm
        self.app_tool = app_tool
        self.callbacks = callbacks
        self.queue = queue

    async def __extract_documents(self, query: str, app_tool: LlmAppTool):
        search_type = "similarity"
        search_kwargs = {"k": 4}
        if app_tool.search_settings:
            search_settings = app_tool.search_settings # type: ignore
            if search_settings.search_type == "similarityScoreThreshold":
                search_type = "similarity_score_threshold"
                search_kwargs = {
                    "score_threshold": search_settings.score_threshold_id if search_settings.score_threshold_id else  0.5,
                    "k": search_settings.search_k if search_settings.search_k else 100
                }
            elif search_settings.search_type == "mmr":
                search_type = "mmr"
                search_kwargs = {"k": search_settings.search_k if search_settings.search_k else 4}
            elif search_settings.search_type == "default":
                search_type = "similarity"
                search_kwargs = {"k": search_settings.search_k if search_settings.search_k else 4}
            else:
                search_type = "mixed"
                search_kwargs = {"k": search_settings.search_k if search_settings.search_k else 4}
        if self.queue:
          await self.queue.put(getRandomWaitingMessage(app_tool.waiting_message, traduction=False))

        return await VectorDbManager.get_strategy(app_tool.vector_type).invoke(
            self.llm.get_embeddings(),
            app_tool.vector_db,
            query,
            search_type,
            search_kwargs,
            app_tool=app_tool,
            llm=self.llm.get_llm(),
            source=app_tool.function_id,
            )

    #region functions
    async def document_retriever(self, query: str) -> list:
        """
        Asynchronously retrieves documents based on the provided query using the specified search settings.

        Args:
          query (str): The search query string.

        Returns:
          list: A list of retrieved documents based on the search criteria.

        Raises:
          ValueError: If the configuration for the tool is invalid or the vector database is not found.

        Notes:
          - The function supports different search types such as "similarity", "similarity_score_threshold", "mmr", and "mixed".
          - The search settings can be customized through the `app_tool.search_settings` attribute.
          - If a queue is provided, a waiting message is put into the queue before invoking the search.
        """
        if (
            self.app_tool.type == "function" and self.app_tool.vector_db
            #and self.settings.get("dataSource") == "knowledgebase"
        ):
            return await self.__extract_documents(query, self.app_tool)

    async def image_generator(self, query: str, language: str = "it"):
        """
        Asynchronously generates an image based on the query.
        set OPENAI_API_KEY in your environment variables
        """
        from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
        model = self.app_tool.model or "dall-e-3"
        random_waiting_message = getRandomWaitingMessage(self.app_tool.waiting_message, traduction=False)
        if not language:
            language = "it"
        await translate_text(
            self.llm, language, random_waiting_message, self.callbacks
        )
        try:
            #set os.environ.get("OPENAI_API_KEY")!
            image_url = DallEAPIWrapper(model=model).run(query)  # type: ignore
            return image_url
        except Exception as e:
            return f"Error: {str(e)}"

    async def llm_chain(self, input: str):
        if self.app_tool.type == "llmChain":
          from langchain_core.prompts import ChatPromptTemplate
          from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
          from pydantic import create_model
          system_message = self.app_tool.llm_chain_settings.prompt
          context = []
          if self.app_tool.data_source == "knowledgebase":
            context = await self.__extract_documents(input, self.app_tool)
          if len(context) > 0:
            for doc in context:
              system_message += f"\n\nContext:\n{doc.metadata.get("source", "")}: {doc.page_content}"
          # Determine output parser and format based on output type
          output_type = self.app_tool.llm_chain_settings.outputStructure.get("outputType")
          is_json_output = output_type == "json"

          if is_json_output:
            output_format = self.app_tool.llm_chain_settings.outputStructure.get("outputFormat", {})
            json_schema = create_model('json_schema', **{k: (type(v), ...) for k, v in output_format.items()})
            output_parser = JsonOutputParser(pydantic_object=json_schema)
            system_message += "\n\nFormat instructions:\n{format_instructions}".strip()
          else:
            output_parser = StrOutputParser()
          # Create prompt template with or without format instructions
          base_messages = [
            ("system", system_message),
            ("user", "{input}")
          ]
          if is_json_output:
            prompt = ChatPromptTemplate.from_messages(base_messages).partial(
              format_instructions=output_parser.get_format_instructions()
            )
          else:
            prompt = ChatPromptTemplate.from_messages(base_messages)
          model = self.app_tool.llm_chain_settings.model
          self.llm.config.model = model
          llm = self.llm.get_llm()
          llm.tags = ["llm_chain"]
          chain = prompt | llm | output_parser
          result = await chain.ainvoke({"input": input})
          return result


    async def search_online(self, query: str):
        from ws_bom_robot_app.llm.tools.utils import fetch_page, extract_content_with_trafilatura
        from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
        import aiohttp, asyncio, ast
        # Wrapper DuckDuckGo
        search = DuckDuckGoSearchAPIWrapper(max_results=10)
        try:
          raw_results = search.results(query, max_results=10)
        except Exception as e:
            print(f"[!] Errore ricerca: {e}")
        urls = [r["link"] for r in raw_results]
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_page(session, url) for url in urls]
            responses = await asyncio.gather(*tasks)
        final_results = []
        for item in responses:
            url = item["url"]
            html = item["html"]
            if html:
                content = await extract_content_with_trafilatura(html)
                if content:
                    final_results.append({"url": url, "content": content})
                else:
                    final_results.append({"url": url, "content": "No content found"})
            else:
                final_results.append({"url": url, "content": "Page not found"})
        return final_results

    async def search_online_google(self, query: str):
      from langchain_google_community import GoogleSearchAPIWrapper
      from ws_bom_robot_app.llm.tools.utils import fetch_page, extract_content_with_trafilatura
      import aiohttp, asyncio
      secrets = {}
      for d in self.app_tool.secrets:
        secrets[d.get("secretId")] = d.get("secretValue")
      search_type = secrets.get("searchType")
      if search_type:
          search_kwargs = {"searchType" : search_type}
      search = GoogleSearchAPIWrapper(
          google_api_key=secrets.get("GOOGLE_API_KEY"),
          google_cse_id=secrets.get("GOOGLE_CSE_ID"),
      )
      if search_type:
          raw_results = search.results(query=query,
                     num_results=secrets.get("num_results", 5),
                     search_params=search_kwargs)
          return raw_results
      raw_results = search.results(
          query=query,
          num_results=secrets.get("num_results", 5)
      )
      urls = [r["link"] for r in raw_results]
      async with aiohttp.ClientSession() as session:
          tasks = [fetch_page(session, url) for url in urls]
          responses = await asyncio.gather(*tasks)
      final_results = []
      for item in responses:
          url = item["url"]
          html = item["html"]
          if html:
              content = await extract_content_with_trafilatura(html)
              if content:
                  final_results.append({"url": url, "content": content, "type": "web"})
              else:
                  final_results.append({"url": url, "content": "No content found", "type": "web"})
          else:
              final_results.append({"url": url, "content": "Page not found", "type": "web"})
      return final_results


    async def send_email(self, email_subject: str, body: str, to_email:str):
        secrets = self.app_tool.secrets
        secrets = {item["secretId"]: item["secretValue"] for item in secrets}
        # Email configuration
        smtp_server = secrets.get("smtp_server")
        smtp_port = secrets.get("smtp_port")
        smtp_user = secrets.get("smtp_user")
        smtp_password = secrets.get("smtp_password")
        from_email = secrets.get("from_email")
        if not to_email or to_email == "":
          return "No recipient email provided"
        if not email_subject or email_subject == "":
          return "No email object provided"
        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = email_subject

        # Create the email body
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        try:
          with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Use authentication and SSL only if password is provided
            if smtp_password:
              server.starttls()
              server.login(smtp_user, smtp_password)
            server.send_message(msg)
        except Exception as e:
          return f"Failed to send email: {str(e)}"
        return "Email sent successfully"

    #endregion

    #class variables (static)
    _list: dict[str,ToolConfig] = {
        "document_retriever": ToolConfig(function=document_retriever, model=DocumentRetrieverInput),
        "image_generator": ToolConfig(function=image_generator, model=ImageGeneratorInput),
        "llm_chain": ToolConfig(function=llm_chain, model=LlmChainInput),
        "search_online": ToolConfig(function=search_online, model=SearchOnlineInput),
        "search_online_google": ToolConfig(function=search_online_google, model=SearchOnlineInput),
        "send_email": ToolConfig(function=send_email, model=EmailSenderInput),
    }

    #instance methods
    def get_coroutine(self):
        tool_cfg = self._list.get(self.app_tool.function_name)
        return getattr(self, tool_cfg.function.__name__)  # type: ignore
