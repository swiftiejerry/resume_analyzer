from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from models.resume import ResumeAnalyzeResponse, ResumeMatchResponse, JobDescriptionRequest, ResumeData, MatchResult, BasicInfo

import hashlib
from core.config import settings

# Since we haven't initialized Redis dependency properly yet, we'll instantiate it here for demo
from services.redis_service import RedisService
from services.pdf_service import PDFService
from services.ai_service import AIService

router = APIRouter()
redis_service = RedisService(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
# Optional: print warning if Redis not available, but logic will fallback or fail

@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_bytes = await file.read()
    
    # Calculate md5 hash for unique identifier
    file_hash = hashlib.md5(file_bytes).hexdigest()
    resume_id = file_hash
    
    # Try fetching from cache
    try:
        cached_data = redis_service.get_resume_data(resume_id)
        if cached_data:
            return ResumeAnalyzeResponse(
                resume_id=resume_id,
                data=ResumeData(**cached_data),
                message="Success (Cache Hit)"
            )
    except Exception as e:
        print(f"Cache check failed: {e}")
        pass # Ignore cache failure and proceed
        
    # PDF Parsing - try text extraction first
    raw_text = ""
    is_image_pdf = False
    try:
        raw_text = PDFService.extract_text(file_bytes)
        if not raw_text or not raw_text.strip():
            # Check if it's an image-based/vector-drawn PDF
            is_image_pdf = PDFService.is_image_based_pdf(file_bytes)
            if not is_image_pdf:
                raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # AI Info Extraction
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        # Fallback dummy data if no key configured
        dummy_data = {
            "basic_info": BasicInfo(name="Test User", phone="123456789", email="test@test.com", address="Beijing"),
            "job_intention": "Software Engineer",
            "work_years": "3 years",
            "education_background": "Bachelor of Computer Science",
            "raw_text_summary": "Skilled in Python and React."
        }
        extracted_data = ResumeData(**dummy_data)
        message = "Success (Mock API)"
    else:
        try:
            if is_image_pdf or not raw_text.strip():
                # Image-based PDF: use vision AI
                print(f"Detected image-based PDF, using vision AI extraction...")
                page_images = PDFService.pdf_pages_to_base64_images(file_bytes, dpi=200)
                if not page_images:
                    raise HTTPException(status_code=400, detail="Failed to convert PDF pages to images.")
                extracted_data = AIService.extract_resume_info_from_images(page_images, api_key)
                message = "Success (Vision AI)"
            else:
                # Text-based PDF: use text AI
                extracted_data = AIService.extract_resume_info(raw_text, api_key)
                message = "Success"
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")

    # Cache the result
    try:
        redis_service.cache_resume_data(resume_id, extracted_data.model_dump())
    except:
        pass
        
    return ResumeAnalyzeResponse(
        resume_id=resume_id,
        data=extracted_data,
        message=message
    )

@router.post("/match", response_model=ResumeMatchResponse)
async def match_job(request: JobDescriptionRequest):
    job_desc = request.job_description.strip()
    resume_id = request.resume_id
    
    if not job_desc:
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
        
    job_hash = hashlib.md5(job_desc.encode('utf-8')).hexdigest()

    # Try cache
    try:
        cached_result = redis_service.get_match_result(resume_id, job_hash)
        if cached_result:
            return ResumeMatchResponse(
                resume_id=resume_id,
                match_result=MatchResult(**cached_result),
                message="Success (Cache Hit)"
            )
        
        # Retrieve resume data to match
        resume_data = redis_service.get_resume_data(resume_id)
        if not resume_data:
            raise HTTPException(status_code=404, detail="Resume data not found in cache. Please re-upload.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed cache operations: {e}")
        raise HTTPException(status_code=404, detail="Unable to retrieve resume info (cache unavailable).")
    
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        # Dummy Match
        match_res = MatchResult(
            score=85,
            skills_match_rate="85%",
            experience_relevance="Highly relevant",
            comment="This candidate fits well."
        )
        message = "Success (Mock Match)"
    else:
        try:
            match_res = AIService.score_resume(resume_data, job_desc, api_key)
            message = "Success"
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"AI matching failed: {str(e)}")
             
    # Cache result
    try:
        redis_service.cache_match_result(resume_id, job_hash, match_res.model_dump())
    except:
        pass
        
    return ResumeMatchResponse(
        resume_id=resume_id,
        match_result=match_res,
        message=message
    )
