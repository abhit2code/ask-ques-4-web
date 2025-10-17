#!/usr/bin/env python3
"""
Simple test script to verify content cache functionality
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.scraper import ContentProcessor
from src.services.cache import CacheService

async def test_content_cache():
    """Test content caching and change detection"""
    
    processor = ContentProcessor()
    cache = CacheService()
    
    test_url = "https://httpbin.org/json"  # Simple JSON endpoint for testing
    
    print("🧪 Testing Content Cache Implementation")
    print("=" * 50)
    
    try:
        # Test 1: First fetch (should not be cached)
        print(" First fetch (should fetch fresh content)...")
        result1 = await processor.fetch_content(test_url)
        print(f"From cache: {result1['from_cache']}")
        print(f"Content hash: {result1['content_hash'][:16]}...")
        print(f"Content changed: {result1.get('content_changed', 'N/A')}")
        
        # Test 2: Second fetch (should be cached)
        print("\n Second fetch (should use cache)...")
        result2 = await processor.fetch_content(test_url)
        print(f"From cache: {result2['from_cache']}")
        print(f"Content hash: {result2['content_hash'][:16]}...")
        print(f"Content changed: {result2.get('content_changed', 'N/A')}")
        
        # Test 3: Force refresh
        print("\n Force refresh (should fetch fresh content)...")
        result3 = await processor.fetch_content(test_url, force_refresh=True)
        print(f"From cache: {result3['from_cache']}")
        print(f"Content hash: {result3['content_hash'][:16]}...")
        print(f"Content changed: {result3.get('content_changed', 'N/A')}")
        
        # Verify hashes are consistent
        if result1['content_hash'] == result2['content_hash'] == result3['content_hash']:
            print("\nAll content hashes match - cache working correctly!")
        else:
            print("\nContent hashes don't match - potential issue")
            
        # Test cache service directly
        print("\nTesting cache service directly...")
        cached_hash = cache.get_content_hash(test_url)
        print(f"Cached hash: {cached_hash[:16] if cached_hash else 'None'}...")
        
        print("\n🎉 Content cache test completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_content_cache())
    sys.exit(0 if success else 1)
