from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from deep_translator import GoogleTranslator
from nltk.corpus import wordnet
import string


def get_word_type(word):
    synsets = wordnet.synsets(word)
    if not synsets:
        return "unknown"

    words_index = {"noun": 0, "verb": 0, "adjective": 0, "adverb": 0}
    
    for syn in synsets:
        word = syn.pos()
        if word == "n":
            words_index["noun"] += 1
        elif word == "v":
            words_index["verb"] += 1
        elif word in ["a", "s"]:
            words_index["adjective"] += 1
        elif word == "r":
            words_index["adverb"] += 1


    return max(words_index, key=words_index.get)

def predict_word_type(prev_type, next_type):

    if prev_type is None and next_type is None:
        return "unknown"
    
    # Sentence structure attempt
    if prev_type is None:

        if next_type == "noun":
            return "adjective"
        elif next_type == "verb":
            return "pronoun"
        else:
            return next_type 

    
    if next_type is None:

        if prev_type == "noun":
            return "adjective" 
         
        elif prev_type == "adjective":
            return "adjective"
        
        else:
            return prev_type  


    if prev_type == "noun" and next_type == "adjective":
        return "adjective"
    
    else:
        return prev_type
    
    return "unknown"


def fill_in_the_blank(driver):
    
    sentence = []
    blank_word_index = None

    # Get main body
    container = driver.find_element(By.XPATH, "//div[@dir='ltr']")

    # Get elements in container
    elements = container.find_elements(By.XPATH, "./*")
    
    for elem in elements:
        class_attr = elem.get_attribute("class")
        
        if "_5HFLU" in class_attr and elem.get_attribute("lang") == "es":
            
            # Get question structure (hint tokens)
            hint_tokens = elem.find_elements(By.XPATH, ".//div[@data-test='hint-token']")
            
            if hint_tokens:
                word = hint_tokens[0].get_attribute("aria-label")
                
                # Check for punctuation cases
                if word and not all(ch in string.punctuation for ch in word):
                    sentence.append(word)
                    
            else:
                text = elem.text.strip()
                
                if text and not all(ch in string.punctuation for ch in text):
                    sentence.append(text)
        
        # Add blank section to required sentence
        elif "_3AISd" in class_attr:
            sentence.append("____")
            blank_word_index = len(sentence) - 1
            
    
    print("Sentence:", sentence)
    print("Blank word position:", blank_word_index)
    
 
    # Get possible answers
    answers_container = driver.find_element(By.XPATH, "//div[@aria-label='choice' and @role='radiogroup']")
    choice_elements = answers_container.find_elements(By.XPATH, ".//div[@data-test='challenge-choice']")
    
    answers = []
    for choice in choice_elements:
        try:
            answer_span = choice.find_element(By.XPATH, ".//span[@data-test='challenge-judge-text']")
            answer_text = answer_span.text.strip()
            if answer_text and not all(ch in string.punctuation for ch in answer_text):
                answers.append(answer_text)
        except Exception as e:
            print("Error extracting answer:", e)
    
    print("Answers:", answers)
    
    
    # Check possible answer for grammar mistakes
    for possible_answer in answers:
        
        # Replace blank by formatted sentence
        possible_sentence_words = [possible_answer if item == '____' else item for item in sentence]
        print("Sentence being checked:", possible_sentence_words)
        possible_sentence = " ".join(possible_sentence_words)

        # Translate sentence into english to check
        possible_translated_sentence = GoogleTranslator(source='es', target='en').translate(possible_sentence)
        print("Translated Sentence:", possible_translated_sentence)
        

        return print(possible_translated_sentence)
        
        
        
    

    



    
    
   
    
    