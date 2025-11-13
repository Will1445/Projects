from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from deep_translator import GoogleTranslator
from nltk.corpus import wordnet
import difflib
import re
import time
import string

from utils.Write_this_in_English import write_this_in_english
from utils.Write_this_in_Spanish import write_this_in_spanish
from utils.Select_the_correct_meaning import select_the_correct_meaning
from utils.Fill_in_the_blank import fill_in_the_blank

# Attach to running Chrome
chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"

service = Service("/opt/homebrew/bin/chromedriver") 
driver = webdriver.Chrome(service=service, options=chrome_options)

# Variable to store the last answered question
last_question = None

while True:
# Extract the question text
    question = driver.find_element(By.XPATH, "//h1[@data-test='challenge-header']").text
    print("Current Question:", question)

    if question == 'Write this in English':
        write_this_in_english(driver)
    elif question == 'Select the correct meaning':
        select_the_correct_meaning(driver) 
    elif question == 'Write this in Spanish':
        write_this_in_spanish(driver)
    else:
        print('Question not yet defined')


    time.sleep(0.5)  # Check for new questions every 0.5 seconds
