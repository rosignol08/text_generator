import spacy
import os
import io
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

def doc_to_word_list(path):
    '''
    paramètre : chemin vers un corpus
    returns : liste de liste 
        - liste de phrases
        - chaque phrase est une liste de tokens
    '''
    with open(path) as input_stream:
        input_stream = io.open(path, mode="r", encoding="utf-8")
        nlp = spacy.load("fr_core_news_sm")
        nlp.max_length = 15000000
        text = input_stream.read()
        doc = nlp(text)
        sentences = []
        for sent in doc.sents:
            tokens = [token.text for token in sent]
            sentences.append(tokens)
        return sentences

def compter_transitions_unigrammes(corpus):
    transitions = {}

    for phrase in corpus:
        prev = ""
        for token in phrase:
            if prev not in transitions:
                transitions[prev] = {}
            if token not in transitions[prev]:
                transitions[prev][token] = 0
            transitions[prev][token] += 1
            prev = token

    return transitions

def probabilify(comptes_transitions):
    '''
    paramètre : dictionnaire de transitions
    returns : dictionnaire à deux niveaux contenant pour chaque mot la probabilité d'apparition pour chaque mot suivant possible. 
    '''
    probabilites = {}
    for mot in comptes_transitions:
        probabilites[mot] = {}
        total = sum(comptes_transitions[mot].values())
        for suivant in comptes_transitions[mot]:
            probabilites[mot][suivant] = comptes_transitions[mot][suivant] / total
            
    return probabilites

def markov_chain_unigram(corpus):
    transitions = compter_transitions_unigrammes(corpus)
    return probabilify(transitions)


def generate_unigram(markov_chain, start_token):
    '''
    Paramètres : 
    - chaîne de Markov
    - token de départ
    Returns : void.
    Affiche la phrase générée.
    '''
    maximum = NB_MOTS_MAXI
    token = start_token
    while token not in ponctuation and maximum > 0:
        print(token, end=" ")
        maximum -= 1
        if token in markov_chain:
            token = max(markov_chain[token], key=markov_chain[token].get)
        else:
            break

def generate_unigram_alea(markov_chain, start_token, n_best=1):
    '''
    Paramètres : 
    - chaîne de Markov
    - token de départ
    - nombre de tokens dans lesquels choisir le token suivant
    
    Returns : void.
    Affiche la phrase générée.
    '''
    markov_chain #chain de markov
    start_token #token de départ
    n_best #nombre de tokens dans lesquels choisir le token suivant
    maximum = NB_MOTS_MAXI
    token = start_token
    while token not in ponctuation and maximum > 0:
        print(token, end=" ")
        maximum -= 1
        if token in markov_chain:
            next_tokens = sorted(markov_chain[token].items(), key=lambda item: item[1], reverse=True)[:n_best]
            token = random.choice(next_tokens)[0]
        else:
            break

def compter_transitions_bigrammes(corpus):
    transitions = {}
    for phrase in corpus:
        prev = ""
        for token in phrase:
            if prev not in transitions:
                transitions[prev] = {}
            if token not in transitions[prev]:
                transitions[prev][token] = 0
            transitions[prev][token] += 1
            prev = token
    return transitions

def chaine_markov_bigramme(corpus):
    transitions = compter_transitions_bigrammes(corpus)
    return probabilify(transitions)

def generate_bi(markov_chain, start_token, n_best=1):
    maximum = NB_MOTS_MAXI
    token = start_token
    prevs = ["", ""]
    # compléter
    while token not in ponctuation and maximum > 0:
        print(token, end=" ")
        maximum -= 1
        if prevs[1] in markov_chain and prevs[0] in markov_chain[prevs[1]]:
            next_tokens = sorted(markov_chain[prevs[1]][prevs[0]].items(), key=lambda item: item[1], reverse=True)[:n_best]
            token = random.choice(next_tokens)[0]
            prevs[0] = prevs[1]
            prevs[1] = token
        else:
            break

def count_transitions(corpus, ordre):
    transitions = {}
    for phrase in corpus:
        prevs = [""] * ordre
        for token in phrase:
            current_state = tuple(prevs)
            if current_state not in transitions:
                transitions[current_state] = {}
            if token not in transitions[current_state]:
                transitions[current_state][token] = 0
            transitions[current_state][token] += 1
            prevs.pop(0)
            prevs.append(token)
    return transitions

def markov_chain(corpus, ordre):
    transitions = count_transitions(corpus, ordre)
    return probabilify(transitions)

def generate(markov_chain, start_tokens, ordre, n_best=1):
    maximum = NB_MOTS_MAXI
    prevs = start_tokens[-ordre:]
    while prevs[-1] not in ponctuation and maximum > 0:
        print(prevs[-1], end=" ")
        maximum -= 1
        current_state = tuple(prevs)
        if current_state in markov_chain:
            next_tokens = sorted(markov_chain[current_state].items(), key=lambda item: item[1], reverse=True)[:n_best]
            next_token = random.choice(next_tokens)[0]
            prevs.pop(0)
            prevs.append(next_token)
        else:
            break
