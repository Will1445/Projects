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

manual_synonyms = {
    "chica": {"nina"},
    "chico": {"nino"},
    "marido": {"esposo"},
    "marida": {"esposa"},
}


def find_closest_match(word, answers):
    closest_match = difflib.get_close_matches(word, answers, n=1, cutoff=0.5)
    return closest_match[0] if closest_match else None

def get_synonyms(word):
    synonyms = set()

    lower_word = word.lower()  # Convert word to lowercase
    if lower_word in manual_synonyms:
        synonyms.update(manual_synonyms[lower_word])  # Use lower_word to access the synonyms

    return synonyms

def write_this_in_spanish(driver):

    # Extract the English words
    spanish_words_elements = driver.find_elements(By.XPATH, "//div[@data-test='hint-token']")
    words = [word.get_attribute("aria-label") for word in spanish_words_elements]
    print("English Words:", words)

    # Join the English words (strings) into a sentence
    spanish_sentence = " ".join(words)
    print("English Sentence:", spanish_sentence)

    # Translate the entire sentence to Spanish
    translated_sentence = GoogleTranslator(source='en', target='es').translate(spanish_sentence)
    print("Translated Sentence:", translated_sentence)

    # Split back down into words
    translated_words = translated_sentence.split()
    print("Translated Words:", translated_words)
    
    # Check if words are available answers, if not find possible synonyms until an available word is found 
   
    answers_elements = driver.find_elements(By.XPATH, "//span[@data-test='challenge-tap-token-text']")
    answers = [word.text for word in answers_elements]
    print("Available Answers:", answers)
    
    for i, word in enumerate(translated_words):  
        lower_word = word.lower()
        
        # Convert the answers list to lowercase for comparison
        lower_answers = [ans.lower() for ans in answers]
        
        if lower_word in lower_answers:  
            print(f"'{word}' is available as an answer.")  
        else:  
            print(f"'{word}' not found, trying synonyms...")  
            synonyms = get_synonyms(word)  # Fetch synonyms  

            # Check if any synonym is in answers
            found_synonym = None  
            for syn in synonyms:  
                if syn.lower() in lower_answers:  
                    found_synonym = syn  
                    break  # Stop searching once a valid synonym is found  

            # If a synonym was found, replace the word in translated_words  
            if found_synonym:  
                print(f"Replacing '{word}' with synonym '{found_synonym}'")  
                translated_words[i] = found_synonym  
            else:  
                print(f"No synonyms of '{word}' found in answers. Trying most similar words")
                
                closest_match = find_closest_match(lower_word, lower_answers)
            
                if closest_match:
                    print(f"Found closest match '{closest_match}' for '{word}'.")
                    # Replace the word in translated_words with the closest match
                    translated_words[i] = closest_match
                else:
                    print(f"No close matches found for '{word}'.")

                


    # Ensure the page is focused by clicking the body element
    body = driver.find_element(By.TAG_NAME, 'body')
    body.click()

    # Find all answer elements (word tiles)
    answer_elements = driver.find_elements(By.XPATH, "//span[@data-test='challenge-tap-token-text']")
    answer_texts = [el.text for el in answer_elements]

    # Click on each correct answer in order
    for word in translated_words:
        for el, text in zip(answer_elements, answer_texts):
            if text.lower() == word.lower():  # Check if it's the correct answer
                el.click()  # Click the word tile
                time.sleep(0.2)  # Small delay to prevent issues
                break  # Move to the next word

    # Send Enter:
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.1)
    actions.send_keys(Keys.ENTER).perform()