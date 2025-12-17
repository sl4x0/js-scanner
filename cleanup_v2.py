"""
Careful cleanup script to remove words and parameters functionality
This version properly handles method boundaries and indentation
"""
from pathlib import Path
import re


def find_method_end(lines, start_idx):
    """Find the end of a method by looking for the next method at same indent level"""
    # Get the indentation of the method def
    method_line = lines[start_idx]
    base_indent = len(method_line) - len(method_line.lstrip())
    
    # Start from next line
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            continue
            
        # Get current line indent
        current_indent = len(line) - len(line.lstrip())
        
        # If we find a line at same or less indent that's not empty, method ended
        if current_indent <= base_indent:
            # Check if it's a new method or class
            if line.strip().startswith(('def ', 'class ', '#', 'async def')):
                return i
            # If it's something else at base level, also end
            elif current_indent == base_indent:
                return i
    
    return len(lines)


def remove_methods(content, method_names):
    """Remove complete methods from content"""
    lines = content.split('\n')
    
    # Find all method starts
    methods_to_remove = []
    for i, line in enumerate(lines):
        for method_name in method_names:
            if f'def {method_name}(' in line:
                end_idx = find_method_end(lines, i)
                methods_to_remove.append((i, end_idx))
                print(f"  Found {method_name} at lines {i+1}-{end_idx}")
                break
    
    # Remove in reverse order to maintain line numbers
    for start, end in reversed(methods_to_remove):
        lines[start:end] = []
    
    return '\n'.join(lines)


def clean_ast_analyzer():
    """Carefully clean ast_analyzer.py"""
    file_path = Path('jsscanner/modules/ast_analyzer.py')
    content = file_path.read_text(encoding='utf-8')
    
    print(f"\n📝 Cleaning {file_path}...")
    print(f"   Original: {len(content.splitlines())} lines")
    
    # 1. Update docstring
    content = content.replace(
        'Uses Tree-sitter to parse JavaScript and extract endpoints, parameters, and wordlists',
        'Uses Tree-sitter to parse JavaScript and extract endpoints, domains, and links'
    )
    
    # 2. Remove min_word_length
    content = re.sub(
        r'        self\.min_word_length = config\.get.*?\n',
        '',
        content
    )
    
    # 3. Remove params and words from extracts_db
    content = content.replace(
        "        self.extracts_db = {\n            'endpoints': {},  # {endpoint: {sources: [], total_count: 0, domains: set()}}\n            'params': {},\n            'domains': {},\n            'links': {},\n            'words': {}  # Add words tracking for domain-specific wordlists\n        }",
        "        self.extracts_db = {\n            'endpoints': {},  # {endpoint: {sources: [], total_count: 0, domains: set()}}\n            'domains': {},\n            'links': {}\n        }"
    )
    
    # 4. Remove params and wordlist extraction calls
    content = re.sub(
        r'            params = await loop\.run_in_executor.*?_extract_params_sync.*?\n',
        '',
        content
    )
    content = re.sub(
        r'            wordlist = await loop\.run_in_executor.*?_generate_wordlist_sync.*?\n',
        '',
        content
    )
    
    # 5. Remove params tracking loop (careful with indentation)
    params_block_pattern = r'            for param in params:\n(?:                .*\n)*?                self\.extracts_db\[\'params\'\]\[param\]\[\'domains\'\]\.add\(source_domain\)\n'
    content = re.sub(params_block_pattern, '', content)
    
    # 6. Remove params file saving  
    params_save_pattern = r'            if params:\n                await FileOps\.append_unique_lines\(\n                    str\(extracts_path / \'params\.txt\'\),\n                    params\n                \)\n'
    content = re.sub(params_save_pattern, '', content)
    
    # 7. Remove words tracking and saving (all of it)
    words_block_pattern = r'            # Track wordlist with source tracking.*?\n(?:            .*\n)*?                    wordlist\n                \)\n'
    content = re.sub(words_block_pattern, '', content, flags=re.DOTALL)
    
    # 8. Update extraction logging
    content = re.sub(
        r'f"Extracted: \{len\(endpoints\)\} endpoints, \{len\(params\)\} params, "\n                f"\{len\(wordlist\)\} words"',
        'f"Extracted: {len(endpoints)} endpoints, {len(domains)} domains, {len(links)} links"',
        content
    )
    
    # 9. Remove STOP_WORDS constant
    stop_words_pattern = r'    # NEW Phase 3b: Stop words list\n    STOP_WORDS = \{[^}]+\}\n\n'
    content = re.sub(stop_words_pattern, '', content, flags=re.DOTALL)
    
    # 10. Remove methods - use our careful function
    methods_to_remove = [
        '_extract_params_sync',
        '_is_valid_param',
        '_extract_html_input_names',
        '_generate_wordlist_sync',
        '_tokenize_text',
        '_extract_words_from_html',
        '_filter_wordlist'
    ]
    
    print(f"\n   Removing methods:")
    content = remove_methods(content, methods_to_remove)
    
    print(f"   Final: {len(content.splitlines())} lines")
    
    # Save
    file_path.write_text(content, encoding='utf-8')
    print(f"\n✅ Cleaned {file_path}")


def clean_domain_organizer():
    """Clean domain_organizer.py"""
    file_path = Path('jsscanner/modules/domain_organizer.py')
    content = file_path.read_text(encoding='utf-8')
    
    print(f"\n📝 Cleaning {file_path}...")
    
    # Remove 'words' and 'params' from extract_types
    content = re.sub(
        r"for extract_type in \['endpoints', 'params', 'domains', 'links', 'words'\]:",
        "for extract_type in ['endpoints', 'domains', 'links']:",
        content
    )
    
    # Remove words initialization
    content = re.sub(
        r"                            'words': set\(\),?\n",
        "",
        content
    )
    
    # Remove words file saving
    words_save = r"            # Save words\.txt.*?\n(?:            .*\n)*?                    f\.write.*?sorted.*?data\['words'\].*?\)\)\n"
    content = re.sub(words_save, '', content, flags=re.DOTALL)
    
    # Remove words_count
    content = re.sub(
        r"                    'words_count': 0,?\n",
        "",
        content
    )
    
    # Remove words counting
    words_count = r"                # Count words\n(?:                .*\n)*?                        summary\[domain\]\['words_count'\] = len.*?\n"
    content = re.sub(words_count, '', content, flags=re.DOTALL)
    
    file_path.write_text(content, encoding='utf-8')
    print(f"✅ Cleaned {file_path}")


if __name__ == '__main__':
    print("=" * 60)
    print("🧹 Removing words and parameters functionality")
    print("=" * 60)
    
    clean_ast_analyzer()
    clean_domain_organizer()
    
    print("\n" + "=" * 60)
    print("✅ Cleanup complete!")
    print("=" * 60)
    print("\nKept: endpoints, domains, links")
    print("Removed: words, parameters")
