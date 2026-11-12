import PyPDF2
import io
import os
from tempfile import NamedTemporaryFile

class PDFProcessor:
    """Process PDF files to extract text content."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        pass
    
    def extract_text_from_pdf(self, pdf_file):
        """
        Extract text from a PDF file.
        
        Args:
            pdf_file: A file-like object containing the PDF data
            
        Returns:
            str: The extracted text content
        """
        try:
            # Create a temporary file to save the PDF content
            with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_file.read())
                temp_path = temp_file.name
            
            # Extract text from the PDF
            text = ""
            with open(temp_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            # Basic text cleaning
            text = text.strip()
            
            # If text is too short, it might be a scanned PDF without OCR
            if len(text) < 100:
                return "The PDF appears to contain little text. It might be a scanned document without OCR processing."
            
            return text
            
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
    
    def summarize_resume(self, text):
        """
        Summarize a resume from extracted text.
        
        Args:
            text: The extracted text from a resume PDF
            
        Returns:
            str: A summary of the resume content
        """
        # This would typically use an LLM to summarize the resume
        # For now, we'll just return a simple message with the text length
        return f"Resume text extracted ({len(text)} characters). Ready for analysis."
    
    def summarize_job_description(self, text):
        """
        Summarize a job description from extracted text.
        
        Args:
            text: The extracted text from a job description PDF
            
        Returns:
            str: A summary of the job description content
        """
        # This would typically use an LLM to summarize the job description
        # For now, we'll just return a simple message with the text length
        return f"Job description text extracted ({len(text)} characters). Ready for analysis."
    
    def detect_document_type(self, text):
        """
        Attempt to detect if the PDF is a resume or job description.
        
        Args:
            text: The extracted text from a PDF
            
        Returns:
            str: Either 'resume', 'job_description', or 'unknown'
        """
        text_lower = text.lower()
        
        # Resume indicators - expanded and more specific
        resume_keywords = [
            'resume', 'curriculum vitae', 'cv', 'professional experience',
            'education', 'skills', 'certifications', 'references',
            'work history', 'employment history', 'professional summary',
            'work experience', 'career objective', 'objective',
            'core competencies', 'technical skills', 'achievements',
            'accomplishments', 'career summary', 'profile',
            'contact information', 'email:', 'phone:', 'address:',
            'bachelor', 'master', 'degree', 'university', 'college',
            'gpa', 'graduated', 'certification'
        ]
        
        # Job description indicators
        job_keywords = [
            'job description', 'responsibilities', 'requirements', 'qualifications',
            'we are seeking', 'about the role', 'about the position',
            'job summary', 'position summary', 'duties', 'about the company',
            'essential functions', 'minimum requirements', 'preferred qualifications',
            'compensation', 'salary range', 'benefits package', 'equal opportunity',
            'how to apply', 'application deadline', 'reports to'
        ]
        
        # Personal information patterns that indicate a resume
        personal_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            r'\b\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|court|ct|circle|cir|boulevard|blvd)\b',  # Addresses
        ]
        
        # Count indicators
        resume_score = sum(1 for keyword in resume_keywords if keyword in text_lower)
        job_score = sum(1 for keyword in job_keywords if keyword in text_lower)
        
        # Check for personal information patterns (strong resume indicators)
        personal_info_found = 0
        for pattern in personal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                personal_info_found += 2  # Weight personal info heavily
        
        resume_score += personal_info_found
        
        # Look for specific resume structure indicators
        if re.search(r'\b(experience|employment)\s*:\s*\n', text_lower):
            resume_score += 2
        if re.search(r'\b(education)\s*:\s*\n', text_lower):
            resume_score += 2
        if re.search(r'\b(skills)\s*:\s*\n', text_lower):
            resume_score += 2
        
        # Look for job posting structure indicators
        if re.search(r'\b(position|role)\s+title\s*:', text_lower):
            job_score += 2
        if re.search(r'\b(company|organization)\s+overview', text_lower):
            job_score += 2
        if re.search(r'\b(apply\s+(?:now|today|online))', text_lower):
            job_score += 2
        
        print(f"Resume score: {resume_score}, Job score: {job_score}")  # Debug info
        
        # Decision logic with lower thresholds
        if resume_score > job_score and resume_score >= 3:
            return 'resume'
        elif job_score > resume_score and job_score >= 3:
            return 'job_description'
        elif resume_score > 0 or personal_info_found > 0:
            # If we found any resume indicators or personal info, lean toward resume
            return 'resume'
        else:
            return 'unknown'

# Import re module at the top level
import re