from actions import Action
from pydantic import TypeAdapter, model_validator
from utils.common import OutputParser
from logs import logger
import asyncio
from pydantic import BaseModel
from tools.search_engine import SearchEngine
from tools.web_browser_engine import WebBrowserEngine
from typing import Optional, Any,Callable,Union
from config2 import config
from utils.text import generate_prompt_chunk, reduce_message_length
from schema import Message

LANG_PROMPT = "Please respond in {language}."

RESEARCH_BASE_SYSTEM = """You are an AI critical thinker research assistant. Your sole purpose is to write well \
written, critically acclaimed, objective and structured reports on the given text."""

RESEARCH_TOPIC_SYSTEM = "You are an AI researcher assistant, and your research topic is:\n#TOPIC#\n{topic}"

SEARCH_TOPIC_PROMPT = """Please provide up to 2 necessary keywords related to your research topic for Google search. \
Your response must be in JSON format, for example: ["keyword1", "keyword2"]."""

SUMMARIZE_SEARCH_PROMPT = """### Requirements
1. The keywords related to your research topic and the search results are shown in the "Search Result Information" section.
2. Provide up to {decomposition_nums} queries related to your research topic base on the search results.
3. Please respond in the following JSON format: ["query1", "query2", "query3", ...].

### Search Result Information
{search_results}
"""

COLLECT_AND_RANKURLS_PROMPT = """### Topic
{topic}
### Query
{query}

### The online search results
{results}

### Requirements
Please remove irrelevant search results that are not related to the query or topic. Then, sort the remaining search results \
based on the link credibility. If two results have equal credibility, prioritize them based on the relevance. Provide the
ranked results' indices in JSON format, like [0, 1, 3, 4, ...], without including other words.
"""

WEB_BROWSE_AND_SUMMARIZE_PROMPT = """### Requirements
1. Utilize the text in the "Reference Information" section to respond to the question "{query}".
2. If the question cannot be directly answered using the text, but the text is related to the research topic, please provide \
a comprehensive summary of the text.
3. If the text is entirely unrelated to the research topic, please reply with a simple text "Not relevant."
4. Include all relevant factual information, numbers, statistics, etc., if available.

### Reference Information
{content}
"""


CONDUCT_RESEARCH_PROMPT = """### Reference Information
{content}

### Requirements
Please provide a detailed research report in response to the following topic: "{topic}", using the information provided \
above. The report must meet the following requirements:

- Focus on directly addressing the chosen topic.
- Ensure a well-structured and in-depth presentation, incorporating relevant facts and figures where available.
- Present data and findings in an intuitive manner, utilizing feature comparative tables, if applicable.
- The report should have a minimum word count of 2,000 and be formatted with Markdown syntax following APA style guidelines.
- Include all source URLs in APA format at the end of the report.
"""

class Report(BaseModel):
    topic: str
    links: dict[str, list[str]] = None
    summaries: list[tuple[str, str]] = None
    content: str = ""

class CollectLinks(Action):
    name: str = "CollectLinks"
    i_context: Optional[str] = None
    desc: str = "Collect links from a search engine."
    search_func: Optional[Any] = None
    search_engine: Optional[SearchEngine] = None
    rank_func: Optional[Callable[[list[str]], None]] = None

    @model_validator(mode="after")
    def validate_engine_and_run_func(self):
        if self.search_engine is None:
            self.search_engine = SearchEngine.from_search_config(self.config.search, proxy=self.config.proxy)
        return self
    async def run(self,topic:str,decomposition_nums:int=4,url_per_query:int=4,system_text:str=None):
        """
        从搜索引擎中进行搜索，并获取url地址信息
        Args:
            topic: 待调研的系统
            decompsition_nums: 子问题拆解
            url_per_query: 每个子问题搜索的生成的URL数
            system_text: 系统提示词
        Returns:
            搜索结果字典，键为子问题，值为URL列表
        """
        system_text = system_text if system_text else RESEARCH_TOPIC_SYSTEM.format(topic=topic)
        # 讲调研问题拆解为多个子问题
        keywords = await self._aask(SEARCH_TOPIC_PROMPT, [system_text])
        try:
            keywords = OutputParser.extract_struct(keywords, list)
            keywords = TypeAdapter(list[str]).validate_python(keywords)
        except Exception as e:
            logger.exception(f"fail to get keywords related to the research topic '{topic}' for {e}")
            keywords = [topic]
        results = await asyncio.gather(*(self.search_engine.run(i, as_string=False) for i in keywords)) 
        def gen_msg():
            while True:
                search_results = "\n".join(
                    f"#### Keyword: {i}\n Search Result: {j}\n" for (i, j) in zip(keywords, results)
                )
                prompt = SUMMARIZE_SEARCH_PROMPT.format(
                    decomposition_nums=decomposition_nums, search_results=search_results
                )
                yield prompt
                remove = max(results, key=len)
                remove.pop()
                if len(remove) == 0:
                    break

        model_name = config.llm.model
        prompt = reduce_message_length(gen_msg(), model_name, system_text, config.llm.max_token)
        logger.debug(prompt)
        queries = await self._aask(prompt, [system_text])
        try:
            queries = OutputParser.extract_struct(queries, list)
            queries = TypeAdapter(list[str]).validate_python(queries)
        except Exception as e:
            logger.exception(f"fail to break down the research question due to {e}")
            queries = keywords
        ret = {}
        for query in queries:
            ret[query] = await self._search_and_rank_urls(topic, query, url_per_query)
        return ret
    async def _search_and_rank_urls(self, topic: str, query: str, num_results: int = 4) -> list[str]:
        """Search and rank URLs based on a query.

        Args:
            topic: The research topic.
            query: The search query.
            num_results: The number of URLs to collect.

        Returns:
            A list of ranked URLs.
        """
        max_results = max(num_results * 2, 6)
        results = await self.search_engine.run(query, max_results=max_results, as_string=False)
        _results = "\n".join(f"{i}: {j}" for i, j in zip(range(max_results), results))
        prompt = COLLECT_AND_RANKURLS_PROMPT.format(topic=topic, query=query, results=_results)
        logger.debug(prompt)
        indices = await self._aask(prompt)
        try:
            indices = OutputParser.extract_struct(indices, list)
            assert all(isinstance(i, int) for i in indices)
        except Exception as e:
            logger.exception(f"fail to rank results for {e}")
            indices = list(range(max_results))
        results = [results[i] for i in indices]
        if self.rank_func:
            results = self.rank_func(results)
        return [i["link"] for i in results[:num_results]]

