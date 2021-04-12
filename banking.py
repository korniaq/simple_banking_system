import random
import sys
import sqlite3


def generate_card_number():
    while True:
        digits = [4,0,0,0,0,0]
        for i in range(9):
            digits.append(random.randint(0,9))

        new_card = ''
        for digit in digits:
            new_card += str(digit)

        suma = 0
        for i in range(len(digits)):
            if i%2 == 0:
                digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
            suma += digits[i]

        if suma%10 == 0:
            new_card += str(0)
        else:
            new_card += str(10-suma%10)

        cur.execute("SELECT number FROM card;")
        if new_card not in cur.fetchall():
            break

    return new_card


def create_account():
    new_card = generate_card_number()
    new_pin = ''
    for i in range(4):
        new_pin += str(random.randint(0, 9))
    print("Your card has been created")
    print("Your card number:")
    print(new_card)
    print("Your card PIN:")
    print(new_pin)

    cur.execute("INSERT INTO card (id, number, pin) VALUES (?, ?, ?);", (int(new_card[6:15]), new_card, new_pin))
    conn.commit()


def log_in():
    print("Enter your card number:")
    card = input()
    print("Enter your PIN:")
    pin = input()
    cur.execute("SELECT number, pin FROM card")
    correct = True
    if (card, pin) not in cur.fetchall():
        correct = False
    return card, pin, correct


def check_balance(card):
    cur.execute("SELECT balance FROM card WHERE number = ?;", (card,))
    print("Balance:", cur.fetchone()[0])


def add_income(card):
    print("Enter income:")
    income = int(input())
    cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (income, card))
    print("Income was added!")
    conn.commit()


def check_luhn_algorithm(card):
    digits = []
    for digit in card:
        digits.append(int(digit))

    suma = 0
    for i in range(len(digits)-1):
        if i % 2 == 0:
            digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
        suma += digits[i]

    if (suma+digits[-1]) % 10 == 0:
        return True
    else:
        return False


def do_transfer(card):
    print("Transfer")
    print("Enter card number:")
    card1 = input()
    cur.execute("SELECT number FROM card")
    if not check_luhn_algorithm(card1):
        print("Probably you made a mistake in the card number. Please try again!")
    elif card1 not in [fetch[0] for fetch in cur.fetchall()]:
        print("Such a card does not exist.")
    else:
        print("Enter how much money you want to transfer:")
        transfer = int(input())
        cur.execute("SELECT balance FROM card WHERE number = ?;", (card,))
        if transfer > cur.fetchone()[0]:
            print("Not enough money!")
        else:
            cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?;", (transfer, card))
            cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (transfer, card1))
            conn.commit()
            print("Success!")


def close_account(card):
    cur.execute("DELETE FROM card WHERE number = ?", (card,))
    conn.commit()
    print("The account has been closed!")


conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0);""")
conn.commit()

while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    choice = int(input())
    if choice == 1:
        create_account()

    elif choice == 2:
        card, pin, correct = log_in()
        if not correct:
            print("Wrong card number or PIN!")
            continue

        print("You have successfully logged in!")
        while True:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            choice1 = int(input())
            if choice1 == 1:
                check_balance(card)
            elif choice1 == 2:
                add_income(card)
            elif choice1 == 3:
                do_transfer(card)
            elif choice1 == 4:
                close_account(card)
            elif choice1 == 5:
                print("You have successfully logged out!")
                break
            elif choice1 == 0:
                print("Bye!")
                sys.exit()
            else:
                print("Wrong input")
    elif choice == 0:
        print("Bye!")
        sys.exit()
    else:
        print("Wrong input")
