import os
import re
from typing import List, Optional, Tuple


class WikiLink:
    """Represents an Obsidian wikilink (e.g., `[[TargetNote]]` or `[[TargetNote|Display Text]]`).

    :param target_name: The name of the target note.
    :type target_name: str
    :param full_text: The full wikilink text, including brackets.
    :type full_text: str
    :param display_text: Optional display text for the wikilink. Defaults to None.
    :type display_text: Optional[str]
    :param start_pos: The starting position of the wikilink in the source text. Defaults to None.
    :type start_pos: Optional[int]
    :param end_pos: The ending position of the wikilink in the source text. Defaults to None.
    :type end_pos: Optional[int]
    :param source_file: The path to the file where the wikilink was found. Defaults to None.
    :type source_file: Optional[str]
    """

    def __init__(
        self,
        target_name: str,
        full_text: str,
        display_text: Optional[str] = None,
        start_pos: Optional[int] = None,
        end_pos: Optional[int] = None,
        source_file: Optional[str] = None,
    ):
        self.target_name = target_name
        self.full_text = full_text
        self.display_text = display_text
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.source_file = source_file

    def is_valid(self) -> bool:
        """Checks if the WikiLink object is valid (has target_name and full_text).

        :returns: True if the wikilink is valid, False otherwise.
        :rtype: bool
        """
        return bool(self.target_name) and bool(self.full_text)

    def get_target_path(self) -> str:
        """Generates the expected file path for the target note.

        Currently, it appends '.md' to the target name.
        :returns: The expected file path for the target note.
        :rtype: str
        """
        return f"{self.target_name}.md"

    def __repr__(self):
        """Returns a string representation of the WikiLink object."""
        return f"WikiLink(target_name='{self.target_name}', full_text='{self.full_text}', display_text='{self.display_text}')"


