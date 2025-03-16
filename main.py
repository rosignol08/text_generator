import spacy
import os
import io
import random
import tkinter as tk
from tkinter import filedialog, messagebox

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
        nlp.max_length = 1500000
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
    maximum = NB_MOTS_MAXI
    prevs = corpus[random.randint(0, len(corpus) - 1)][:ordre]  #un vrai début de phrase
    print(start_token, end=" ")
    maximum -= 1
    
    while maximum > 0:
        current_state = tuple(prevs)
        if current_state in markov_chain:
            next_tokens = sorted(markov_chain[current_state].items(), key=lambda item: item[1], reverse=True)[:n_best]
            next_token = random.choice(next_tokens)[0]
            prevs.pop(0)
            prevs.append(next_token)
            
            if next_token in ponctuation:
                break
                
            print(next_token, end=" ")
            maximum -= 1
        else:
            break


corpus = []
#corpus.extend(doc_to_word_list("data/Corpus/2999-0.txt"))
#markov_chain = markov_chain_unigram(corpus)
markov_chaine = markov_chain(corpus, 3)
ponctuation = [".", "!", "?", "...", ":", ";", ")", "(", "]", "[", "{", "}", "«", "»", "“", "”", "‘", "’", "'", '"', "—", "-", "–", " ", "\n", "\t", "\r", "\f", "\v"]
NB_MOTS_MAXI = 100



def select_files():
    file_paths = filedialog.askopenfilenames(title="Select Text Files", filetypes=[("Text Files", "*.txt")])
    if file_paths:
        corpus.clear()
        for file_path in file_paths:
            corpus.extend(doc_to_word_list(file_path))
        messagebox.showinfo("Success", "Files loaded successfully!")
def generate_sentence():
    start_token = start_token_entry.get()
    if not start_token:
        messagebox.showerror("Error", "Please enter a start token.")
        return
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, start_token + " ")
    generate_alea(markov_chaine, 3, start_token, 2)
# Create the main window
root = tk.Tk()
root.title("Text Generator")
# Create and place widgets
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
# Run the application
root.mainloop()
