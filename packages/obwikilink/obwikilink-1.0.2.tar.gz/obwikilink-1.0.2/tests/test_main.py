import pytest
import os
from obwikilink.core import WikiLink, WikiLinkFactory, ObsidianMarkdownSDK, KeywordStrategy, SimilarityStrategy, ILinkGenerationStrategy

# Test WikiLink Class
def test_wikilink_creation():
    link = WikiLink("TargetNote", "[[TargetNote]]")
    assert link.target_name == "TargetNote"
    assert link.full_text == "[[TargetNote]]"
    assert link.is_valid() == True

def test_wikilink_with_display_text():
    link = WikiLink("TargetNote", "[[TargetNote|Display Text]]", "Display Text")
    assert link.display_text == "Display Text"

def test_wikilink_get_target_path():
    link = WikiLink("TargetNote", "[[TargetNote]]")
    assert link.get_target_path() == "TargetNote.md"

# Test WikiLinkFactory Class
def test_wikilink_factory_create_from_text():
    link = WikiLinkFactory.create_from_text("[[TestNote]]", 0, 12)
    assert link.target_name == "TestNote"
    assert link.full_text == "[[TestNote]]"
    assert link.start_pos == 0
    assert link.end_pos == 12

def test_wikilink_factory_create_from_text_with_display():
    link = WikiLinkFactory.create_from_text("[[TestNote|Display]]", 0, 19)
    assert link.target_name == "TestNote"
    assert link.display_text == "Display"

def test_wikilink_factory_create_from_target():
    link = WikiLinkFactory.create_from_target("NewNote")
    assert link.target_name == "NewNote"
    assert link.full_text == "[[NewNote]]"

def test_wikilink_factory_create_from_target_with_display():
    link = WikiLinkFactory.create_from_target("NewNote", "New Display")
    assert link.target_name == "NewNote"
    assert link.full_text == "[[NewNote|New Display]]"
    assert link.display_text == "New Display"

# Test ObsidianMarkdownSDK - File I/O
def test_sdk_write_and_read_markdown(tmp_path):
    sdk = ObsidianMarkdownSDK()
    file_path = tmp_path / "test.md"
    content = "# Hello World\nThis is a test."
    
    assert sdk.write_markdown(str(file_path), content) == True
    assert sdk.read_markdown(str(file_path)) == content

def test_sdk_read_non_existent_file(tmp_path):
    sdk = ObsidianMarkdownSDK()
    file_path = tmp_path / "non_existent.md"
    with pytest.raises(FileNotFoundError):
        sdk.read_markdown(str(file_path))

# Test ObsidianMarkdownSDK - Wikilink Handling
def test_sdk_find_wikilinks():
    sdk = ObsidianMarkdownSDK()
    content = "This is a [[Note1]] and another [[Note2|Display]]."
    links = sdk.find_wikilinks(content)
    assert len(links) == 2
    assert links[0].target_name == "Note1"
    assert links[1].target_name == "Note2"
    assert links[1].display_text == "Display"

def test_sdk_insert_wikilink_append():
    sdk = ObsidianMarkdownSDK()
    content = "Existing content."
    new_link = WikiLinkFactory.create_from_target("AppendedNote")
    updated_content = sdk.insert_wikilink(content, new_link)
    assert updated_content == "Existing content.[[AppendedNote]]"

def test_sdk_insert_wikilink_at_position():
    sdk = ObsidianMarkdownSDK()
    content = "Insert here."
    new_link = WikiLinkFactory.create_from_target("InsertedNote")
    updated_content = sdk.insert_wikilink(content, new_link, 7)
    assert updated_content == "Insert [[InsertedNote]]here."

# Test ObsidianMarkdownSDK - Content Refactoring
def test_sdk_refactor_to_wikilink(tmp_path):
    sdk = ObsidianMarkdownSDK()
    original_file = tmp_path / "original.md"
    new_note_dir = tmp_path / "notes"
    
    original_content = "This is some content. Extract this part. More content."
    sdk.write_markdown(str(original_file), original_content)

    content_to_extract = "Extract this part."
    new_note_name = "ExtractedNote"

    new_note_path, updated_original_content = sdk.refactor_to_wikilink(
        str(original_file), content_to_extract, new_note_name, str(new_note_dir)
    )

    assert os.path.exists(new_note_path)
    assert sdk.read_markdown(new_note_path) == content_to_extract
    assert "[[ExtractedNote]]" in updated_original_content
    assert content_to_extract not in updated_original_content
    assert sdk.read_markdown(str(original_file)) == "This is some content. [[ExtractedNote]] More content."

def test_sdk_extract_sections_paragraph():
    sdk = ObsidianMarkdownSDK()
    content = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
    sections = sdk.extract_sections(content, 'paragraph')
    assert len(sections) == 3
    assert sections[0] == "Paragraph 1."
    assert sections[1] == "Paragraph 2."

def test_sdk_extract_sections_heading():
    sdk = ObsidianMarkdownSDK()
    content = "# Heading 1\nContent 1.\n## Subheading 1\nContent 2.\n# Heading 2\nContent 3."
    sections = sdk.extract_sections(content, 'heading')
    assert len(sections) == 6 # Includes content between headings
    assert sections[0] == "# Heading 1"
    assert sections[1] == "Content 1."
    assert sections[2] == "## Subheading 1"
    assert sections[3] == "Content 2."
    assert sections[4] == "# Heading 2"
    assert sections[5] == "Content 3."

# Test ObsidianMarkdownSDK - Tag Handling
def test_sdk_find_tags():
    sdk = ObsidianMarkdownSDK()
    content = "This has #tag1 and #tag2/subtag. Also #tag1 again."
    tags = sdk.find_tags(content)
    assert len(tags) == 2
    assert "tag1" in tags
    assert "tag2/subtag" in tags

def test_sdk_add_tags():
    sdk = ObsidianMarkdownSDK()
    content = "Original content."
    tags_to_add = ["newtag1", "newtag2"]
    updated_content = sdk.add_tags(content, tags_to_add)
    assert updated_content == "Original content.\n\n#newtag1 #newtag2"

# Test Strategy Pattern Integration
def test_sdk_set_link_generation_strategy():
    sdk = ObsidianMarkdownSDK()
    keyword_strategy = KeywordStrategy()
    sdk.set_link_generation_strategy(keyword_strategy)
    assert sdk.link_strategy is keyword_strategy

def test_keyword_strategy_generate_link():
    strategy = KeywordStrategy()
    link = strategy.generate_link("This content has keyword.", None)
    assert link.target_name == "keyword"

def test_similarity_strategy_generate_link():
    strategy = SimilarityStrategy()
    link = strategy.generate_link("This content has similarity.", None)
    assert link.target_name == "similarity"
