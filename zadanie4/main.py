import soundcard as sc
import numpy as np
from scipy.io.wavfile import write, read

# Dostępne poziomy kwantyzacji (głębia bitowa)
WSPIERANE_GLEBIE_BITOWE = [8, 16, 32]
# Domyślna liczba kanałów (1 dla mono, 2 dla stereo)
KANALY = 1


def nagrywaj_i_zapisz_audio(nazwa_pliku, czas_trwania_s, czestotliwosc_probkowania, glebia_bitowa, kanaly=KANALY):
    print(f"\nRozpoczynanie nagrywania: {nazwa_pliku}")
    print(f"Parametry: czas={czas_trwania_s}s, Fs={czestotliwosc_probkowania}Hz, bity={glebia_bitowa}, kanały={kanaly}")

    try:
        mikrofon = sc.default_microphone()
        # Nagrywanie - soundcard zazwyczaj zwraca dane jako float32 w zakresie [-1.0, 1.0]
        liczba_ramek = int(czas_trwania_s * czestotliwosc_probkowania)
        nagranie_float = mikrofon.record(numframes=liczba_ramek, samplerate=czestotliwosc_probkowania, channels=kanaly)

        print("Nagrywanie zakończone. Rozpoczynanie kwantyzacji i zapisu...")

        # Kwantyzacja i konwersja do odpowiedniego formatu całkowitoliczbowego dla WAV
        if glebia_bitowa == 8:
            # Skalowanie do zakresu [0, 255] dla uint8
            # (nagranie_float + 1.0) / 2.0  => mapuje [-1,1] na [0,1]
            # * 255                         => mapuje [0,1] na [0,255]
            dane_skwantyzowane = ((nagranie_float + 1.0) / 2.0 * 255).astype(np.uint8)
        elif glebia_bitowa == 16:
            # Skalowanie do zakresu [-32768, 32767] dla int16
            dane_skwantyzowane = (nagranie_float * 32767).astype(np.int16)
        elif glebia_bitowa == 32:
            # Skalowanie do zakresu [-2147483648, 2147483647] dla int32
            dane_skwantyzowane = (nagranie_float * (2 ** 31 - 1)).astype(np.int32)
        else:
            print(f"Nieobsługiwana głębia bitowa: {glebia_bitowa}. Zapisuję jako 16-bit.")
            dane_skwantyzowane = (nagranie_float * 32767).astype(np.int16)

        # Zapis do pliku WAV
        write(nazwa_pliku, czestotliwosc_probkowania, dane_skwantyzowane)
        print(f"Dźwięk zapisany jako: {nazwa_pliku}")

    except Exception as e:
        print(f"Wystąpił błąd podczas nagrywania lub zapisu: {e}")


def odtworz_audio_z_pliku(nazwa_pliku):
    print(f"\nOdtwarzanie pliku: {nazwa_pliku}")
    try:
        czestotliwosc_probkowania, dane_audio = read(nazwa_pliku)
        print(f"Odczytana częstotliwość próbkowania: {czestotliwosc_probkowania} Hz")
        print(f"Oryginalny typ danych wczytanych z pliku: {dane_audio.dtype}")

        # Konwersja do float32 i normalizacja do zakresu [-1.0, 1.0]
        dane_znormalizowane = None
        if dane_audio.dtype == np.int16:
            # Zakres int16: -32768 do 32767
            dane_znormalizowane = dane_audio.astype(np.float32) / np.iinfo(np.int16).max
        elif dane_audio.dtype == np.int32:
            # Zakres int32: -2147483648 do 2147483647
            dane_znormalizowane = dane_audio.astype(np.float32) / np.iinfo(np.int32).max
        elif dane_audio.dtype == np.uint8:
            # Zakres uint8: 0 do 255. Mapujemy [0, 255] -> [-1.0, 1.0]
            dane_znormalizowane = (dane_audio.astype(np.float32) / 255.0 - 0.5) * 2.0
        elif dane_audio.dtype == np.float32:
            # Jeśli plik WAV jest już float32, zakładamy, że jest już w odpowiednim zakresie.
            # W praktyce pliki WAV float32 często mają zakres [-1.0, 1.0].
            dane_znormalizowane = dane_audio
        else:
            print(f"Nierozpoznany lub nieobsługiwany typ danych z pliku WAV: {dane_audio.dtype}.")
            print("Próba odtworzenia może się nie udać lub dźwięk może być zniekształcony.")
            dane_znormalizowane = dane_audio.astype(np.float32)


        if dane_znormalizowane is not None:

            glosnik = sc.default_speaker()
            glosnik.play(dane_znormalizowane, samplerate=czestotliwosc_probkowania)
            print("Odtwarzanie rozpoczęte. Powinno zakończyć się automatycznie.")

        else:
            print("Nie udało się przygotować danych do odtworzenia.")


    except FileNotFoundError:
        print(f"Błąd: Plik '{nazwa_pliku}' nie został znaleziony.")
    except Exception as e:
        print(f"Wystąpił błąd podczas wczytywania lub przygotowywania do odtwarzania: {e}")
        import traceback
        traceback.print_exc()


