import numpy as np
import random

# stałe pliki wejściowe i wyjściowe
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"

# przygotowujemy wbudowaną wiadomość do testowania, tablica 8-bitowa 'A'
MESSAGE = np.array([0, 1, 0, 0, 0, 0, 0, 1])

# macierz kontrolna Hamminga dla kodowania i dekodowania danych
H_MATRIX = np.array([
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]
])

def encode_message(message):
    """zamienia wiadomość tekstową na ciąg bitowy: dodaje bity parzystości"""
    encoded_list = []
    for char in message:
        # każdy znak zamieniany jest na jego 8-bitową postać binarną
        data_bits = np.array([int(bit) for bit in f"{ord(char):08b}"], dtype=int)
        # bity parzystości generowane w oparciu o macierz kontrolną
        parity_bits = (np.dot(H_MATRIX[:, :8], data_bits) % 2).astype(int)
        # łączymy bity danych z wygenerowanymi bitami parzystości
        encoded_char = np.concatenate((data_bits, parity_bits))
        # zapisujemy zakodowany znak do listy
        encoded_list.append(encoded_char)
    return np.array(encoded_list)

def encode_bits(bit_array):
    """koduje tablicę bitów - rozszerzając ją o bity parzystości"""
    parity_bits = (np.dot(H_MATRIX[:, :8], bit_array) % 2).astype(int)
    # zwraca zakodowaną tablicę (bity danych + bity parzystości)
    encoded_bits = np.concatenate((bit_array, parity_bits))
    return np.array([encoded_bits])

def introduce_errors(encoded_message, num_errors=1):
    """dodaje błędy (wskazaną liczbę) do zakodowanej wiadomości"""
    modified_positions = []  # przechowuje pozycje, gdzie są już zmodyfikowane bity
    result = encoded_message.copy()  # kopia oryginalnej wiadomości

    for i in range(num_errors):
        while True:
            # losujemy znak i jego bit, który zamierzamy uszkodzić
            word_index = random.randint(0, len(result) - 1)
            bit_index = random.randint(0, len(result[word_index]) - 1)

            if (word_index, bit_index) not in modified_positions:
                # upewniamy się, że ten bit nie jest już uszkodzony
                modified_positions.append((word_index, bit_index))
                break

        # uszkadzamy wybrany bit poprzez odwrócenie jego wartości
        result[word_index][bit_index] = 1 - result[word_index][bit_index]
        print(f"\nwprowadzono błąd na pozycji: znak {word_index}, bit {bit_index}")

    return result

def count_errors(code_word):
    """sprawdza liczbę błędów w podanym słowie kodowym"""
    syndrome = np.mod(np.dot(H_MATRIX, code_word), 2)  # oblicza syndrom błędu

    if np.all(syndrome == 0):  # jeśli syndrom to same zera, to brak błędów
        return 0

    for i in range(H_MATRIX.shape[1]):
        # sprawdzamy, czy syndrom pasuje do którejś kolumny macierzy H
        if np.array_equal(syndrome, H_MATRIX[:, i]):
            return 1  # jeśli tak, mamy dokładnie 1 błąd

    return 2  # jeśli nie, to więcej niż jeden błąd

def fix_errors(encoded_message):
    """naprawa błędów w zakodowanej wiadomości"""
    fixed_message = []

    for word in encoded_message:  # dla każdego zakodowanego słowa
        syndrome = np.mod(np.dot(H_MATRIX, word), 2)  # obliczamy syndrom błędu
        error_count = count_errors(word)
        corrected_word = word.copy()  # kopia do naprawiania

        if error_count == 0:  # brak błędów
            fixed_message.append(corrected_word[:8])

        elif error_count == 1:  # naprawiamy pojedynczy błąd
            for i in range(len(corrected_word)):
                if np.array_equal(syndrome, H_MATRIX[:, i]):
                    corrected_word[i] = 1 - corrected_word[i]  # odwracamy bit
                    fixed_message.append(corrected_word[:8]) # zapisujemy poprawione dane
                    break

        else:
            # dla dwóch błędów musimy zastosować zaawansowaną naprawę
            found = False
            for i in range(len(corrected_word)):
                if found:
                    break
                for j in range(i + 1, len(corrected_word)):
                    sum_cols = (H_MATRIX[:, i] + H_MATRIX[:, j]) % 2 # suma kolumn modulo 2
                    if np.array_equal(syndrome, sum_cols):  # znaleźliśmy pasującą parę
                        corrected_word[i], corrected_word[j] = 1 - corrected_word[i], 1 - corrected_word[j] # poprawiamy oba błedy błąd
                        fixed_message.append(corrected_word[:8]) # zapisujemy poprawione dane
                        found = True
                        break

            if not found:
                fixed_message.append(word[:8])  # błędy zostają niezmienione / nie udało sie naprawić

    return np.array(fixed_message)

def decode_message(encoded_data):
    """konwersja naprawionej wiadomości binarnej na tekst"""
    return ''.join(chr(int(''.join(map(str, word)), 2)) for word in encoded_data)

def process_bits(bit_array, error_count):
    """procedura obsługi tablicy bitów: koduje, uszkadza, naprawia"""
    print("\nOryginalne bity:")
    print(bit_array)

    encoded_bits = encode_bits(bit_array)  # kodowanie
    print("\nBity zakodowane:")
    print(encoded_bits)

    damaged_bits = introduce_errors(encoded_bits, error_count)  # wprowadzenie błędów
    print("\nBity z błędami:")
    print(damaged_bits)

    repaired_bits = fix_errors(damaged_bits)  # naprawa
    print("\nBity po naprawie:")
    print(repaired_bits)

    return repaired_bits

def process_message(message, error_count):
    """proces przetwarzania wiadomości: kodowanie -> błędy -> naprawa"""
    print("\nWiadomość oryginalna:")
    print(message)

    encoded_message = encode_message(message)  # kodowanie wiadomości
    print("\nWiadomość zakodowana:")
    print(encoded_message)

    damaged_message = introduce_errors(encoded_message, error_count)  # wprowadzenie błędów
    print("\nWiadomość z błędami:")
    print(damaged_message)

    repaired_message = fix_errors(damaged_message)  # naprawa
    print("\nWiadomość po naprawie:")
    print(repaired_message)

    decoded_message = decode_message(repaired_message)  # dekodowanie na tekst
    print("\nWiadomość zdekodowana:")
    print(decoded_message)

    return decoded_message

def process_file():
    """procesowanie wiadomości z pliku wejściowego"""
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            message = f.read()

        decoded_message = process_message(message, 2)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(decoded_message)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

def main():
    """główne menu programu - wybór opcji"""
    print("1. Przetwarzanie wbudowanej wiadomości z 1 błędem")
    print("2. Przetwarzanie wbudowanej wiadomości z 2 błędami")
    print("3. Przetwarzanie z pliku")

    choice = input("Wybierz opcję: ")

    if choice == "1":
        process_bits(MESSAGE, 1)

    elif choice == "2":
        process_bits(MESSAGE, 2)

    elif choice == "3":
        process_file()

if __name__ == "__main__":
    main()