class WebBrowseAndSummarize(Action):
    """Action class to explore the web and provide summaries of articles and webpages."""

    name: str = "WebBrowseAndSummarize"
    i_context: Optional[str] = None
    desc: str = "Explore the web and provide summaries of articles and webpages."
    browse_func: Union[Callable[[list[str]], None], None] = None
    web_browser_engine: Optional[WebBrowserEngine] = None

    @model_validator(mode="after")
    def validate_engine_and_run_func(self):
        if self.web_browser_engine is None:
            self.web_browser_engine = WebBrowserEngine.from_browser_config(
                self.config.browser,
                browse_func=self.browse_func,
                proxy=self.config.proxy,
            )
        return self

    async def run(
        self,
        url: str,
        *urls: str,
        query: str,
        system_text: str = RESEARCH_BASE_SYSTEM,
    ) -> dict[str, str]:
        """Run the action to browse the web and provide summaries.

        Args:
            url: The main URL to browse.
            urls: Additional URLs to browse.
            query: The research question.
            system_text: The system text.

        Returns:
            A dictionary containing the URLs as keys and their summaries as values.
        """
        contents = await self.web_browser_engine.run(url, *urls)
        if not urls:
            contents = [contents]

        summaries = {}
        prompt_template = WEB_BROWSE_AND_SUMMARIZE_PROMPT.format(query=query, content="{}")
        for u, content in zip([url, *urls], contents):
            content = content.inner_text
            chunk_summaries = []
            for prompt in generate_prompt_chunk(content, prompt_template, self.llm.model, system_text, 4096):
                logger.debug(prompt)
                summary = await self._aask(prompt, [system_text])
                if summary == "Not relevant.":
                    continue
                chunk_summaries.append(summary)

            if not chunk_summaries:
                summaries[u] = None
                continue

            if len(chunk_summaries) == 1:
                summaries[u] = chunk_summaries[0]
                continue

            content = "\n".join(chunk_summaries)
            prompt = WEB_BROWSE_AND_SUMMARIZE_PROMPT.format(query=query, content=content)
            summary = await self._aask(prompt, [system_text])
            summaries[u] = summary
        return summaries


class ConductResearch(Action):
    """Action class to conduct research and generate a research report."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def run(
        self,
        topic: str,
        content: str,
        system_text: str = RESEARCH_BASE_SYSTEM,
    ) -> str:
        """Run the action to conduct research and generate a research report.

        Args:
            topic: The research topic.
            content: The content for research.
            system_text: The system text.

        Returns:
            The generated research report.
        """
        prompt = CONDUCT_RESEARCH_PROMPT.format(topic=topic, content=content)
        logger.debug(prompt)
        self.llm.auto_max_tokens = True
        return await self._aask(prompt, [system_text])

def get_research_system_text(topic: str, language: str):
    """Get the system text for conducting research.

    Args:
        topic: The research topic.
        language: The language for the system text.

    Returns:
        The system text for conducting research.
    """
    return " ".join((RESEARCH_TOPIC_SYSTEM.format(topic=topic), LANG_PROMPT.format(language=language)))

def research_system_text(self, topic, current_task: Action) -> str:
        """BACKWARD compatible
        This allows sub-class able to define its own system prompt based on topic.
        return the previous implementation to have backward compatible
        Args:
            topic:
            language:

        Returns: str
        """
        return get_research_system_text(topic, self.language)

def get_research_system_text(topic: str, language: str):
    """Get the system text for conducting research.

    Args:
        topic: The research topic.
        language: The language for the system text.

    Returns:
        The system text for conducting research.
    """
    return " ".join((RESEARCH_TOPIC_SYSTEM.format(topic=topic), LANG_PROMPT.format(language=language)))

class SearchDomainKnowledge(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please get some domain knowlege for the developing system."
        rsp = await self._aask(prompt)
        return rsp
        # collectaction = CollectLinks()
        # links = await collectaction.run(topic,4,4)
        # webbrowse = WebBrowseAndSummarize()
        # research_system_text = research_system_text(topic,webbrowse)
        # todos = (webbrowse.run(*url, query=query, system_text=research_system_text) for (query, url) in links.items())
        # summaries = await asyncio.gather(*todos)
        # summaries = list((url, summary) for i in summaries for (url, summary) in i.items() if summary)
        # conductre = ConductResearch()
        # summary_text = "\n---\n".join(f"url: {url}\nsummary: {summary}" for (url, summary) in summaries)
        # content = await conductre.run(topic, summary_text, system_text=research_system_text)
        # return Report(
        #     topic=topic,
        #     links=links,
        #     summaries=summaries,
        #     content=content
        # )
