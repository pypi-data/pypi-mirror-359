from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Dict, List, Optional
from browser_use.dom.history_tree_processor.view import CoordinateSet, HashedDomElement, ViewportInfo

# Avoid circular import issues
if TYPE_CHECKING:
    from .views import DOMElementNode


@dataclass(frozen=False)
class DOMBaseNode:
    is_visible: bool
    # Use None as default and set parent later to avoid circular reference issues
    parent: Optional['DOMElementNode'] = None


@dataclass(frozen=False)
class DOMTextNode(DOMBaseNode):
    # Fix: Use field() with default_factory to avoid non-default argument following default argument
    text: str = field(default="")  # Give text a default value
    type: str = 'TEXT_NODE'

    def has_parent_with_highlight_index(self) -> bool:
        current = self.parent
        while current is not None:
            # stop if the element has a highlight index (will be handled separately)
            if current.highlight_index is not None:
                return True

            current = current.parent
        return False

    def is_parent_in_viewport(self) -> bool:
        if self.parent is None:
            return False
        return self.parent.is_in_viewport

    def is_parent_top_element(self) -> bool:
        if self.parent is None:
            return False
        return self.parent.is_top_element


@dataclass(frozen=False)
class DOMElementNode(DOMBaseNode):
    """
    xpath: the xpath of the element from the last root node (shadow root or iframe OR document if no shadow root or iframe).
    To properly reference the element we need to recursively switch the root node until we find the element (work you way up the tree with `.parent`)
    """

    # Fix: Give default values to all required parameters that follow a parameter with a default
    tag_name: str = field(default="")
    component_type: str = field(default="")
    component_props: Dict[str, str] = field(default_factory=dict)
    xpath: str = field(default="")
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List[DOMBaseNode] = field(default_factory=list)
    desc: str = field(default="")
    is_interactive: bool = False
    is_scroll_element: bool = False
    is_top_element: bool = False
    is_in_viewport: bool = False
    shadow_root: bool = False
    highlight_index: Optional[int] = None
    viewport_coordinates: Optional[CoordinateSet] = None
    page_coordinates: Optional[CoordinateSet] = None
    viewport_info: Optional[ViewportInfo] = None

    def __repr__(self) -> str:
        tag_str = f'<{self.tag_name}'

        # Add attributes
        for key, value in self.attributes.items():
            tag_str += f' {key}="{value}"'
        tag_str += '>'

        # Add extra info
        extras = []
        if self.is_interactive:
            extras.append('interactive')
        if self.is_top_element:
            extras.append('top')
        if self.shadow_root:
            extras.append('shadow-root')
        if self.highlight_index is not None:
            extras.append(f'highlight:{self.highlight_index}')
        if self.is_in_viewport:
            extras.append('in-viewport')

        if extras:
            tag_str += f' [{", ".join(extras)}]'

        return tag_str

    @cached_property
    def hash(self) -> HashedDomElement:
        from browser_use.dom.history_tree_processor.service import (
            HistoryTreeProcessor,
        )

        return HistoryTreeProcessor._hash_dom_element(self)

    def get_all_text_till_next_clickable_element(self, max_depth: int = -1) -> str:
        text_parts = []

        def collect_text(node: DOMBaseNode, current_depth: int) -> None:
            if max_depth != -1 and current_depth > max_depth:
                return

            # Skip this branch if we hit a highlighted element (except for the current node)
            if isinstance(node, DOMElementNode) and node != self and node.highlight_index is not None:
                return

            if isinstance(node, DOMTextNode):
                text_parts.append(node.text)
            elif isinstance(node, DOMElementNode):
                for child in node.children:
                    collect_text(child, current_depth + 1)

        collect_text(self, 0)
        return '\n'.join(text_parts).strip()

    # Note: the time_execution_sync decorator is missing from the provided code
    # Commenting it out for now
    # @time_execution_sync('--clickable_elements_to_string')
    def clickable_elements_to_string(self, include_attributes: list[str] | None = None) -> str:
        """Convert the processed DOM content to HTML."""
        formatted_text = []

        def process_node(node: DOMBaseNode, depth: int) -> None:
            if isinstance(node, DOMElementNode):
                # Add element with highlight_index
                if node.highlight_index is not None:
                    attributes_str = ''
                    if(node.is_scroll_element):
                        text = ''
                    else:
                        text = node.get_all_text_till_next_clickable_element()
                    if include_attributes:
                        attributes = list(
                            set(
                                [
                                    str(value)
                                    for key, value in node.attributes.items()
                                    if key in include_attributes and value != node.tag_name
                                ]
                            )
                        )
                        if text in attributes:
                            attributes.remove(text)
                        attributes_str = ';'.join(attributes)
                    if node.desc:
                        line = f'[{node.highlight_index}]:({node.desc})<{node.tag_name}'
                        for key in node.attributes.keys():
                            if key != 'style':
                                line += f' {key}="{node.attributes[key]}"'
                        line += ' '
                    if node.component_type: 
                        match node.component_type:
                            case 'DatePicker':
                                time_value = node.component_props.get('showTime', False)
                                range_value = node.component_props.get('isRange', False)
                                time_value = 'true' if time_value else 'false'
                                range_value = 'true' if range_value else 'false'
                                line = f'[{node.highlight_index}]:<{node.component_type} time={time_value} range={range_value} format={node.component_props.get("format", "YYYY-MM-DD")} />'
                            case _:
                                pass                                
                    else:
                        line = f'[{node.highlight_index}]:<{node.tag_name}'
                        for key in node.attributes.keys():
                            if key != 'style':
                                line += f' {key}="{node.attributes[key]}"'
                    if attributes_str:
                        line += f'{attributes_str}'
                    if text:
                        if attributes_str:
                            line += f'>{text}'
                        else:
                            line += f' {text}'

                    line += '/>'
                    
                    formatted_text.append(line)

                # Process children regardless
                for child in node.children:
                    process_node(child, depth + 1)

            elif isinstance(node, DOMTextNode):
                # Add text only if it doesn't have a highlighted parent
                if not node.has_parent_with_highlight_index() and node.is_visible:
                    formatted_text.append(f'{node.text}')

        process_node(self, 0)
        return '\n'.join(formatted_text)

    def get_file_upload_element(self, check_siblings: bool = True) -> Optional['DOMElementNode']:
        # Check if current element is a file input
        if self.tag_name == 'input' and self.attributes.get('type') == 'file':
            return self

        # Check children
        for child in self.children:
            if isinstance(child, DOMElementNode):
                result = child.get_file_upload_element(check_siblings=False)
                if result:
                    return result

        # Check siblings only for the initial call
        if check_siblings and self.parent:
            for sibling in self.parent.children:
                if sibling is not self and isinstance(sibling, DOMElementNode):
                    result = sibling.get_file_upload_element(check_siblings=False)
                    if result:
                        return result

        return None

    def get_advanced_css_selector(self) -> str:
        from browser_use.browser.context import BrowserContext
        return BrowserContext._enhanced_css_selector_for_element(self)


class ElementTreeSerializer:
    @staticmethod
    def serialize_clickable_elements(element_tree):
        return element_tree.clickable_elements_to_string()
    
    @staticmethod
    def dom_element_node_to_json(element_tree):
        def process_node(node):
            if isinstance(node, DOMTextNode):
                return {
                    'type': 'text',
                    'text': node.text
                }
            elif isinstance(node, DOMElementNode):
                return {
                    'type': 'element',
                    'tag_name': node.tag_name,
                    'attributes': node.attributes,
                    'highlight_index': node.highlight_index,
                    'children': [process_node(child) for child in node.children]
                }
            return None
            
        return process_node(element_tree)


SelectorMap = Dict[int, DOMElementNode]


@dataclass
class DOMState:
    element_tree: DOMElementNode
    selector_map: SelectorMap