def pobierz_parametry_nagrywania():
    while True:
        try:
            glebia = int(input(f"Podaj poziom kwantyzacji {WSPIERANE_GLEBIE_BITOWE}: "))
            if glebia in WSPIERANE_GLEBIE_BITOWE:
                break
            else:
                print(f"Niepoprawna wartość. Wybierz spośród {WSPIERANE_GLEBIE_BITOWE}.")
        except ValueError:
            print("Proszę podać liczbę całkowitą.")

    while True:
        try:
            probkowanie = int(input("Podaj częstotliwość próbkowania (np. 8000, 22050, 44100, 48000 Hz): "))
            if probkowanie > 0:
                break
            else:
                print("Częstotliwość próbkowania musi być dodatnia.")
        except ValueError:
            print("Proszę podać liczbę całkowitą.")

    while True:
        try:
            czas = int(input("Podaj czas nagrania w sekundach: "))
            if czas > 0:
                break
            else:
                print("Czas nagrania musi być dodatni.")
        except ValueError:
            print("Proszę podać liczbę całkowitą.")

    nazwa_pliku_sugerowana = f"nagranie_b{glebia}_fs{probkowanie}.wav"
    nazwa_pliku_uzytkownika = input(f"Podaj nazwę pliku do zapisu (sugerowana: '{nazwa_pliku_sugerowana}'): ")
    if not nazwa_pliku_uzytkownika.strip():
        nazwa_pliku = nazwa_pliku_sugerowana
    else:
        nazwa_pliku = nazwa_pliku_uzytkownika if nazwa_pliku_uzytkownika.endswith(
            ".wav") else nazwa_pliku_uzytkownika + ".wav"

    return nazwa_pliku, czas, probkowanie, glebia


def main():
    while True:
        print("\n--- Menu Główne ---")
        opcja = input("Wybierz opcję:\n"
                      "1. Nagrywanie dźwięku\n"
                      "2. Odtwarzanie dźwięku\n"
                      "3. Koniec programu\n"
                      "Twój wybór: ")

        if opcja == '1':
            nazwa_pliku, czas, probkowanie, glebia = pobierz_parametry_nagrywania()
            nagrywaj_i_zapisz_audio(nazwa_pliku, czas, probkowanie, glebia, kanaly=KANALY)

        elif opcja == '2':
            nazwa_pliku_do_odtworzenia = input("Podaj nazwę pliku WAV do odtworzenia: ")
            if not nazwa_pliku_do_odtworzenia.endswith(".wav"):
                nazwa_pliku_do_odtworzenia += ".wav"
            odtworz_audio_z_pliku(nazwa_pliku_do_odtworzenia)

        elif opcja == '3':
            print("Zamykanie programu.")
            break
        else:
            print("Podałeś niepoprawną opcję. Spróbuj ponownie.")


if __name__ == '__main__':
    main()