"""
Cleanup script to remove words and parameters functionality
Keeps only: domains, links, and endpoints
"""
import re
from pathlib import Path


def clean_ast_analyzer():
    """Remove params and words from ast_analyzer.py"""
    file_path = Path('jsscanner/modules/ast_analyzer.py')
    content = file_path.read_text(encoding='utf-8')
    
    print(f"📝 Cleaning {file_path}...")
    
    # 1. Update docstring
    content = content.replace(
        'Uses Tree-sitter to parse JavaScript and extract endpoints, parameters, and wordlists',
        'Uses Tree-sitter to parse JavaScript and extract endpoints, domains, and links'
    )
    
    # 2. Remove min_word_length line
    content = re.sub(
        r'\s+self\.min_word_length = config\.get\(.*?\n',
        '',
        content
    )
    
    # 3. Remove params and wordlist execution
    content = re.sub(
        r'\s+params = await loop\.run_in_executor\(None, self\._extract_params_sync, root_node, content\)\n',
        '',
        content
    )
    content = re.sub(
        r'\s+wordlist = await loop\.run_in_executor\(None, self\._generate_wordlist_sync, root_node, content\)\n',
        '',
        content
    )
    
    # 4. Remove params tracking block
    params_tracking = re.search(
        r'(\s+)for param in params:.*?self\.extracts_db\[\'params\'\]\[param\]\[\'domains\'\]\.add\(source_domain\)',
        content,
        re.DOTALL
    )
    if params_tracking:
        # Find the end (next line after .add())
        end_pos = params_tracking.end()
        # Find next line break
        next_newline = content.find('\n', end_pos)
        content = content[:params_tracking.start()] + content[next_newline+1:]
    
    # 5. Remove params file saving block
    params_save = re.search(
        r'(\s+)if params:.*?params\s*\)',
        content,
        re.DOTALL
    )
    if params_save:
        end_pos = params_save.end()
        next_newline = content.find('\n', end_pos)
        content = content[:params_save.start()] + content[next_newline+1:]
    
    # 6. Remove methods completely
    methods_to_remove = [
        '_extract_params_sync',
        '_is_valid_param',
        '_extract_html_input_names',
        '_generate_wordlist_sync',
        '_tokenize_text',
        '_extract_words_from_html',
        '_filter_wordlist'
    ]
    
    for method in methods_to_remove:
        # Find method start
        pattern = rf'(\n    def {method}\(.*?\n)(?=    def |\nclass |\Z)'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 7. Remove STOP_WORDS constant
    stop_words_pattern = r'\n    # NEW Phase 3b: Stop words list\n    STOP_WORDS = \{[^}]+\}\n'
    content = re.sub(stop_words_pattern, '', content, flags=re.DOTALL)
    
    # 8. Update regex extraction to not reference params/words
    content = re.sub(
        r"'params': \[\],\s*\n\s*'words': \[\]",
        "",
        content
    )
    
    # Save
    file_path.write_text(content, encoding='utf-8')
    print(f"✅ Cleaned {file_path}")
    return content


def clean_domain_organizer():
    """Remove words from domain_organizer.py"""
    file_path = Path('jsscanner/modules/domain_organizer.py')
    content = file_path.read_text(encoding='utf-8')
    
    print(f"📝 Cleaning {file_path}...")
    
    # Remove 'words' from extract types list
    content = re.sub(
        r"'endpoints', 'params', 'domains', 'links', 'words'",
        "'endpoints', 'domains', 'links'",
        content
    )
    
    # Remove words from dictionary initialization
    content = re.sub(
        r"'words': set\(\)",
        "",
        content
    )
    
    # Remove words file saving block
    words_save = re.search(
        r'(\s+)# Save words\.txt.*?sorted\(list\(data\[\'words\'\]\)\)\)',
        content,
        re.DOTALL
    )
    if words_save:
        end_pos = words_save.end()
        next_newline = content.find('\n', end_pos)
        content = content[:words_save.start()] + content[next_newline+1:]
    
    # Remove words_count from summary
    content = re.sub(
        r"'words_count': 0,?\s*\n",
        "",
        content
    )
    
    # Remove words file reading/counting
    words_count = re.search(
        r'(\s+)# Count words.*?summary\[domain\]\[\'words_count\'\] = len\(f\.readlines\(\)\)',
        content,
        re.DOTALL
    )
    if words_count:
        end_pos = words_count.end()
        next_newline = content.find('\n', end_pos)
        content = content[:words_count.start()] + content[next_newline+1:]
    
    file_path.write_text(content, encoding='utf-8')
    print(f"✅ Cleaned {file_path}")


if __name__ == '__main__':
    print("🧹 Starting cleanup of words and parameters functionality...\n")
    
    clean_ast_analyzer()
    clean_domain_organizer()
    
    print("\n✅ Cleanup complete!")
    print("\nRemaining: endpoints, domains, links")
    print("Removed: words, parameters")