class WikiLinkFactory:
    """A factory class for creating WikiLink objects."""

    @staticmethod
    def create_from_text(
        full_text: str, start_pos: int, end_pos: int, source_file: Optional[str] = None
    ) -> WikiLink:
        """Creates a WikiLink object from a full wikilink string.

        :param full_text: The full wikilink text (e.g., "[[TargetNote]]" or "[[TargetNote|Display]]").
        :type full_text: str
        :param start_pos: The starting position of the wikilink in the source text.
        :type start_pos: int
        :param end_pos: The ending position of the wikilink in the source text.
        :type end_pos: int
        :param source_file: The path to the file where the wikilink was found. Defaults to None.
        :type source_file: Optional[str]
        :returns: A WikiLink object.
        :rtype: WikiLink
        :raises ValueError: If the provided full_text is not a valid wikilink format.
        """
        match = re.match(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", full_text)
        if match:
            target_name = match.group(1)
            display_text = match.group(2) if match.group(2) else None
            return WikiLink(
                target_name=target_name,
                full_text=full_text,
                display_text=display_text,
                start_pos=start_pos,
                end_pos=end_pos,
                source_file=source_file,
            )
        else:
            raise ValueError(f"Invalid wikilink format: {full_text}")

    @staticmethod
    def create_from_target(
        target_name: str,
        display_text: Optional[str] = None,
        source_file: Optional[str] = None,
    ) -> WikiLink:
        """Creates a WikiLink object from a target name and optional display text.

        :param target_name: The name of the target note.
        :type target_name: str
        :param display_text: Optional display text for the wikilink. Defaults to None.
        :type display_text: Optional[str]
        :param source_file: The path to the file where the wikilink will be created. Defaults to None.
        :type source_file: Optional[str]
        :returns: A WikiLink object.
        :rtype: WikiLink
        """
        full_text = f"[[{target_name}]]"
        if display_text:
            full_text = f"[[{target_name}|{display_text}]]"
        return WikiLink(
            target_name=target_name,
            full_text=full_text,
            display_text=display_text,
            start_pos=None,
            end_pos=None,
            source_file=source_file,
        )


class ILinkGenerationStrategy:
    """Abstract base class for defining link generation strategies.

    Concrete strategies should inherit from this class and implement the `generate_link` method.
    """

    def generate_link(self, content: str, context: any) -> WikiLink:
        """Generates a WikiLink based on the provided content and context.

        :param content: The markdown content to analyze for link generation.
        :type content: str
        :param context: Additional context that might be needed by the strategy (e.g., a list of keywords, a similarity model).
        :type context: any
        :returns: A WikiLink object if a link can be generated, otherwise None.
        :rtype: WikiLink
        :raises NotImplementedError: This method must be implemented by concrete strategy classes.
        """
        raise NotImplementedError


class KeywordStrategy(ILinkGenerationStrategy):
    """A concrete strategy for generating WikiLinks based on predefined keywords.

    This is a placeholder implementation. In a real scenario, it would identify keywords in the content
    and create WikiLink objects for them.
    """

    def generate_link(self, content: str, context: any) -> WikiLink:
        """Generates a WikiLink if the content contains the keyword "keyword".

        :param content: The markdown content to analyze.
        :type content: str
        :param context: Not used in this placeholder implementation.
        :type context: any
        :returns: A WikiLink object for "keyword" if found, otherwise None.
        :rtype: WikiLink
        """
        if "keyword" in content:
            return WikiLinkFactory.create_from_target("keyword")
        return None


class SimilarityStrategy(ILinkGenerationStrategy):
    """A concrete strategy for generating WikiLinks based on content similarity.

    This is a placeholder implementation. In a real scenario, it would use NLP techniques
    to find similar concepts and create WikiLink objects.
    """

    def generate_link(self, content: str, context: any) -> WikiLink:
        """Generates a WikiLink if the content contains the keyword "similarity".

        :param content: The markdown content to analyze.
        :type content: str
        :param context: Not used in this placeholder implementation.
        :type context: any
        :returns: A WikiLink object for "similarity" if found, otherwise None.
        :rtype: WikiLink
        """
        if "similarity" in content:
            return WikiLinkFactory.create_from_target("similarity")
        return None


class ObsidianMarkdownSDK:
    """A facade class providing a simplified interface for interacting with Obsidian Markdown documents.

    This SDK offers atomic, composable operations for creating and managing Obsidian wikilinks and tags,
    facilitating the efficient construction of knowledge networks.
    """

    def __init__(
        self, link_generation_strategy: Optional[ILinkGenerationStrategy] = None
    ):
        """Initializes the ObsidianMarkdownSDK.

        :param link_generation_strategy: An optional strategy for generating links.
                                         If None, no automatic link generation will occur.
        :type link_generation_strategy: Optional[ILinkGenerationStrategy]
        """
        self.link_strategy = link_generation_strategy
        self.link_factory = WikiLinkFactory()

    def set_link_generation_strategy(self, strategy: ILinkGenerationStrategy):
        """Sets the link generation strategy for the SDK.

        :param strategy: The strategy to be used for generating links.
        :type strategy: ILinkGenerationStrategy
        """
        self.link_strategy = strategy

    def read_markdown(self, file_path: str) -> str:
        """Reads the content of a Markdown file.

        :param file_path: The path to the Markdown file.
        :type file_path: str
        :returns: The content of the Markdown file as a string.
        :rtype: str
        :raises FileNotFoundError: If the specified file does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def write_markdown(self, file_path: str, content: str) -> bool:
        """Writes content to a Markdown file.

        If the directory for the file does not exist, it will be created.

        :param file_path: The path to the Markdown file.
        :type file_path: str
        :param content: The content to write to the file.
        :type content: str
        :returns: True if the content was successfully written, False otherwise.
        :rtype: bool
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing markdown to {file_path}: {e}")
            return False

    def find_wikilinks(self, markdown_content: str) -> List[WikiLink]:
        """Identifies and extracts all Obsidian wikilinks from the given Markdown content.

        :param markdown_content: The Markdown content to search within.
        :type markdown_content: str
        :returns: A list of WikiLink objects found in the content.
        :rtype: List[WikiLink]
        """
        wikilinks = []
        matches = re.finditer(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", markdown_content)
        for match in matches:
            full_text = match.group(0)
            target_name = match.group(1)
            display_text = match.group(2)
            start_pos = match.start()
            end_pos = match.end()
            wikilinks.append(
                self.link_factory.create_from_text(full_text, start_pos, end_pos)
            )
        return wikilinks

    def insert_wikilink(
        self, markdown_content: str, wikilink: WikiLink, position: int = -1
    ) -> str:
        """Inserts a WikiLink object into the Markdown content at a specified position.

        :param markdown_content: The original Markdown content.
        :type markdown_content: str
        :param wikilink: The WikiLink object to insert.
        :type wikilink: WikiLink
        :param position: The character position at which to insert the wikilink.
                         If -1 (default), the wikilink is appended to the end of the content.
        :type position: int
        :returns: The Markdown content with the wikilink inserted.
        :rtype: str
        :raises ValueError: If an invalid WikiLink object is provided.
        """
        if not wikilink.is_valid():
            raise ValueError("Invalid WikiLink object provided.")

        if position == -1:  # Append to end
            return markdown_content + wikilink.full_text
        else:
            return (
                markdown_content[:position]
                + wikilink.full_text
                + markdown_content[position:]
            )

    def refactor_to_wikilink(
        self,
        original_file_path: str,
        content_to_extract: str,
        new_note_name: str,
        new_note_dir: str = "",
    ) -> Tuple[str, str]:
        """Extracts specific content from an original Markdown file into a new note,
        and replaces the extracted content in the original file with a wikilink to the new note.

        :param original_file_path: The path to the original Markdown file.
        :type original_file_path: str
        :param content_to_extract: The exact content string to be extracted.
        :type content_to_extract: str
        :param new_note_name: The name of the new note (will be used as the target name for the wikilink).
        :type new_note_name: str
        :param new_note_dir: Optional directory where the new note will be created. Defaults to current directory.
        :type new_note_dir: str
        :returns: A tuple containing the path to the new note and the updated content of the original file.
        :rtype: Tuple[str, str]
        :raises ValueError: If the content to extract is not found in the original file.
        """
        original_content = self.read_markdown(original_file_path)

        if content_to_extract not in original_content:
            raise ValueError("Content to extract not found in the original file.")

        new_note_content = content_to_extract

        if new_note_dir:
            os.makedirs(new_note_dir, exist_ok=True)
            new_note_path = os.path.join(new_note_dir, f"{new_note_name}.md")
        else:
            new_note_path = f"{new_note_name}.md"

        self.write_markdown(new_note_path, new_note_content)

        new_wikilink = self.link_factory.create_from_target(new_note_name)

        updated_original_content = original_content.replace(
            content_to_extract, new_wikilink.full_text, 1
        )
        self.write_markdown(original_file_path, updated_original_content)

        return new_note_path, updated_original_content

    def extract_sections(
        self, markdown_content: str, section_type: str = "paragraph"
    ) -> List[str]:
        """Extracts sections from Markdown content based on a specified type.

        :param markdown_content: The Markdown content to extract sections from.
        :type markdown_content: str
        :param section_type: The type of sections to extract ('paragraph' or 'heading'). Defaults to 'paragraph'.
        :type section_type: str
        :returns: A list of extracted sections.
        :rtype: List[str]
        :raises ValueError: If an unsupported section type is provided.
        """
        sections = []
        if section_type == "paragraph":
            sections = [p.strip() for p in markdown_content.split("\n\n") if p.strip()]
        elif section_type == "heading":
            matches = re.finditer(r"^(#+ .*)$", markdown_content, re.MULTILINE)
            last_end = 0
            for match in matches:
                if match.start() > last_end:
                    sections.append(markdown_content[last_end : match.start()].strip())
                sections.append(match.group(0).strip())
                last_end = match.end()
            if last_end < len(markdown_content):
                sections.append(markdown_content[last_end:].strip())
            sections = [s for s in sections if s]
        else:
            raise ValueError(f"Unsupported section type: {section_type}")
        return sections

    def find_tags(self, markdown_content: str) -> List[str]:
        """Identifies and extracts all Obsidian tags (e.g., `#tag` or `#tag/subtag`) from the given Markdown content.

        :param markdown_content: The Markdown content to search within.
        :type markdown_content: str
        :returns: A list of unique tags found in the content.
        :rtype: List[str]
        """
        tags = []
        matches = re.finditer(r"#([a-zA-Z0-9_/-]+)", markdown_content)
        for match in matches:
            tags.append(match.group(1))
        return list(set(tags))

    def add_tags(self, markdown_content: str, tags: List[str]) -> str:
        """Adds specified tags to the Markdown content.

        Currently, tags are appended to the end of the content.

        :param markdown_content: The original Markdown content.
        :type markdown_content: str
        :param tags: A list of tags (strings, without '#') to add.
        :type tags: List[str]
        :returns: The Markdown content with the new tags added.
        :rtype: str
        """
        if not tags:
            return markdown_content

        tags_to_add = " ".join([f"#{tag}" for tag in tags])

        return f"{markdown_content}\n\n{tags_to_add}"


class SimilarityStrategy(ILinkGenerationStrategy):
    """
    Strategy for generating WikiLinks based on similarity.
    """

    def generate_link(self, content: str, context: any) -> WikiLink:
        # This is a placeholder implementation.
        # In a real scenario, it would use NLP techniques to find similar concepts
        # and create WikiLink objects.
        # For demonstration, let's assume 'similarity' is always the target.
        if "similarity" in content:
            return WikiLinkFactory.create_from_target("similarity")
        return None
