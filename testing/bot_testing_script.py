#!/usr/bin/env python3
"""
Comprehensive testing script for the Career Bot
Tests memory, intent classification, and response quality
"""

import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI

# Add the current directory to path so we can import our modules
sys.path.append('.')

from gpt_service import GPTService
from response_handlers import ResponseHandlers
from user_intent import IntentClassifier
from memory_manager import MemoryManager

class BotTester:
    def __init__(self):
        """Initialize the bot tester with all services."""
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        # Initialize services
        client = OpenAI(api_key=api_key)
        self.gpt_service = GPTService(client)
        self.response_handlers = ResponseHandlers()
        self.intent_classifier = IntentClassifier(client)
        self.memory_manager = MemoryManager(k=15)
        
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
    
    def simulate_user_input(self, user_input, expected_keywords=None, should_contain=None, should_not_contain=None):
        """Simulate a user input and test the response."""
        print(f"\n{'='*60}")
        print(f"USER INPUT: {user_input}")
        print(f"{'='*60}")
        
        try:
            # Classify intent
            intent_info = self.intent_classifier.classify_intent(user_input, self.memory_manager.get_user_info())
            print(f"CLASSIFIED INTENT: {intent_info['intent']}")
            if 'args' in intent_info:
                print(f"INTENT ARGS: {intent_info['args']}")
            
            # Handle intent and get response
            response = self._handle_intent(intent_info, user_input)
            
            # Add to memory
            if response:
                self.memory_manager.add_message(user_input, response)
            
            print(f"\nBOT RESPONSE: {response}")
            
            # Test response quality
            self._test_response_quality(user_input, response, expected_keywords, should_contain, should_not_contain)
            
            return response
            
        except Exception as e:
            print(f"ERROR: {e}")
            self._record_test_result(user_input, False, f"Exception occurred: {e}")
            return None
    
    def _handle_intent(self, intent_info, original_input):
        """Handle the classified intent and return response."""
        intent = intent_info['intent']
        args = intent_info.get('args', {})
        
        if intent == 'handle_greeting':
            return self.response_handlers.handle_greeting(args['greeting'], self.memory_manager.get_user_info())
            
        elif intent == 'handle_goodbye':
            return self.response_handlers.handle_goodbye(args['farewell'], self.memory_manager.get_user_info())
            
        elif intent == 'process_job_url':
            return self.gpt_service.generate_resume_sections(
                args['url'], 
                self.memory_manager.get_user_info(),
                self.memory_manager.get_chat_history()
            )
            
        elif intent == 'process_job_description':
            return self.gpt_service.process_job_description(
                args['job_description'], 
                self.memory_manager.get_user_info(),
                self.memory_manager.get_chat_history()
            )
            
        elif intent == 'answer_career_question':
            return self.gpt_service.chat_about_resumes(
                args['question'], 
                self.memory_manager.get_user_info(), 
                self.memory_manager.get_chat_history()
            )
            
        elif intent == 'store_personal_info':
            info_type = args['info_type']
            info_value = args['info_value']
            self.memory_manager.store_user_info(info_type, info_value)
            
            # Create specific confirmation messages
            if info_type == 'experience':
                return f"Got it! I've noted that you have {info_value}. This will be helpful for tailoring your data science resume."
            elif info_type == 'current_role':
                return f"Perfect! I've noted that you work as {info_value}. Your background will be valuable for data science roles."
            elif info_type == 'name':
                return f"Nice to meet you, {info_value}! How can I help with your career today?"
            elif info_type == 'career_interest':
                return f"Excellent! I've noted your interest in {info_value}. I'm here to help you with your job search in this field."
            else:
                return f"Thanks for sharing that information! I've noted your {info_type}: {info_value}."
                
        elif intent == 'handle_off_topic':
            return "I'm specialized in helping with resumes, job applications, and career advice. How can I assist you with your career today?"
            
        else:
            return "I'm not sure I understood that. Could you please rephrase your question about careers or resumes?"
    
    def _test_response_quality(self, user_input, response, expected_keywords, should_contain, should_not_contain):
        """Test the quality of the response."""
        test_passed = True
        issues = []
        
        if not response:
            test_passed = False
            issues.append("No response generated")
        
        if expected_keywords:
            for keyword in expected_keywords:
                if keyword.lower() not in response.lower():
                    test_passed = False
                    issues.append(f"Missing expected keyword: '{keyword}'")
        
        if should_contain:
            for phrase in should_contain:
                if phrase.lower() not in response.lower():
                    test_passed = False
                    issues.append(f"Missing required phrase: '{phrase}'")
        
        if should_not_contain:
            for phrase in should_not_contain:
                if phrase.lower() in response.lower():
                    test_passed = False
                    issues.append(f"Contains forbidden phrase: '{phrase}'")
        
        self._record_test_result(user_input, test_passed, issues)
    
    def _record_test_result(self, user_input, passed, issues):
        """Record test result."""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print("✅ TEST PASSED")
        else:
            print("❌ TEST FAILED")
            if issues:
                for issue in issues:
                    print(f"   - {issue}")
        
        self.test_results.append({
            'input': user_input,
            'passed': passed,
            'issues': issues
        })
    
    def check_memory(self, key, expected_value):
        """Check if memory contains expected value."""
        print(f"\n📋 MEMORY CHECK: {key} = {expected_value}")
        user_info = self.memory_manager.get_user_info()
        
        if key in user_info and user_info[key] == expected_value:
            print("✅ MEMORY CHECK PASSED")
            self.passed_tests += 1
        else:
            print(f"❌ MEMORY CHECK FAILED")
            print(f"   Expected: {expected_value}")
            print(f"   Actual: {user_info.get(key, 'NOT FOUND')}")
        
        self.total_tests += 1
        print(f"Current memory: {user_info}")
    
    def run_comprehensive_test(self):
        """Run a comprehensive test suite."""
        print("🤖 STARTING COMPREHENSIVE BOT TEST")
        print("="*60)
        
        # Test 1: Initial greeting and name storage
        self.simulate_user_input(
            "hello my name is Gavriel Kirichenko",
            expected_keywords=["Gavriel"],
            should_not_contain=["I'm here to assist you, Gavriel! If you have specific"]
        )
        self.check_memory("name", "Gavriel Kirichenko")
        
        # Test 2: Career interest storage
        self.simulate_user_input(
            "i want to create a resume for data science positions",
            expected_keywords=["data science"],
            should_contain=["noted", "interest"]
        )
        self.check_memory("career_interest", "data science positions")
        
        # Test 3: Experience storage
        self.simulate_user_input(
            "i have 3 years of experience in machine learning",
            should_contain=["noted", "3 years"],
            should_not_contain=["I'm here to assist you, Gavriel! If you have specific"]
        )
        self.check_memory("experience", "3 years of experience in machine learning")
        
        # Test 4: Current role storage
        self.simulate_user_input(
            "i work as a software engineer",
            should_contain=["noted", "software engineer"],
            should_not_contain=["I'm here to assist you, Gavriel! If you have specific"]
        )
        self.check_memory("current_role", "software engineer")
        
        # Test 5: Name recall
        self.simulate_user_input(
            "what is my name?",
            should_contain=["Gavriel Kirichenko"],
            should_not_contain=["user"]
        )
        
        # Test 6: Career interest recall
        self.simulate_user_input(
            "what job am i looking for?",
            should_contain=["data science"],
            expected_keywords=["Gavriel"]
        )
        
        # Test 7: Personalized objective
        self.simulate_user_input(
            "can you write me an objective section for my resume?",
            expected_keywords=["Gavriel", "software engineer", "machine learning", "data science"],
            should_contain=["objective"]
        )
        
        # Test 8: Memory persistence check
        self.simulate_user_input(
            "who am i and what do i do?",
            expected_keywords=["Gavriel Kirichenko", "software engineer", "data science", "machine learning"]
        )
        
        # Test 9: Greeting with stored name
        self.simulate_user_input(
            "hi there",
            expected_keywords=["Gavriel"],
            should_not_contain=["user"]
        )
        
        # Test 10: Off-topic redirect
        self.simulate_user_input(
            "what's the weather like?",
            should_contain=["specialized", "resumes", "career"]
        )
        
        # Test 11: Complex career question
        self.simulate_user_input(
            "how should i highlight my machine learning experience for data science roles?",
            expected_keywords=["machine learning", "data science"]
        )
        
        self._print_test_summary()
    
    def _print_test_summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print("🎯 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Passed: {self.passed_tests}/{self.total_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        failed_tests = [test for test in self.test_results if not test['passed']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - Input: {test['input']}")
                for issue in test['issues']:
                    print(f"     * {issue}")
        else:
            print("\n🎉 ALL TESTS PASSED!")

def main():
    """Main function to run tests."""
    try:
        tester = BotTester()
        tester.run_comprehensive_test()
    except Exception as e:
        print(f"Failed to initialize tester: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())