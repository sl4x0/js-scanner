#!/usr/bin/env python3
"""Test tree-sitter initialization across versions"""
import sys

def test_tree_sitter_initialization():
    """Test that tree-sitter initializes properly"""
    
    print("Testing tree-sitter initialization...")
    print(f"Python version: {sys.version}")
    
    try:
        import tree_sitter
        print(f"✓ tree-sitter imported")
        
        try:
            from importlib.metadata import version
            ts_version = version('tree-sitter')
        except:
            ts_version = getattr(tree_sitter, '__version__', 'unknown')
        
        print(f"  Version: {ts_version}")
        
    except ImportError as e:
        print(f"❌ tree-sitter not installed: {e}")
        return False
    
    try:
        import tree_sitter_javascript
        print(f"✓ tree-sitter-javascript imported")
        print(f"  Has language(): {callable(getattr(tree_sitter_javascript, 'language', None))}")
        
    except ImportError as e:
        print(f"❌ tree-sitter-javascript not installed: {e}")
        return False
    
    # Test actual initialization
    try:
        from jsscanner.modules.ast_analyzer import ASTAnalyzer
        from jsscanner.utils.logger import setup_logger
        
        logger = setup_logger('test')
        config = {'ast': {'min_word_length': 4}}
        paths = {'base': '.', 'extracts': 'test_output'}
        
        analyzer = ASTAnalyzer(config, logger, paths)
        
        if analyzer.parser:
            print(f"✅ AST Analyzer initialized successfully")
            print(f"   Parser type: {type(analyzer.parser)}")
            
            # Test parsing
            test_code = "const x = 1; function test() { return 'hello'; }"
            tree = analyzer.parser.parse(bytes(test_code, 'utf8'))
            
            if tree and tree.root_node:
                print(f"✅ Test parse successful")
                print(f"   Root node type: {tree.root_node.type}")
                return True
            else:
                print(f"❌ Parse returned invalid tree")
                return False
        else:
            print(f"❌ Parser is None (initialization failed)")
            return False
            
    except Exception as e:
        print(f"❌ Analyzer initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_tree_sitter_initialization()
    exit(0 if success else 1)
