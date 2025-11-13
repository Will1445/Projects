from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from deep_translator import GoogleTranslator
from nltk.corpus import wordnet
import time

manual_synonyms = {
    "i": {"yo"},
    "su": {"tu"},
    "chica": {"nina"},
    "chico": {"nino"},
    "marido": {"esposo"},
    "marida": {"esposa"},
    "ok": {"bien"}
}

def select_the_correct_meaning(driver):
    
    # Pull out English word
    english_word_elements = driver.find_elements(By.XPATH, "//div[contains(@class, '_20npu')]")
    words = [word.text for word in english_word_elements]

    if not words:  # Handle case where no word is found
        print("No English word found.")
        return

    word = words[0]  # Extract the first word as a string
    print("English Word:", word)

    # Translate the word to Spanish
    translated_word = GoogleTranslator(source='en', target='es').translate(word)
    print("Translated Word:", translated_word)

    # Find all answer choices
    choices = driver.find_elements(By.XPATH, "//span[@data-test='challenge-judge-text']")
    word_choices = [choice.text for choice in choices]

    # Initialize correct_index
    correct_index = None

    for index, choice_text in enumerate(word_choices):
        if choice_text.lower() == translated_word.lower():
            correct_index = index + 1
            break  # Stop once the correct index is found

    # If translation is not found, check manual synonyms
    if correct_index is None:
        print("No answer found, using synonyms")
        lower_word = translated_word.lower()  # Convert word to lowercase

        if lower_word in manual_synonyms:
            for synonym in manual_synonyms[lower_word]:  # Check all synonyms
                for index, choice_text in enumerate(word_choices):
                    if choice_text.lower() == synonym.lower():
                        correct_index = index + 1
                        break
                if correct_index:  
                    break  # Stop searching once we find a match

    print("Correct Answer:", correct_index)

    if correct_index:
        actions = ActionChains(driver)
        actions.send_keys(str(correct_index)).perform()
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(0.1)
        actions.send_keys(Keys.ENTER).perform()
    else:
        print("No correct answer found.")

