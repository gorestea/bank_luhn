from random import randint

def gen():

    master_card, new_card = randint(511111, 551111), randint(111111111, 999999999)
    card_number = str(master_card) + str(new_card)
    print(card_number)

    return card_number

def luhn(card_number):

    summa = 0

    for number in card_number[::2]:
        if int(number) * 2 > 9:
            number = int(number) * 2 - 9
        else:
            number = int(number) * 2

        summa += int(number)

    for number in card_number[1::2]:
        summa += int(number)

    if (summa % 10) != 0:
        summa2 = (summa + 10) - (summa % 10)
        last = summa2 - summa
        card_number += str(last)

    print(card_number)
    return str(card_number)

def main():
    return luhn(gen())

if __name__ == '__main__':
    main()
