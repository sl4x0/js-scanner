"""
Hashing Utility
SHA256 calculation for file deduplication
"""
import hashlib
import aiofiles


async def calculate_hash(content: str) -> str:
    """
    Calculates SHA256 hash of content
    
    Args:
        content: String content to hash
        
    Returns:
        SHA256 hex digest
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


async def calculate_file_hash(filepath: str) -> str:
    """
    Calculates SHA256 hash of a file
    
    Args:
        filepath: Path to the file
        
    Returns:
        SHA256 hex digest
    """
    sha256_hash = hashlib.sha256()
    
    async with aiofiles.open(filepath, 'rb') as f:
        # Read in chunks to handle large files
        while chunk := await f.read(8192):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()


def calculate_hash_sync(content: str) -> str:
    """
    Synchronous version of calculate_hash
    
    Args:
        content: String content to hash
        
    Returns:
        SHA256 hex digest
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
