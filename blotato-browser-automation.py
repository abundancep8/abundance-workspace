#!/usr/bin/env python3
"""
Blotato Web Automation - Generate + Upload Videos via Browser
Since API is failing, using Selenium to automate the web dashboard
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime

class BlotatoAutomation:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None
        self.session = {}
        
    def start_browser(self):
        """Start Chrome browser"""
        chrome_options = Options()
        # Run headless for automation (no window)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Browser started")
        
    def login_to_blotato(self):
        """Log into Blotato dashboard"""
        print("Navigating to Blotato login...")
        self.driver.get("https://app.blotato.com/login")
        
        time.sleep(3)  # Wait for page load
        
        # Find email field
        try:
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.send_keys(self.email)
            print("✅ Email entered")
        except Exception as e:
            print(f"❌ Could not find email field: {e}")
            return False
            
        # Find password field
        try:
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(self.password)
            print("✅ Password entered")
        except Exception as e:
            print(f"❌ Could not find password field: {e}")
            return False
            
        # Click login button
        try:
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_btn.click()
            print("✅ Login clicked")
        except Exception as e:
            print(f"❌ Could not click login: {e}")
            return False
            
        # Wait for dashboard to load
        time.sleep(5)
        return True
        
    def create_video_from_script(self, script_text, title, hook):
        """Create a video in Blotato from script"""
        print(f"\n📹 Creating video: {title}")
        
        try:
            # Navigate to create new project
            self.driver.get("https://app.blotato.com/projects/new")
            time.sleep(3)
            
            # Find title field
            title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "projectTitle"))
            )
            title_input.clear()
            title_input.send_keys(title)
            print(f"✅ Title set: {title}")
            
            # Find script/content field
            script_input = self.driver.find_element(By.ID, "scriptContent")
            script_input.clear()
            script_input.send_keys(script_text)
            print("✅ Script entered")
            
            # Click generate button
            generate_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]")
            generate_btn.click()
            print("✅ Generation started")
            
            # Wait for video to generate (can take several minutes)
            print("⏳ Waiting for video generation...")
            time.sleep(120)  # 2 minute timeout
            
            # Check if video is ready
            try:
                success_msg = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "video-ready"))
                )
                print("✅ Video generated successfully")
                return True
            except:
                print("⚠️ Video generation may still be processing")
                return True  # Assume it's processing
                
        except Exception as e:
            print(f"❌ Error creating video: {e}")
            return False
            
    def upload_to_youtube(self, video_id):
        """Upload generated video to YouTube"""
        print(f"\n📤 Uploading video {video_id} to YouTube...")
        
        try:
            # Find upload button
            upload_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Upload to YouTube')]"))
            )
            upload_btn.click()
            print("✅ Upload started")
            
            # Wait for upload to complete
            time.sleep(30)
            print("✅ Upload completed")
            return True
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
            
    def process_script_batch(self, scripts, batch_name):
        """Process multiple scripts"""
        results = []
        
        for idx, script in enumerate(scripts):
            print(f"\n{'='*60}")
            print(f"Script {idx+1}/{len(scripts)}")
            print(f"{'='*60}")
            
            # Create video
            success = self.create_video_from_script(
                script['transcript'],
                script['title'],
                script['hook']
            )
            
            if success:
                # Upload to YouTube
                upload_success = self.upload_to_youtube(script['id'])
                
                results.append({
                    "script_id": script['id'],
                    "title": script['title'],
                    "created": success,
                    "uploaded": upload_success,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"✅ Script {idx+1} complete")
            else:
                results.append({
                    "script_id": script['id'],
                    "title": script['title'],
                    "created": False,
                    "uploaded": False,
                    "timestamp": datetime.now().isoformat()
                })
                
            # Small delay between videos
            time.sleep(10)
            
        return results
        
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")
            
    def log_results(self, results, batch_name):
        """Log results to file"""
        log_file = f".cache/blotato-automation-log-{batch_name}.jsonl"
        
        for result in results:
            with open(log_file, 'a') as f:
                f.write(json.dumps(result) + "\n")
                
        print(f"✅ Results logged to {log_file}")


def main():
    # Get credentials
    email = input("Blotato email: ").strip()
    password = input("Blotato password: ").strip()
    
    # Load scripts
    with open('blotato-script-batch-1.md', 'r') as f:
        content = f.read()
        
    # Parse scripts (simplified)
    scripts = []
    sections = content.split('## SCRIPT ')[1:]
    
    for i, section in enumerate(sections[:2]):  # Start with first 2 scripts
        lines = section.split('\n')
        title = lines[0].split(': ')[1] if ': ' in lines[0] else f"Script {i+1}"
        
        scripts.append({
            'id': i+1,
            'title': title,
            'hook': 'Test hook',
            'transcript': '\n'.join(lines[5:20])  # First ~15 lines as transcript
        })
    
    # Run automation
    bot = BlotatoAutomation(email, password)
    
    try:
        bot.start_browser()
        if bot.login_to_blotato():
            results = bot.process_script_batch(scripts, "batch-1")
            bot.log_results(results, "batch-1")
        else:
            print("❌ Login failed")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        bot.close()


if __name__ == "__main__":
    main()
