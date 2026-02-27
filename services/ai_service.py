import json
import dashscope
from typing import List
from dashscope import Generation
from models.resume import ResumeData, BasicInfo, MatchResult

class AIService:
    @staticmethod
    def _parse_json_result(text: str) -> dict:
        """
        Attempt to parse JSON from AI response, handling basic cleanup and common issues like markdown code blocks
        """
        # Remove common markdown starting/ending codes
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Failed to decode AI response as JSON: {text}")
            # Try finding the first '{' and last '}'
            start_index = text.find('{')
            end_index = text.rfind('}')
            if start_index != -1 and end_index != -1 and start_index < end_index:
                try:
                    return json.loads(text[start_index:end_index+1])
                except json.JSONDecodeError:
                    pass
            print("Failed to decode even after finding bounds.")
            return {}

    @staticmethod
    def _get_extraction_system_prompt() -> str:
        """Shared system prompt for resume extraction."""
        return '''你是一个专业的HR简历解析助手。请从给定的简历内容中提取以下关键信息，并严格按照下方的JSON格式返回，不要包含其他无关内容或说明文字。
{
    "basic_info": {
        "name": "姓名，若无返回null",
        "phone": "电话号码，若无返回null",
        "email": "邮件地址，若无返回null",
        "address": "籍贯或地址，若无返回null"
    },
    "job_intention": "求职意向/目标岗位，若无返回null",
    "work_years": "工作总年限字符串，如'5年'，若无返回null",
    "education_background": "最高学历描述，若无返回null",
    "raw_text_summary": "一段关于候选人核心技能的简要总结（100字以内）"
}
'''

    @staticmethod
    def _build_resume_data(parsed_dict: dict) -> ResumeData:
        """Build ResumeData from a parsed dict."""
        basic_info = parsed_dict.get("basic_info", {})
        return ResumeData(
            basic_info=BasicInfo(
                name=basic_info.get("name"),
                phone=basic_info.get("phone"),
                email=basic_info.get("email"),
                address=basic_info.get("address")
            ),
            job_intention=parsed_dict.get("job_intention"),
            work_years=parsed_dict.get("work_years"),
            education_background=parsed_dict.get("education_background"),
            raw_text_summary=parsed_dict.get("raw_text_summary")
        )
            
    @staticmethod
    def extract_resume_info(pdf_text: str, api_key: str) -> ResumeData:
        """
        Calls DashScope API to extract resume information from text into structured JSON.
        """
        if not api_key:
            raise Exception("DashScope API Key is not configured")
        
        dashscope.api_key = api_key
        
        sys_prompt = AIService._get_extraction_system_prompt()
        user_prompt = f"这是待解析的简历文本：\n{pdf_text[:3000]}"
        
        messages = [
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        response = Generation.call(
            model='qwen-turbo',
            messages=messages,
            result_format='message',
        )

        if response.status_code == 200:
            result_str = response.output.choices[0]['message']['content']
            parsed_dict = AIService._parse_json_result(result_str)
            return AIService._build_resume_data(parsed_dict)
        else:
            raise Exception(f"DashScope API failed with status {response.status_code}: {response.code} - {response.message}")

    @staticmethod
    def extract_resume_info_from_images(page_images_b64: List[str], api_key: str) -> ResumeData:
        """
        Calls DashScope multimodal vision API to extract resume info from PDF page images.
        Used for image-based/vector-drawn PDFs where text extraction fails.
        """
        if not api_key:
            raise Exception("DashScope API Key is not configured")
        
        dashscope.api_key = api_key
        
        sys_prompt = AIService._get_extraction_system_prompt()
        
        # Build multimodal content with images
        user_content = [{"text": "请仔细分析以下简历图片中的所有文字信息并提取关键信息："}]
        for img_b64 in page_images_b64[:4]:  # Limit to 4 pages
            user_content.append({
                "image": f"data:image/png;base64,{img_b64}"
            })

        messages = [
            {'role': 'system', 'content': [{"text": sys_prompt}]},
            {'role': 'user', 'content': user_content}
        ]
        
        from dashscope import MultiModalConversation
        response = MultiModalConversation.call(
            model='qwen-vl-max',
            messages=messages,
        )

        if response.status_code == 200:
            result_str = response.output.choices[0]['message']['content'][0]['text']
            print(f"Vision AI raw response: {result_str[:500]}")
            parsed_dict = AIService._parse_json_result(result_str)
            return AIService._build_resume_data(parsed_dict)
        else:
            raise Exception(f"DashScope Vision API failed with status {response.status_code}: {response.code} - {response.message}")

    @staticmethod
    def score_resume(resume_data: dict, job_description: str, api_key: str) -> MatchResult:
        """
        Calls DashScope to match the extracted resume data with the job description.
        """
        if not api_key:
            raise Exception("DashScope API Key is not configured")
        
        dashscope.api_key = api_key
        
        sys_prompt = '''你是一个资深的招聘专家。你需要评估一份已解析的简历提取数据与目标招聘岗位需求描述的匹配程度。
请分析后给出一个匹配度打分（0-100的整数），并给出各项的匹配评价，严格按照如下JSON格式返回：
{
    "score": 匹配度打分整数值,
    "skills_match_rate": "技能要求匹配度分析及百分比感觉",
    "experience_relevance": "经验与行业相关性分析",
    "comment": "综合短评（50字内）"
}
'''
        resume_str = json.dumps(resume_data, ensure_ascii=False)
        user_prompt = f"岗位需求：\n{job_description[:1000]}\n\n简历摘要数据：\n{resume_str}"
        
        messages = [
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        response = Generation.call(
            model='qwen-turbo',
            messages=messages,
            result_format='message',
        )
        
        if response.status_code == 200:
            result_str = response.output.choices[0]['message']['content']
            parsed_dict = AIService._parse_json_result(result_str)
            
            return MatchResult(
                score=parsed_dict.get('score', 0),
                skills_match_rate=parsed_dict.get('skills_match_rate', "N/A"),
                experience_relevance=parsed_dict.get('experience_relevance', 'N/A'),
                comment=parsed_dict.get('comment', '解析失败或模型未给出标准格式')
            )
        else:
            raise Exception(f"DashScope API failed during match with status {response.status_code}: {response.code}")
