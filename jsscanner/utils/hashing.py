"""
Hashing Utility
MD5 calculation for file deduplication (faster than SHA256)
"""
import hashlib
import aiofiles


async def calculate_hash(content: str) -> str:
    """
    Calculates MD5 hash of content
    
    Args:
        content: String content to hash
        
    Returns:
        MD5 hex digest (32 characters)
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


async def calculate_file_hash(filepath: str) -> str:
    """
    Calculates MD5 hash of a file
    
    Args:
        filepath: Path to the file
        
    Returns:
        MD5 hex digest (32 characters)
    """
    md5_hash = hashlib.md5()
    
    async with aiofiles.open(filepath, 'rb') as f:
        # Read in chunks to handle large files
        while chunk := await f.read(8192):
            md5_hash.update(chunk)
    
    return md5_hash.hexdigest()


def calculate_hash_sync(content: str) -> str:
    """
    Synchronous version of calculate_hash
    
    Args:
        content: String content to hash
        
    Returns:
        MD5 hex digest (32 characters)
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()
