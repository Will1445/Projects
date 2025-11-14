from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
    "ok": {"bien"},
    "elegante" : {"guapo"},
    "gente" : {"personas"}
}

def select_the_correct_meaning(driver):
    
    # Get english word
    english_word_elements = driver.find_elements(By.XPATH, "//div[contains(@class, '_20npu')]")
    words = [word.text for word in english_word_elements]

    if not words:
        print("No English word found.")
        return

    word = words[0]
    print("English Word:", word)

    # Translate to Spanish
    translated_word = GoogleTranslator(source='en', target='es').translate(word)
    print("Translated Word:", translated_word)

    # Get answers
    choices = driver.find_elements(By.XPATH, "//span[@data-test='challenge-judge-text']")
    word_choices = [choice.text for choice in choices]


    correct_index = None
    for index, choice_text in enumerate(word_choices):
        if choice_text.lower() == translated_word.lower():
            correct_index = index + 1
            break 
    
    # Synonym case
    if correct_index is None:
        print("No answer found, using synonyms") 
        lower_word = translated_word.lower() 

        if lower_word in manual_synonyms: 
            for synonym in manual_synonyms[lower_word]: 
                for index, choice_text in enumerate(word_choices):
                    if choice_text.lower() == synonym.lower():
                        correct_index = index + 1
                        break
                if correct_index:  
                    break

    print("Correct Answer:", correct_index)

    if correct_index:
        actions = ActionChains(driver)
        actions.send_keys(str(correct_index)).perform()
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(0.1)
        actions.send_keys(Keys.ENTER).perform()
    else:
        print("No correct answer found.")

