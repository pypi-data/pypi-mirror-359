import asyncio
import logging
from typing import Callable, Dict, Generic, Optional, Type, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
import json
import lmnr
from lmnr import Laminar, observe

from browser_use.agent.views import ActionModel, ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.registry.service import Registry
from browser_use.controller.views import (
    ClickElementAction,
    DoDatePickerAction,
    DoneAction,
    GoToUrlAction,
    InputTextAction,
    NoParamsAction,
    OpenTabAction,
    GetAllTabsAction,
    ScrollAction,
    SearchBaiduAction,
    SendKeysAction,
    SwitchTabAction,
    ExtractPageContentAction,
    ClickByPositionAction,
    GetElementsAction
)
from browser_use.utils import time_execution_async, time_execution_sync

logger = logging.getLogger(__name__)

Context = TypeVar('Context')


class Controller(Generic[Context]):
    def __init__(
        self,
        exclude_actions: list[str] = [],
        output_model: Optional[Type[BaseModel]] = None,
    ):
        self.exclude_actions = exclude_actions
        self.output_model = output_model
        # Fix: Remove type parameter since Registry is not a generic class
        self.registry = Registry(exclude_actions)
        self._register_default_actions()

    def _register_default_actions(self):
        """Register all default browser actions"""
        
        if self.output_model is not None:
            # Create a new model that extends the output model with success parameter
            class ExtendedOutputModel(self.output_model):  # type: ignore
                success: bool = True

            @self.registry.action(
                'Complete task - with return text and if the task is finished (success=True) or not yet completly finished (success=False), because last step is reached',
                param_model=ExtendedOutputModel,
            )
            async def done(params: ExtendedOutputModel):
                # Exclude success from the output JSON since it's an internal parameter
                output_dict = params.model_dump(exclude={'success'})
                return ActionResult(is_done=True, success=params.success, extracted_content=json.dumps(output_dict))
        else:
            @self.registry.action(
                'Complete task - with return text and if the task is finished (success=True) or not yet completly finished (success=False), because last step is reached',
                param_model=DoneAction,
            )
            async def done(params: DoneAction):
                return ActionResult(is_done=True, extracted_content=params.text)

        # Basic Navigation Actions
        @self.registry.action(
            'Search the query in Baidu in the current tab, the query should be a search query like humans search in Baidu, concrete and not vague or super long. More the single most important items. ',
            param_model=SearchBaiduAction,
        )
        async def search_baidu(params: SearchBaiduAction, browser: BrowserContext):
            page = await browser.get_current_page()
            await page.goto(f'https://www.baidu.com/s?wd={params.query}')
            await page.wait_for_load_state()
            msg = f'🔍  Searched for "{params.query}" in Baidu'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)

        @self.registry.action('Navigate to URL in the current tab', param_model=GoToUrlAction)
        async def go_to_url(params: GoToUrlAction, browser: BrowserContext):
            page = await browser.get_current_page()
            await page.goto(params.url)
            await page.wait_for_load_state()
            msg = f'🔗  Navigated to {params.url}'
            content = await page.evaluate("""
                () => {
                    let str = document.body.innerText
                        .replace(/\\n+/g, "\\n")
                        .replace(/ +/g, " ")
                        .trim();
                    if (str.length > 20000) {
                        str = str.substring(0, 20000) + "...";
                    }
                    return str;
                }
            """)
            logger.info(msg)
            return ActionResult(extracted_content=content, include_in_memory=True)
        
        @self.registry.action('Get elements', param_model=GetElementsAction)
        async def get_elements(params: GetElementsAction, browser: BrowserContext):
            msg = f'🔍  Got elements'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)
        
        @self.registry.action('Operate the date selector and select the given date', param_model=DoDatePickerAction)
        async def do_date_picker(params: DoDatePickerAction, browser: BrowserContext):
            # session  = await browser.get_session()
            if params.index not in await browser.get_selector_map():
                raise Exception(f'Element with index {params.index} does not exist - retry or use alternative actions')
            element_node = await browser.get_dom_element_by_index(params.index)
            await browser.do_date_picker(element_node, params.date, params.date_range)
            msg = f'🔍  Selected Success with index {params.index}'
            return ActionResult(extracted_content=msg, include_in_memory=True)

        @self.registry.action('Go back', param_model=NoParamsAction)
        async def go_back(_: NoParamsAction, browser: BrowserContext):
            await browser.go_back()
            msg = '🔙  Navigated back'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)

        # wait for x seconds
        @self.registry.action('Wait for x seconds default 3')
        async def wait(seconds: int = 3):
            msg = f'🕒  Waiting for {seconds} seconds'
            logger.info(msg)
            await asyncio.sleep(seconds)
            return ActionResult(extracted_content=msg, include_in_memory=True)

        # Element Interaction Actions
        @self.registry.action('Click element', param_model=ClickElementAction)
        async def click_element(params: ClickElementAction, browser: BrowserContext):
            session = await browser.get_session()

            if params.index not in await browser.get_selector_map():
                raise Exception(f'Element with index {params.index} does not exist - retry or use alternative actions')

            element_node = await browser.get_dom_element_by_index(params.index)
            initial_pages = len(session.context.pages)
            logger.info(f'Initial pages count: {initial_pages}')

            # if element has file uploader then dont click
            if await browser.is_file_uploader(element_node):
                msg = f'Index {params.index} - has an element which opens file upload dialog. To upload files please use a specific function to upload files '
                logger.info(msg)
                return ActionResult(extracted_content=msg, include_in_memory=True)

            msg = None

            try:
                download_path = await browser._click_element_node(element_node)
                
                # # Wait for potential new page events to be processed
                # # Check multiple times over a longer period
                # max_checks = 10
                # check_interval = 0.05  # 50ms intervals
                
                # for i in range(max_checks):
                #     await asyncio.sleep(check_interval)
                #     current_pages = len(session.context.pages)
                #     if current_pages > initial_pages:
                #         logger.info(f'New page detected after {(i+1) * check_interval:.2f}s, pages: {initial_pages} -> {current_pages}')
                #         break
                
                if download_path:
                    msg = f'💾  Downloaded file to {download_path}'
                else:
                    msg = f'🖱️  Clicked button with index {params.index}: {element_node.get_all_text_till_next_clickable_element(max_depth=2)}'

                logger.info(msg)
                logger.debug(f'Element xpath: {element_node.xpath}')
                
                # Final check for new pages
                final_pages = len(session.context.pages)
                logger.info(f'Final pages count: {final_pages}')
                if final_pages > initial_pages:
                    new_tab_msg = 'New tab opened - switching to it'
                    msg += f' - {new_tab_msg}'
                    logger.info(new_tab_msg)
                    await browser.switch_to_tab(-1)
                
                return ActionResult(extracted_content=msg, include_in_memory=True)
            except Exception as e:
                logger.warning(f'Element not clickable with index {params.index} - most likely the page changed')
                return ActionResult(error=str(e))

        @self.registry.action('Click by position', param_model=ClickByPositionAction)
        async def click_by_position(params: ClickByPositionAction, browser: BrowserContext):
            page = await browser.get_current_page()
            # await page.mouse.move(params.x, params.y)
            await page.mouse.click(x=params.x, y=params.y)
            msg = f'🖱️  Clicked at position {params.x}, {params.y}'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)
        @self.registry.action(
            'Input text into a input interactive element',
            param_model=InputTextAction,
        )
        async def input_text(params: InputTextAction, browser: BrowserContext, has_sensitive_data: bool = False):
            if params.index not in await browser.get_selector_map():
                raise Exception(f'Element index {params.index} does not exist - retry or use alternative actions')

            element_node = await browser.get_dom_element_by_index(params.index)
            await browser._input_text_element_node(element_node, params.text)
            if not has_sensitive_data:
                msg = f'⌨️  Input {params.text} into index {params.index}'
            else:
                msg = f'⌨️  Input sensitive data into index {params.index}'
            logger.info(msg)
            logger.debug(f'Element xpath: {element_node.xpath}')
            return ActionResult(extracted_content=msg, include_in_memory=True)

        # Tab Management Actions
        @self.registry.action('Switch tab', param_model=SwitchTabAction)
        async def switch_tab(params: SwitchTabAction, browser: BrowserContext):
            await browser.switch_to_tab(params.page_id)
            # Wait for tab to be ready
            page = await browser.get_current_page()
            await page.wait_for_load_state()
            msg = f'🔄  Switched to tab {params.page_id}'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)

        @self.registry.action('Open url in new tab', param_model=OpenTabAction)
        async def open_tab(params: OpenTabAction, browser: BrowserContext):
            await browser.create_new_tab(params.url)
            msg = f'🔗  Opened new tab with {params.url}'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)
        
        @self.registry.action('Get all tabs', param_model=GetAllTabsAction)
        async def get_all_tabs(params: GetAllTabsAction, browser: BrowserContext):
            list = browser.current_state.tabs
            logger.info(list)
            msg = f'🔗  All tabs: {list}'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True, include_elements=False)

        # Content Actions
        @self.registry.action(
            'Extract page content to retrieve specific information from the page, e.g. all company names, a specifc description, all information about, links with companies in structured format or simply links',
            param_model=ExtractPageContentAction,
        )
        async def extract_content(params: ExtractPageContentAction, browser: BrowserContext):
            page = await browser.get_current_page()
            import markdownify
            # import json
            
            logger.info('Extracting content---')

            content = await page.evaluate("""
                () => {
                    let str = document.body.innerText
                        .replace(/\\n+/g, "\\n")
                        .replace(/ +/g, " ")
                        .trim();
                    if (str.length > 20000) {
                        str = str.substring(0, 20000) + "...";
                    }
                    return str;
                }
            """)
            
            

            # prompt = 'Your task is to extract the content of the page. goal: {goal}, Page: {page}'
            # template = PromptTemplate(input_variables=['goal', 'page'], template=prompt)
            try:
                # output = page_extraction_llm.invoke(template.format(goal=params.goal, page=content))
                msg = f'📄  Extracted from page\n: {page.url}\n'
                logger.info(msg)
                return ActionResult(extracted_content=content, include_in_memory=True)
            except Exception as e:
                logger.debug(f'Error extracting content: {e}')
                msg = f'📄  Extracted from page\n: {content}\n'
                logger.info(msg)
                return ActionResult(extracted_content=content)

        @self.registry.action(
            'Scroll down the page by pixel amount - if no amount is specified, scroll down one page',
            param_model=ScrollAction,
        )
        async def scroll_down(params: ScrollAction, browser: BrowserContext):
            page = await browser.get_current_page()
            if params.amount is not None:
                await page.evaluate(f'window.scrollBy(0, {params.amount});')
            else:
                await page.evaluate('window.scrollBy(0, window.innerHeight);')

            amount = f'{params.amount} pixels' if params.amount is not None else 'one page'
            msg = f'🔍  Scrolled down the page by {amount}'
            logger.info(msg)
            return ActionResult(
                extracted_content=msg,
                include_in_memory=True,
            )

        # scroll up
        @self.registry.action(
            'Scroll up the page by pixel amount - if no amount is specified, scroll up one page',
            param_model=ScrollAction,
        )
        async def scroll_up(params: ScrollAction, browser: BrowserContext):
            page = await browser.get_current_page()
            if params.amount is not None:
                await page.evaluate(f'window.scrollBy(0, -{params.amount});')
            else:
                await page.evaluate('window.scrollBy(0, -window.innerHeight);')

            amount = f'{params.amount} pixels' if params.amount is not None else 'one page'
            msg = f'🔍  Scrolled up the page by {amount}'
            logger.info(msg)
            return ActionResult(
                extracted_content=msg,
                include_in_memory=True,
            )

        @self.registry.action(
            'Scroll to the bottom of the page',
            param_model=NoParamsAction,
        )
        async def scroll_to_bottom(_: NoParamsAction, browser: BrowserContext):
            page = await browser.get_current_page()
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
            msg = '🔍  Scrolled to the bottom of the page'
            logger.info(msg)
            return ActionResult(
                extracted_content=msg,
                include_in_memory=True,
            )

        @self.registry.action(
            'Scroll element to bottom by index',
            param_model=ScrollAction,
        )
        async def scroll_element_to_bottom_by_index(params: ScrollAction, browser: BrowserContext):
            if params.index not in await browser.get_selector_map():
                raise Exception(f'Element with index {params.index} does not exist - retry or use alternative actions')

            element_node = await browser.get_dom_element_by_index(params.index)
            page = await browser.get_current_page()
            try:
                # 首先确保元素在视图中
                locator = page.locator(f'xpath={element_node.xpath}')
                await locator.scroll_into_view_if_needed()
                
                # 执行JavaScript将元素滚动到底部
                await page.evaluate("""
                (xpath) => {
                    const element = document.evaluate(xpath, document, null, 
                                       XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element && element.scrollHeight) {
                        element.scrollTop = element.scrollHeight;
                    }
                }
                """, element_node.xpath)
                
                msg = f'🔍  Scrolled element with index {params.index} to bottom: {element_node.get_all_text_till_next_clickable_element(max_depth=2)}'
                logger.info(msg)
                return ActionResult(extracted_content=msg, include_in_memory=True)
            except Exception as e:
                logger.warning(f'Failed to scroll element with index {params.index} to bottom: {str(e)}')
                return ActionResult(error=str(e))

        # send keys
        @self.registry.action(
            'Send strings of special keys like Escape,Backspace, Insert, PageDown, Delete, Enter, Shortcuts such as `Control+o`, `Control+Shift+T` are supported as well. This gets used in keyboard.press.',
            param_model=SendKeysAction,
        )
        async def send_keys(params: SendKeysAction, browser: BrowserContext):
            page = await browser.get_current_page()

            try:
                await page.keyboard.press(params.keys)
            except Exception as e:
                if 'Unknown key' in str(e):
                    # loop over the keys and try to send each one
                    for key in params.keys:
                        try:
                            await page.keyboard.press(key)
                        except Exception as e:
                            logger.debug(f'Error sending key {key}: {str(e)}')
                            raise e
                else:
                    raise e
            msg = f'⌨️  Sent keys: {params.keys}'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)

        @self.registry.action(
            description='If you dont find something which you want to interact with, scroll to it',
        )
        async def scroll_to_text(text: str, browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                # Try different locator strategies
                locators = [
                    page.get_by_text(text, exact=False),
                    page.locator(f'text={text}'),
                    page.locator(f"//*[contains(text(), '{text}')]"),
                ]

                for locator in locators:
                    try:
                        # First check if element exists and is visible
                        if await locator.count() > 0 and await locator.first.is_visible():
                            await locator.first.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)  # Wait for scroll to complete
                            msg = f'🔍  Scrolled to text: {text}'
                            logger.info(msg)
                            return ActionResult(extracted_content=msg, include_in_memory=True)
                    except Exception as e:
                        logger.debug(f'Locator attempt failed: {str(e)}')
                        continue

                msg = f"Text '{text}' not found or not visible on page"
                logger.info(msg)
                return ActionResult(extracted_content=msg, include_in_memory=True)

            except Exception as e:
                msg = f"Failed to scroll to text '{text}': {str(e)}"
                logger.error(msg)
                return ActionResult(error=msg, include_in_memory=True)

        @self.registry.action(
            description='Get all options from a native dropdown',
        )
        async def get_dropdown_options(index: int, browser: BrowserContext) -> ActionResult:
            """Get all options from a native dropdown"""
            page = await browser.get_current_page()
            selector_map = await browser.get_selector_map()
            dom_element = selector_map[index]

            try:
                # Frame-aware approach since we know it works
                all_options = []
                frame_index = 0

                for frame in page.frames:
                    try:
                        options = await frame.evaluate(
                            """
                            (xpath) => {
                                const select = document.evaluate(xpath, document, null,
                                    XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                if (!select) return null;

                                return {
                                    options: Array.from(select.options).map(opt => ({
                                        text: opt.text,
                                        value: opt.value,
                                        index: opt.index
                                    })),
                                    id: select.id,
                                    name: select.name
                                };
                            }
                            """,
                            dom_element.xpath,
                        )

                        if options:
                            logger.debug(f'Found dropdown in frame {frame_index}')
                            logger.debug(f'Dropdown ID: {options["id"]}, Name: {options["name"]}')

                            formatted_options = []
                            for opt in options['options']:
                                # encoding ensures AI uses the exact string in select_dropdown_option
                                encoded_text = json.dumps(opt['text'])
                                formatted_options.append(f'{opt["index"]}: text={encoded_text}')

                            all_options.extend(formatted_options)

                    except Exception as frame_e:
                        logger.debug(f'Frame {frame_index} evaluation failed: {str(frame_e)}')

                    frame_index += 1

                if all_options:
                    msg = '\n'.join(all_options)
                    msg += '\nUse the exact text string in select_dropdown_option'
                    logger.info(msg)
                    return ActionResult(extracted_content=msg, include_in_memory=True)
                else:
                    msg = 'No options found in any frame for dropdown'
                    logger.info(msg)
                    return ActionResult(extracted_content=msg, include_in_memory=True)

            except Exception as e:
                logger.error(f'Failed to get dropdown options: {str(e)}')
                msg = f'Error getting options: {str(e)}'
                logger.info(msg)
                return ActionResult(extracted_content=msg, include_in_memory=True)

        @self.registry.action(
            description='Select dropdown option for interactive element index by the text of the option you want to select',
        )
        async def select_dropdown_option(
            index: int,
            text: str,
            browser: BrowserContext,
        ) -> ActionResult:
            """Select dropdown option by the text of the option you want to select"""
            page = await browser.get_current_page()
            selector_map = await browser.get_selector_map()
            dom_element = selector_map[index]

            # Validate that we're working with a select element
            if dom_element.tag_name != 'select':
                logger.error(f'Element is not a select! Tag: {dom_element.tag_name}, Attributes: {dom_element.attributes}')
                msg = f'Cannot select option: Element with index {index} is a {dom_element.tag_name}, not a select'
                return ActionResult(extracted_content=msg, include_in_memory=True)

            logger.debug(f"Attempting to select '{text}' using xpath: {dom_element.xpath}")
            logger.debug(f'Element attributes: {dom_element.attributes}')
            logger.debug(f'Element tag: {dom_element.tag_name}')

            xpath = '//' + dom_element.xpath

            try:
                frame_index = 0
                for frame in page.frames:
                    try:
                        logger.debug(f'Trying frame {frame_index} URL: {frame.url}')

                        # First verify we can find the dropdown in this frame
                        find_dropdown_js = """
                            (xpath) => {
                                try {
                                    const select = document.evaluate(xpath, document, null,
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                    if (!select) return null;
                                    if (select.tagName.toLowerCase() !== 'select') {
                                        return {
                                            error: `Found element but it's a ${select.tagName}, not a SELECT`,
                                            found: false
                                        };
                                    }
                                    return {
                                        id: select.id,
                                        name: select.name,
                                        found: true,
                                        tagName: select.tagName,
                                        optionCount: select.options.length,
                                        currentValue: select.value,
                                        availableOptions: Array.from(select.options).map(o => o.text.trim())
                                    };
                                } catch (e) {
                                    return {error: e.toString(), found: false};
                                }
                            }
                        """

                        dropdown_info = await frame.evaluate(find_dropdown_js, dom_element.xpath)

                        if dropdown_info:
                            if not dropdown_info.get('found'):
                                logger.error(f'Frame {frame_index} error: {dropdown_info.get("error")}')
                                continue

                            logger.debug(f'Found dropdown in frame {frame_index}: {dropdown_info}')

                            # "label" because we are selecting by text
                            # nth(0) to disable error thrown by strict mode
                            # timeout=1000 because we are already waiting for all network events, therefore ideally we don't need to wait a lot here (default 30s)
                            selected_option_values = (
                                await frame.locator('//' + dom_element.xpath).nth(0).select_option(label=text, timeout=1000)
                            )

                            msg = f'selected option {text} with value {selected_option_values}'
                            logger.info(msg + f' in frame {frame_index}')

                            return ActionResult(extracted_content=msg, include_in_memory=True)

                    except Exception as frame_e:
                        logger.error(f'Frame {frame_index} attempt failed: {str(frame_e)}')
                        logger.error(f'Frame type: {type(frame)}')
                        logger.error(f'Frame URL: {frame.url}')

                    frame_index += 1

                msg = f"Could not select option '{text}' in any frame"
                logger.info(msg)
                return ActionResult(extracted_content=msg, include_in_memory=True)

            except Exception as e:
                msg = f'Selection failed: {str(e)}'
                logger.error(msg)
                return ActionResult(error=msg, include_in_memory=True)

    def action(self, description: str, **kwargs):
        """Decorator for registering custom actions

        @param description: Describe the LLM what the function does (better description == better function calling)
        """
        return self.registry.action(description, **kwargs)

    @time_execution_sync('--act')
    async def act(
        self,
        action: ActionModel,
        browser_context: BrowserContext,
        page_extraction_llm: Optional[BaseChatModel] = None,
        sensitive_data: Optional[Dict[str, str]] = None,
        available_file_paths: Optional[list[str]] = None,
        context: Context | None = None,
    ) -> ActionResult:
        """Execute an action"""

        try:
            for action_name, params in action.model_dump(exclude_unset=True).items():
                if params is not None:
                    result = await self.registry.execute_action(
                        action_name,
                        params,
                        browser=browser_context,
                        page_extraction_llm=page_extraction_llm,
                        sensitive_data=sensitive_data,
                        available_file_paths=available_file_paths,
                        context=context,
                    )

                    if isinstance(result, str):
                        return ActionResult(extracted_content=result)
                    elif isinstance(result, ActionResult):
                        return result
                    elif result is None:
                        return ActionResult()
                    else:
                        raise ValueError(f'Invalid action result type: {type(result)} of {result}')
            return ActionResult()
        except Exception as e:
            raise e

    @observe(name='controller.multi_act')
    @time_execution_async('--multi-act')
    async def multi_act(
        self,
        actions: list[ActionModel],
        browser_context: BrowserContext,
        check_break_if_paused: Callable[[], bool],
        check_for_new_elements: bool = True,
        page_extraction_llm: Optional[BaseChatModel] = None,
        sensitive_data: Optional[Dict[str, str]] = None,
    ) -> list[ActionResult]:
        """Execute multiple actions"""
        results = []
        session = await browser_context.get_session()
        selector_map = session.cached_state.selector_map
        initial_hash_set = set(dom.hash.branch_path_hash for dom in selector_map.values())

        check_break_if_paused()

        for i, action in enumerate(actions):
            logger.info(f'executing action {i}')
            
            check_break_if_paused()
            
            if action.get_index() is not None and i != 0:
                current_state = await browser_context.get_state()
                current_hash_set = set(dom.hash.branch_path_hash for dom in current_state.selector_map.values())
                
                if check_for_new_elements and not current_hash_set.issubset(initial_hash_set):
                    msg = f'Something new appeared after action {i} / {len(actions)}'
                    logger.info(msg)
                    results.append(ActionResult(extracted_content=msg, include_in_memory=True))
                    break
            
            check_break_if_paused()
            
            results.append(await self.act(action, browser_context, page_extraction_llm, sensitive_data))
            
            logger.debug(f'Executed action {i + 1} / {len(actions)}')
            
            if results[-1].is_done or results[-1].error or i == len(actions) - 1:
                break
            
            await asyncio.sleep(browser_context.config.wait_between_actions)
        
        return results