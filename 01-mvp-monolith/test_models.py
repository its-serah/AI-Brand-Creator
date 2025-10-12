#!/usr/bin/env python3
"""
Simple test script to verify AI model generation is working
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project path to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.services.brand_service import BrandService
from api.models.brand import BrandRequest
from api.config import Settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_model_generation():
    """Test the AI model generation with simple parameters"""
    logger.info("Starting AI model test...")
    
    try:
        # Initialize settings
        settings = Settings()
        
        # Create brand service
        brand_service = BrandService(settings)
        
        # Initialize the service (this will load models)
        logger.info("Initializing brand service and loading models...")
        await brand_service.initialize()
        
        # Create a simple test request
        test_request = BrandRequest(
            business_name="TestBrand",
            industry="technology",
            style="minimal",
            color_scheme="cool",
            personality_traits=["professional", "modern"],
            target_audience="professionals",  # Use correct enum value
            prompt="simple clean logo design",
            negative_prompt="complex, cluttered",
            additional_notes="This is a test",
            num_logos=1  # Generate only 1 logo for testing
        )
        
        logger.info("Testing logo generation...")
        logos = await brand_service._generate_logos(test_request)
        
        if logos:
            logger.info(f"SUCCESS: Generated {len(logos)} logos")
            for i, logo in enumerate(logos):
                logger.info(f"Logo {i+1}: ID={logo.id}, Generated with: {logo.metadata.get('generated_with', 'unknown')}")
                logger.info(f"  Style confidence: {logo.style_confidence:.2f}")
                logger.info(f"  Quality score: {logo.quality_score:.2f}")
                
                # Check if image data is valid
                if logo.url.startswith('data:image'):
                    logger.info(f"  Image data: Valid base64 data URL ({len(logo.url)} characters)")
                else:
                    logger.info(f"  Image URL: {logo.url}")
        else:
            logger.error("FAILED: No logos generated")
        
        # Cleanup
        await brand_service.cleanup()
        
        return len(logos) > 0
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function"""
    print("=" * 50)
    print("AI Brand Creator - Model Test")
    print("=" * 50)
    
    success = await test_model_generation()
    
    print("=" * 50)
    if success:
        print("✅ MODEL TEST PASSED")
        print("The AI models are working correctly!")
    else:
        print("❌ MODEL TEST FAILED")
        print("There are issues with the AI model setup.")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