def generate_alea(markov_chain, ordre, start_token, n_best=1):
    phrase = []
    maximum = NB_MOTS_MAXI
    prevs = [""] * ordre
    prevs[-1] = start_token
    min_length = 10
    phrase.append(start_token)
    
    while maximum > 0:
        current_state = tuple(prevs)
        
        # Check if we have this context in our model
        if current_state in markov_chain:
            # Instead of just taking n_best tokens, take more possibilities
            # Get all possible next tokens with their probabilities
            candidates = list(markov_chain[current_state].items())
            
            # If we have enough candidates, sample more broadly
            if len(candidates) > n_best * 2:
                # Take a wider selection to increase randomness
                n_consider = min(len(candidates), n_best * 3)
                # Randomly select from more options
                candidates = random.sample(candidates, n_consider)
            
            if candidates:
                # Use weighted random choice based on probabilities
                total = sum(prob for _, prob in candidates)
                r = random.random() * total
                cumulative = 0
                for token, prob in candidates:
                    cumulative += prob
                    if cumulative >= r:
                        next_token = token
                        break
                
                # Skip ending punctuation if phrase is too short
                if next_token in [".", "!", "?"] and len(phrase) < min_length:
                    continue
                
                prevs.pop(0)
                prevs.append(next_token)
                phrase.append(next_token)
                maximum -= 1
                
                if next_token in [".", "!", "?"] and len(phrase) >= min_length:
                    break
            else:
                break
        else:
            # Try backoff to shorter contexts
            found = False
            for backoff in range(ordre-1, 0, -1):
                shorter_context = tuple(prevs[-backoff:])
                if shorter_context in markov_chain:
                    candidates = list(markov_chain[shorter_context].items())
                    if candidates:
                        # Introduce more randomness in backoff
                        next_token = random.choice(candidates)[0]
                        prevs.pop(0)
                        prevs.append(next_token)
                        phrase.append(next_token)
                        maximum -= 1
                        found = True
                        break
            
            if not found:
                # Add some random ending if needed
                if len(phrase) < min_length:
                    # Add truly random words from our vocabulary
                    all_words = list(set(word for state in markov_chain.keys() 
                                    for word in markov_chain[state].keys() 
                                    if word not in ponctuation))
                    if all_words:
                        for _ in range(min(5, min_length - len(phrase))):
                            random_word = random.choice(all_words)
                            phrase.append(random_word)
                
                if phrase[-1] not in [".", "!", "?"]:
                    phrase.append(".")
                break
                
    return " ".join(phrase)

corpus = []
ponctuation = [".", "!", "?", "...", ":", ";", ")", "(", "]", "[", "{", "}", "«", "»", "“", "”", "‘", "’", "'", '"', "—", "-", "–", " ", "\n", "\t", "\r", "\f", "\v"]
NB_MOTS_MAXI = 500

def select_files():
    def load_files():
        file_paths = filedialog.askopenfilenames(title="Select Text Files", filetypes=[("Text Files", "*.txt")])
        if file_paths:
            corpus.clear()
            progress_bar['maximum'] = len(file_paths)
            for i, file_path in enumerate(file_paths):
                corpus.extend(doc_to_word_list(file_path))
                progress_bar['value'] = i + 1
                root.update_idletasks()
            messagebox.showinfo("Success", "Files loaded successfully!")
            progress_bar['value'] = 0

    threading.Thread(target=load_files).start()

def generate_sentence():
    def generate():
        if not corpus:
            messagebox.showerror("Error", "Please load text files first.")
            return
            
        markov_chaine = markov_chain(corpus, 4)
        start_token = start_token_entry.get().strip()
        if not start_token:
            messagebox.showerror("Error", "Please enter a start token.")
            return
        
        result_text.delete("1.0", tk.END)
        progress_bar['maximum'] = NB_MOTS_MAXI
        
        #gen la phrases
        sentence = generate_alea(markov_chaine, 5, start_token, n_best=3)
        
        #verif si la phrase se termine bien
        if not sentence.rstrip().endswith((".", "!", "?")):
            #cherche une fin bien
            last_words = sentence.split()[-min(4, len(sentence.split())):]
            for punct in [".", "!", "?"]:
                if tuple(last_words) + (punct,) in markov_chaine:
                    sentence += " " + punct
                    break
            else:
                #si on trouve pas de fin on met un point
                sentence += "."
        
        result_text.insert(tk.END, sentence)
        progress_bar['value'] = 0  #reset la barre de progression
        
    threading.Thread(target=generate).start()

root = tk.Tk()
root.title("Text Generator")

#widgets
select_button = tk.Button(root, text="Select Text Files", command=select_files)
select_button.pack(pady=10)
start_token_label = tk.Label(root, text="Start Token:")
start_token_label.pack(pady=5)
start_token_entry = tk.Entry(root)
start_token_entry.pack(pady=5)
generate_button = tk.Button(root, text="Generate Sentence", command=generate_sentence)
generate_button.pack(pady=10)
result_text = tk.Text(root, height=10, width=50)
result_text.pack(pady=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

#run
root.mainloop()
