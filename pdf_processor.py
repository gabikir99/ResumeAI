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
        
        # Resume indicators
        resume_keywords = [
            'resume', 'curriculum vitae', 'cv', 'professional experience',
            'education', 'skills', 'certifications', 'references',
            'work history', 'employment history', 'professional summary'
        ]
        
        # Job description indicators
        job_keywords = [
            'job description', 'responsibilities', 'requirements', 'qualifications',
            'we are seeking', 'about the role', 'about the position',
            'job summary', 'position summary', 'duties', 'about the company'
        ]
        
        resume_score = sum(1 for keyword in resume_keywords if keyword in text_lower)
        job_score = sum(1 for keyword in job_keywords if keyword in text_lower)
        
        if resume_score > job_score and resume_score > 2:
            return 'resume'
        elif job_score > resume_score and job_score > 2:
            return 'job_description'
        else:
            return 'unknown'
