# AI Analysis Setup Guide

This guide explains how to set up AI-powered analysis for ECG images, X-ray images, and medical reports in DiagnoRx.

## Features

The AI analysis system provides:

1. **ECG Image Analysis**: Heart rate detection, rhythm analysis, abnormality detection
2. **X-ray Image Analysis**: Structure detection, abnormality identification, image quality assessment
3. **Medical Report Analysis**: Text analysis, key findings extraction, recommendation generation

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys (Optional)

For enhanced AI analysis, you can configure API keys:

#### Environment Variables

Create a `.env` file in your project root:

```env
# Hugging Face API (for image analysis)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# OpenAI API (for text analysis)
OPENAI_API_KEY=your_openai_api_key_here
```

#### Free API Options

**Hugging Face (Free Tier)**:

- Sign up at https://huggingface.co/
- Get free API access for image analysis
- Models available: medical image classification, text analysis

**OpenAI (Free Tier)**:

- Sign up at https://openai.com/
- Get free API credits for text analysis
- GPT-3.5-turbo for medical report analysis

## How It Works

### 1. Basic Analysis (No API Keys Required)

The system performs basic analysis using computer vision:

**ECG Analysis**:

- Edge detection to identify waveform patterns
- Peak detection for heart rate estimation
- Rhythm regularity assessment
- Abnormality detection

**X-ray Analysis**:

- Image intensity analysis
- Contrast detection
- Structure identification
- Quality assessment

**Medical Report Analysis**:

- Keyword extraction
- Medical condition identification
- Abnormal value detection
- Recommendation extraction

### 2. Advanced Analysis (With API Keys)

When API keys are configured, the system provides enhanced analysis:

**Hugging Face Integration**:

- Advanced medical image classification
- Pre-trained models for ECG and X-ray analysis
- Real-time image processing

**OpenAI Integration**:

- Natural language processing of medical reports
- Intelligent text analysis
- Contextual understanding

## Usage

### 1. Upload Medical Files

When creating a patient record, upload:

- ECG images (PNG, JPG, JPEG)
- X-ray images (PNG, JPG, JPEG)
- Medical reports (TXT, PDF)

### 2. Automatic Analysis

The system automatically:

1. Analyzes uploaded files
2. Integrates findings with symptom-based diagnosis
3. Provides comprehensive medical recommendations
4. Generates detailed reports

### 3. View Results

Results are displayed in the prescription view with:

- AI analysis findings
- Confidence scores
- Abnormalities detected
- Recommendations

## Configuration

### API Key Setup

1. **Hugging Face**:

   - Visit https://huggingface.co/settings/tokens
   - Create a new token
   - Add to environment variables

2. **OpenAI**:
   - Visit https://platform.openai.com/api-keys
   - Create a new API key
   - Add to environment variables

### Model Configuration

Edit `core/config.py` to customize:

- Model paths
- Confidence thresholds
- Image size limits
- API endpoints

## Testing

### Test Without API Keys

The system works without API keys using basic computer vision analysis:

1. Upload an ECG image
2. Check the analysis results
3. Verify confidence scores

### Test With API Keys

1. Set up API keys
2. Upload medical files
3. Compare basic vs. advanced analysis
4. Check enhanced confidence scores

## Troubleshooting

### Common Issues

1. **Image Analysis Fails**:

   - Check file format (PNG, JPG, JPEG)
   - Ensure file size < 10MB
   - Verify image quality

2. **API Errors**:

   - Verify API keys are correct
   - Check internet connection
   - Ensure API quotas not exceeded

3. **Performance Issues**:
   - Reduce image size
   - Use smaller files
   - Check server resources

### Error Logs

Check Django logs for detailed error information:

```bash
python manage.py runserver
```

## Security Notes

1. **API Keys**: Never commit API keys to version control
2. **Medical Data**: Ensure HIPAA compliance for medical data
3. **File Uploads**: Validate file types and sizes
4. **Privacy**: Implement proper data protection measures

## Future Enhancements

1. **Local Models**: Train custom models for specific medical domains
2. **Real-time Analysis**: Implement streaming analysis
3. **Multi-modal**: Combine image and text analysis
4. **Validation**: Add medical validation workflows

## Support

For issues or questions:

1. Check the Django logs
2. Verify API key configuration
3. Test with sample medical files
4. Review the error messages

## License

This AI analysis system is for educational and demonstration purposes. For medical use, ensure proper validation and regulatory compliance.
