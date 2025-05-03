#!/usr/bin/env python3
"""
Accurate Instagram Username Checker
----------------------------------
This script checks if a given Instagram username exists by using
a more reliable method to distinguish between non-existent users
and private accounts.
"""

import urllib.request
import urllib.error
import ssl
import sys
import time
import re
import json

def check_username(username):
    """
    Check if an Instagram username exists by making a request to Instagram's GraphQL API.
    
    Args:
        username (str): The Instagram username to check
        
    Returns:
        bool: True if username exists, False if available, None if error
    """
    # Clean the username (remove @ if present)
    username = username.strip().lstrip('@')
    
    # We'll use Instagram's web API directly rather than parsing the HTML
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    # Set headers to mimic a browser, including the x-ig-app-id which is needed for the API
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Accept': 'text/html,application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-IG-App-ID': '936619743392459',  # This is important for the API request
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # Create an SSL context that doesn't verify certificates
        context = ssl._create_unverified_context()
        
        # Create a request object with headers
        req = urllib.request.Request(url, headers=headers)
        
        # Make the request with our custom SSL context
        response = urllib.request.urlopen(req, context=context)
        
        # Read the response content
        content = response.read().decode('utf-8')
        
        # Try to parse the JSON response
        data = json.loads(content)
        
        # If we got a valid response with user data, the username exists
        if 'data' in data and 'user' in data['data'] and data['data']['user'] is not None:
            return True
        
        # If the user field is null but we got a 200 response, the username doesn't exist
        return False
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # 404 definitely means username doesn't exist
            return False
        else:
            # Try a fallback method with direct page access
            return _check_username_fallback(username)
    
    except Exception as e:
        print(f"Error with API method: {e}")
        # Try fallback method if the API fails
        return _check_username_fallback(username)

def _check_username_fallback(username):
    """Fallback method using page content analysis"""
    try:
        # Instagram URL for the user's page
        url = f"https://www.instagram.com/{username}/"
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # Create an SSL context that doesn't verify certificates
        context = ssl._create_unverified_context()
        
        # Create a request object with headers
        req = urllib.request.Request(url, headers=headers)
        
        # Make the request with our custom SSL context
        response = urllib.request.urlopen(req, context=context)
        
        # Read the response content
        html_content = response.read().decode('utf-8')
        
        # Look for a meta tag with the username in it (strong indicator of a real profile)
        username_meta_pattern = re.compile(f'<meta property="og:title" content="(.+?)(@{username}|{username})')
        if username_meta_pattern.search(html_content):
            return True
            
        # Look for specific JSON data in the page that indicates a user profile
        if f'"username":"{username}"' in html_content or f'username\\": \\"{username}\\"' in html_content:
            return True
            
        # If we see these page not found indicators, the username is available
        not_found_indicators = [
            "Sorry, this page isn't available",
            "The link you followed may be broken",
            "Page Not Found"
        ]
        
        for indicator in not_found_indicators:
            if indicator in html_content:
                return False
                
        # Default: If we got this far without a clear signal, assume the username exists
        # (Instagram tends to restrict access rather than show non-existent pages)
        return True
            
    except Exception as e:
        print(f"Error in fallback method: {e}")
        return None

def main():
    """Main function to handle command-line arguments and check usernames."""
    
    print("Instagram Username Checker (Advanced)")
    print("-----------------------------------")
    
    if len(sys.argv) > 1:
        # Username provided as command line argument
        username = sys.argv[1]
        print(f"Checking @{username}...")
        result = check_username(username)
        
        if result is True:
            print(f"✖ @{username} already exists")
        elif result is False:
            print(f"✓ @{username} is available!")
        else:
            print(f"? Could not determine if @{username} exists")
    
    else:
        # Interactive mode
        print("Enter usernames to check, or 'q' to quit")
        
        while True:
            username = input("\nEnter Instagram username to check (or 'q' to quit): ")
            if username.lower() == 'q':
                break
                
            if not username.strip():
                continue
                
            print(f"Checking @{username}...")
            result = check_username(username)
            
            if result is True:
                print(f"✖ @{username} already exists")
            elif result is False:
                print(f"✓ @{username} is available!")
            else:
                print(f"? Could not determine if @{username} exists")
            
            # Add a delay to avoid rate limiting
            time.sleep(1)

if __name__ == "__main__":
    main()