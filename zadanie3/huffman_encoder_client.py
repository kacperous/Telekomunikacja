import heapq
import socket
import pickle

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def calculate_frequencies(filepath):
    frequencies = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    return frequencies, text

def build_huffman_tree(frequencies):
    priority_queue = [HuffmanNode(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)

        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(priority_queue, merged)

    return priority_queue[0]

def generate_codes(node, current_code="", codes={}):
    if node is None:
        return

    if node.char is not None:
        codes[node.char] = current_code if current_code else "0"
        return codes

    codes.update(generate_codes(node.left, current_code + "0", codes.copy()))
    codes.update(generate_codes(node.right, current_code + "1", codes.copy()))
    return codes


def encode_text(text, codes):
    encoded_text = ""
    for char in text:
        encoded_text += codes[char]
    return encoded_text

def pad_encoded_text(encoded_text):
    extra_padding = 8 - len(encoded_text) % 8
    if extra_padding == 8:
        extra_padding = 0

    padded_encoded_text = encoded_text + '0' * extra_padding
    padding_info = "{:08b}".format(extra_padding)
    return padded_encoded_text, padding_info

def get_byte_array(padded_encoded_text):
    if len(padded_encoded_text) % 8 != 0:
        print("Error: Padded text length is not a multiple of 8")
        exit()

    b = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        b.append(int(byte, 2))
    return b

filepath = "plik_do_zakodowania.txt"
server_address = ('localhost', 65432)

frequencies, original_text = calculate_frequencies(filepath)
if not frequencies:
    print("Plik jest pusty.")
    exit()

root = build_huffman_tree(frequencies)
huffman_codes = generate_codes(root)

# Słownik Huffmana zebysmy wiedzieli wogole jak on to koduje
print("Słownik kodowy Huffmana:")
for char, code in sorted(huffman_codes.items()):
     print(f"  '{char}': {code}")
print("-" * 20)


encoded_text = encode_text(original_text, huffman_codes)
padded_text, padding_info = pad_encoded_text(encoded_text)
byte_array = get_byte_array(padded_text)

serialized_codes = pickle.dumps(huffman_codes)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Łączenie z {server_address}...")
        s.connect(server_address)
        print("Połączono.")

        codes_len = len(serialized_codes).to_bytes(4, byteorder='big')
        print(f"Wysyłanie długości słownika: {len(serialized_codes)} bajtów")
        s.sendall(codes_len)

        print("Wysyłanie słownika...")
        s.sendall(serialized_codes)

        print(f"Wysyłanie informacji o paddingu: {int(padding_info, 2)} bitów")
        s.sendall(int(padding_info, 2).to_bytes(1, byteorder='big'))

        print(f"Wysyłanie danych: {len(byte_array)} bajtów")
        s.sendall(byte_array)
        print("Wysyłanie zakończone.")

except ConnectionRefusedError:
    print(f"Błąd: Nie można połączyć się z serwerem {server_address}. Czy serwer jest uruchomiony?")
except Exception as e:
    print(f"Wystąpił błąd sieciowy: {e}")
