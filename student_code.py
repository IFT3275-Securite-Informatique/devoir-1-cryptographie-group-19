import math
import random as rnd
import numpy as np
import requests
from collections import Counter

# IFT3275 Devoir 1 Question 2
# Auteurs : Syrine Cherni (20251962) et Andy Le (20218631)
# Date : 2024-11-10

def decrypt(C):
    # Charger un corpus de textes en français
    urls = [
        "https://www.gutenberg.org/ebooks/13846.txt.utf-8",
        "https://www.gutenberg.org/ebooks/4650.txt.utf-8"
    ]
    corpus = load_text_from_web(urls)

    # Calculer les fréquences des lettres et des bisymboles
    french_letter_freq, french_bisymboles_freq = calculate_frequencies(corpus)

    # Ajuster les fréquences des lettres avec celles des bisymboles
    adjusted_letter_freq = adjust_frequencies_with_bisymboles(french_letter_freq, french_bisymboles_freq)

    # Trier les fréquences pour le déchiffrement
    sorted_letter_freq = [item[0] for item in Counter(adjusted_letter_freq).most_common()]
    sorted_bisymboles_freq = [item[0] for item in Counter(french_bisymboles_freq).most_common()]

    # Segmenter le texte chiffré
    ciphertext_segments = split_ciphertext_into_segments(ciphertext)

    # Déchiffrer en utilisant des mappages probables
    best_plaintext = ""
    best_ioc = 0
    best_mapping = {}

    for _ in range(10):  # Nombre d'itérations pour améliorer les résultats
        single_mapping = {}
        pair_mapping = {}

        # Mapper les segments les plus fréquents avec les lettres et bisymboles
        for segment, _ in Counter(ciphertext_segments).most_common():
            if sorted_letter_freq:
                single_mapping[segment] = sorted_letter_freq.pop(0)
            elif sorted_bisymboles_freq:
                pair_mapping[segment] = sorted_bisymboles_freq.pop(0)
            else:
                break

        # Appliquer le déchiffrement et calculer l'indice de coïncidence
        decrypted_text = decrypt_segments(ciphertext_segments, single_mapping, pair_mapping)
        ioc = calculate_index_of_coincidence(decrypted_text)

        if abs(ioc - 0.077) < abs(best_ioc - 0.077):  # Comparer avec l'IoC attendu pour le français
            M = decrypted_text
    return M
# Charger plusieurs textes français pour un corpus plus complet
def load_text_from_web(urls):
    corpus = ""
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            corpus += response.text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du chargement du texte : {e}")
    return corpus

# Découper le texte en bisymboles pour un ensemble de 256 symboles
def cut_string_into_pairs(text):
    pairs = []
    for i in range(0, len(text) - 1, 2):
        pairs.append(text[i:i + 2])
    if len(text) % 2 != 0:
        pairs.append(text[-1] + '_')
    return pairs

# Générer les symboles et calculer les fréquences
def calculate_symbol_frequencies(text):
    caracteres = list(set(text))
    nb_bisymboles = 256 - len(caracteres)
    bisymboles = [item for item, _ in Counter(cut_string_into_pairs(text)).most_common(nb_bisymboles)]
    symboles = caracteres + bisymboles
    return symboles

# Calculer les fréquences de lettres et de bisymboles en français
def calculate_frequencies(text):
    letter_freq = Counter(text)
    bisymboles_freq = Counter(cut_string_into_pairs(text))
    total_letters = sum(letter_freq.values())
    total_bisymboles = sum(bisymboles_freq.values())
    letter_freq = {char: count / total_letters for char, count in letter_freq.items()}
    bisymboles_freq = {pair: count / total_bisymboles for pair, count in bisymboles_freq.items()}
    return letter_freq, bisymboles_freq

# Ajuster les fréquences des lettres en fonction des fréquences des bisymboles
def adjust_frequencies_with_bisymboles(letter_freq, bisymboles_freq):
    adjusted_letter_freq = letter_freq.copy()

    for bisymboles, freq in bisymboles_freq.items():
        if len(bisymboles) == 2:
            letter1, letter2 = bisymboles[0], bisymboles[1]
            if letter1 in adjusted_letter_freq:
                adjusted_letter_freq[letter1] -= freq  # Soustraire la frequence des bisymboles
            if letter2 in adjusted_letter_freq:
                adjusted_letter_freq[letter2] -= freq  # Soustraire la frequence des bisymboles

    # Assurer qu'aucune frequence est negative
    adjusted_letter_freq = {char: max(freq, 0) for char, freq in adjusted_letter_freq.items()}

    total_freq = sum(adjusted_letter_freq.values())
    if total_freq > 0:
        adjusted_letter_freq = {char: freq / total_freq for char, freq in adjusted_letter_freq.items()}

    return adjusted_letter_freq

# Diviser le texte chiffré en segments de longueur fixe (8 bits chacun)
def split_ciphertext_into_segments(ciphertext, segment_length=8):
    return [ciphertext[i:i + segment_length] for i in range(0, len(ciphertext), segment_length)]

# Calculer l'indice de coïncidence
def calculate_index_of_coincidence(text):
    frequency = Counter(text)
    N = sum(frequency.values())
    ic = sum(f * (f - 1) for f in frequency.values()) / (N * (N - 1)) if N > 1 else 0
    return ic

# Déchiffrer le texte basé sur les mappages
def decrypt_segments(ciphertext_segments, single_mapping, pair_mapping):
    plaintext = []
    for segment in ciphertext_segments:
        if segment in pair_mapping:
            plaintext.append(pair_mapping[segment])
        elif segment in single_mapping:
            plaintext.append(single_mapping[segment])
        else:
            plaintext.append('?')  # Placeholder si le mappage n'est pas trouvé
    return ''.join(plaintext)
