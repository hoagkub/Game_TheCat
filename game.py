import client
import server
import os

clear = lambda: os.system('cls')

if __name__ == "__main__":
    clear()
    if (input("Do you have an available server (y/n): ")=="y"):
        print("Join a exist server room...")
        client.main()
    else:
        print("Create new server room...")
        server.main()
