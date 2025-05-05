import socket
import pickle

def remove_padding(padded_encoded_text, padding_info_byte):
    padding_amount = int.from_bytes(padding_info_byte, byteorder='big')
    if padding_amount == 0:
        return padded_encoded_text
    return padded_encoded_text[:-padding_amount]

def decode_text(encoded_text, huffman_codes):
    reverse_codes = {v: k for k, v in huffman_codes.items()}
    if not reverse_codes:
        return ""

    current_code = ""
    decoded_text = ""

    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codes:
            character = reverse_codes[current_code]
            decoded_text += character
            current_code = ""

    return decoded_text

server_address = ('0.0.0.0', 65432)
output_filepath = "plik_odkodowany.txt"
buffer_size = 4096

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_socket:
    serv_socket.bind(server_address)
    serv_socket.listen(1)
    print(f"Serwer nasłuchuje na {server_address}...")

    conn, addr = serv_socket.accept()
    with conn:
        print(f"Połączono z {addr}")

        try:
            codes_len_bytes = conn.recv(4)
            if not codes_len_bytes: raise ConnectionError("Klient rozłączył się przedwcześnie (długość słownika).")
            codes_len = int.from_bytes(codes_len_bytes, byteorder='big')
            print(f"Oczekiwanie na słownik o długości: {codes_len} bajtów")

            serialized_codes = b""
            while len(serialized_codes) < codes_len:
                chunk = conn.recv(min(buffer_size, codes_len - len(serialized_codes)))
                if not chunk: raise ConnectionError("Klient rozłączył się podczas wysyłania słownika.")
                serialized_codes += chunk
            huffman_codes = pickle.loads(serialized_codes)
            print("Odebrano i zdeserializowano słownik.")

            padding_info_byte = conn.recv(1)
            if not padding_info_byte: raise ConnectionError("Klient rozłączył się przed wysłaniem info o paddingu.")
            print(f"Odebrano info o paddingu: {int.from_bytes(padding_info_byte, byteorder='big')} bitów")

            encoded_data_bytes = bytearray()
            print("Odbieranie danych...")
            while True:
                chunk = conn.recv(buffer_size)
                if not chunk:
                    break
                encoded_data_bytes.extend(chunk)
            print(f"Odebrano {len(encoded_data_bytes)} bajtów danych.")

            encoded_bit_string = "".join(format(byte, "08b") for byte in encoded_data_bytes)

            encoded_text_no_padding = remove_padding(encoded_bit_string, padding_info_byte)

            decoded_text = decode_text(encoded_text_no_padding, huffman_codes)

            print(f"Zapisywanie odkodowanego tekstu do {output_filepath}...")
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(decoded_text)
            print("Zapisano pomyślnie.")

        except pickle.UnpicklingError:
            print("Błąd: Nie można zdeserializować słownika kodowego.")
        except ConnectionError as e:
             print(f"Błąd połączenia: {e}")
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {e}")
        finally:
            print("Zamykanie połączenia.")

print("Serwer zakończył działanie.")
