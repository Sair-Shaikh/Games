import UNO
import Scrabble

while True:
    user_input = input("Enter 'U' to play UNO and 'S' to play scrabble. Press q to quit.\n")

    if user_input == "U":
        UNO.main()  # assuming that file1 has a main() function that runs its main logic
    elif user_input == "S":
        Scrabble.main()  # assuming that file2 has a main() function that runs its main logic
    elif user_input == "q":
        break  # exit the loop if the user enters "q"
    else:
        print("Invalid input. Please enter 1, 2, or q.")