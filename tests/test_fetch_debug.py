"""Quick test to diagnose kick.com fetch failures"""
import asyncio
from curl_cffi.requests import AsyncSession

async def test_fetch():
    """Test direct fetch to see status code"""
    url = "https://kick.com/_next/static/chunks/5429.dac67e98b77fd976.js"
    
    async with AsyncSession(impersonate="chrome120") as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://kick.com/',
            'Origin': 'https://kick.com',
        }
        
        print(f"🔍 Testing: {url}")
        print(f"📤 Headers: {headers}\n")
        
        try:
            response = await session.get(url, headers=headers, timeout=30)
            print(f"✅ Status Code: {response.status_code}")
            print(f"📝 Response Headers:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")
            print(f"\n📦 Content Length: {len(response.text)} bytes")
            print(f"🔍 Content Preview: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_fetch())
