import numpy as np
import random

H = np.array([
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]
], dtype=int)


def kodowanie(tekst):
    zakodowane = []
    for znak in tekst:
        bity_danych = np.array([int(bit) for bit in f"{ord(znak):08b}"], dtype=int)

        bity_parzystosci = (np.dot(H[:, :8], bity_danych) % 2).astype(int)

        zakodowane.append(np.concatenate((bity_danych, bity_parzystosci)).tolist())
    return zakodowane


def dekodowanie(zakodowane):
    tekst = ''.join(chr(int(''.join(map(str, slowo)), 2)) for slowo in zakodowane)
    return tekst


def sprawdz_poprawnosc(zakodowana_wiadomosc):
    odkodowana = []
    for slowo in zakodowana_wiadomosc:
        syndrom = (np.dot(H, slowo) % 2).astype(int)

        if any(syndrom):
            for i in range(H.shape[1]):
                if np.array_equal(H[:, i], syndrom):
                    slowo[i] = 1 - slowo[i]
                    break
        odkodowana.append(slowo[:8])
    return odkodowana


def wprowadz_blad(zakodowane):
    indeks_slowa = random.randint(0, len(zakodowane) - 1)
    indeks_bitu = random.randint(0, len(zakodowane[indeks_slowa]) - 1)

    zakodowane[indeks_slowa][indeks_bitu] = 1 - zakodowane[indeks_slowa][indeks_bitu]

    print(f"\nWprowadzono błąd w pozycji: słowo {indeks_slowa}, bit {indeks_bitu}")
    return zakodowane

def main():
    wejscie = "input.txt"
    wyjscie = "output.txt"

    with open(wejscie, "r") as f:
        tekst = f.read()

    print("Oryginalna wiadomość:")
    print(tekst)

    zakodowane = kodowanie(tekst)
    print("\nZakodowane dane (z bitami parzystości):")
    print(zakodowane)

    zakodowane = wprowadz_blad(zakodowane)

    poprawnosc = sprawdz_poprawnosc(zakodowane)
    print("\nDane po naprawie:")
    print(poprawnosc)

    odkodowana = dekodowanie(poprawnosc)
    print("\nOdkodowana wiadomość:")
    print(odkodowana)

    with open(wyjscie, "w") as plik:
        plik.write(odkodowana)

if __name__ == '__main__':
    main()