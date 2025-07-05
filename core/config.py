import os
from django.conf import settings

# AI Analysis Configuration
class AIConfig:
    """Configuration for AI analysis services."""
    
    # API Keys (set these as environment variables)
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Model configurations
    ECG_MODEL_PATH = os.path.join(settings.BASE_DIR, 'core', 'ai_models', 'ecg_model.h5')
    XRAY_MODEL_PATH = os.path.join(settings.BASE_DIR, 'core', 'ai_models', 'xray_model.h5')
    
    # Analysis settings
    MAX_IMAGE_SIZE = 1024  # pixels
    CONFIDENCE_THRESHOLD = 0.6
    
    # API endpoints
    HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    
    @classmethod
    def is_configured(cls):
        """Check if AI services are properly configured."""
        return bool(cls.HUGGINGFACE_API_KEY or cls.OPENAI_API_KEY)
    
    @classmethod
    def get_available_services(cls):
        """Get list of available AI services."""
        services = []
        if cls.HUGGINGFACE_API_KEY:
            services.append('huggingface')
        if cls.OPENAI_API_KEY:
            services.append('openai')
        return services 