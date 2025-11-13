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


# Load the model

def check_sentence_coherence(sentence):
    reference_sentences = [
        "This is a well-structured and grammatically correct sentence.",
        "I enjoy walking in the park during the evening.",
        "The cat sat on the mat and looked at the stars.",
        "She quickly ran to catch the last train home.",
        "He studied all night for his physics exam.",
        "The quick brown fox jumps over the lazy dog.",
        "I went to the supermarket to buy some bread and milk.",
        "A scientist studies the fundamental laws of nature."
    ]

    # Compute sentence embeddings
    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    reference_embeddings = model.encode(reference_sentences, convert_to_tensor=True)
    
    # Compute cosine similarity scores
    scores = util.pytorch_cos_sim(sentence_embedding, reference_embeddings)
    
    # Take the maximum similarity score instead of the mean
    return scores.max().item()

# Test the function again


def determine_word_type(word):
    """
    Determines the part of speech for a given word using WordNet.
    Returns one of: "noun", "verb", "adjective", "adverb", or "unknown".
    """
    synsets = wordnet.synsets(word)
    if not synsets:
        return "unknown"

    # Initialize counts for each pos type
    pos_counts = {"noun": 0, "verb": 0, "adjective": 0, "adverb": 0}
    
    for syn in synsets:
        pos = syn.pos()
        if pos == "n":
            pos_counts["noun"] += 1
        elif pos == "v":
            pos_counts["verb"] += 1
        elif pos in ["a", "s"]:
            pos_counts["adjective"] += 1
        elif pos == "r":
            pos_counts["adverb"] += 1

    # Return the part-of-speech with the highest count.
    return max(pos_counts, key=pos_counts.get)

def predict_missing_word_type(prev_type, next_type):
    
    """
    Predicts the missing word type given the part-of-speech of the word immediately
    before (prev_type) and after (next_type) the blank, considering Spanish grammar rules.
    
    Returns one of: "noun", "verb", "adjective", "adverb", or "unknown".
    """
    # Case where both neighbors are missing (shouldn't happen, but just in case)
    if prev_type is None and next_type is None:
        return "unknown"
    
    # Blank is at the start of the sentence
    if prev_type is None:
        # Rely solely on the next word's type.
        if next_type == "noun":
            return "adjective"
        elif next_type == "verb":
            return "pronoun"
        else:
            return next_type  # If it's an adjective, we might expect a noun.

    # Blank is at the end of the sentence
    if next_type is None:
        # Rely solely on the previous word's type.
        if prev_type == "noun":
            # e.g. "familia ____" might be missing a verb or adjective.
            return "adjective"  # It can also be an adjective, depending on context.
        elif prev_type == "adjective":
            # e.g. "gran ____" typically expects a noun.
            return "adjective"
        else:
            return prev_type  # If it's a verb, we might expect a noun.

    # Both neighbors exist; apply combined heuristics.
    if prev_type == "noun" and next_type == "adjective":
        # e.g., "familia ____ grande" typically needs an adverb ("muy").
        return "adjective"
    else:
        return prev_type
    
    # You can add additional rules here...
    
    # Default case if no rule applies.
    return "unknown"


def fill_in_the_blank(driver):
    
    ####### Get Question Sentence #######
    
    # Locate the container element that holds the full sentence
    container = driver.find_element(By.XPATH, "//div[@dir='ltr']")
    # Get all direct children of the container
    children = container.find_elements(By.XPATH, "./*")
    
    sentence = []
    blank_word_index = None
    
    for child in children:
        class_attr = child.get_attribute("class")
        
        # If it's a standard word element
        if "_5HFLU" in class_attr and child.get_attribute("lang") == "es":
            # Try to extract the full word from the hint-token div, if available
            hint_tokens = child.find_elements(By.XPATH, ".//div[@data-test='hint-token']")
            if hint_tokens:
                word = hint_tokens[0].get_attribute("aria-label")
                # Only append if the word isn't solely punctuation
                if word and not all(ch in string.punctuation for ch in word):
                    sentence.append(word)
            else:
                # Otherwise, use the visible text (in case it contains punctuation, etc.)
                text = child.text.strip()
                if text and not all(ch in string.punctuation for ch in text):
                    sentence.append(text)
        
        # If it is the blank element (identified by the class _3AISd)
        elif "_3AISd" in class_attr:
            sentence.append("____")
            blank_word_index = len(sentence) - 1
            
    
    print("Sentence:", sentence)
    print("Blank word position:", blank_word_index)
    
    ####### Get Answers #######
    
    answers_container = driver.find_element(By.XPATH, "//div[@aria-label='choice' and @role='radiogroup']")
    # Get all answer choice elements within the container
    choice_elements = answers_container.find_elements(By.XPATH, ".//div[@data-test='challenge-choice']")
    
    answers = []
    for choice in choice_elements:
        try:
            # Extract the answer text from the child span
            answer_span = choice.find_element(By.XPATH, ".//span[@data-test='challenge-judge-text']")
            answer_text = answer_span.text.strip()
            # Only append if the answer isn't solely punctuation
            if answer_text and not all(ch in string.punctuation for ch in answer_text):
                answers.append(answer_text)
        except Exception as e:
            print("Error extracting answer:", e)
    
    print("Answers:", answers)
    
    
    ####### Place possible answer into blank, translate, then test logic #######
    
    for possible_answer in answers:
        
        # Create possible sentence
        possible_sentence_words = [possible_answer if item == '____' else item for item in sentence]
        print("Sentence being checked:", possible_sentence_words)
    
        # String words together to make a sentence 
        possible_sentence = " ".join(possible_sentence_words)

        # Translate sentence 
        possible_translated_sentence = GoogleTranslator(source='es', target='en').translate(possible_sentence)
        print("Translated Sentence:", possible_translated_sentence)
        
        # Check grammar of possible sentence 
        print(check_sentence_coherence(possible_translated_sentence))
        
        
        
    

    



    
    
   
    
    