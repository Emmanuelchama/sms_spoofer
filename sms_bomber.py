import os
import platform
import csv
import configparser

from os import system

try:
    import vonage
    import psutil
except ImportError:
    # Create an install function for this
    os.system("pip install vonage")
    os.system("pip install psutil")

try:
    import vonage
    import psutil
except:
    pass

def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def getProcess(name):
    for proc in psutil.process_iter():
        try:
            if name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False

# TODO: Do this in an init_environment() function
#       and call it in the start of main or before the main. decide what makes more sense
if platform.system() == "Windows" and getProcess("excel.exe"):
    # TODO: Dont kill excel, show a message if excel is running and exit  
    os.system("taskkill /im excel.exe")

# TODO: put this in an init_config() function 
#       and call it in the if __name__ == "__main__" section before calling main
config = configparser.ConfigParser()
try:
    open("config.ini")
    open("contacts.csv")

    config.read("config.ini")
except FileNotFoundError:
    clear()

    api_key = input("Type your API Key: ")
    api_secret = input("Type your API Secret: ")

    config.add_section("api_credentials")
    config.set("api_credentials", "api_key", api_key)
    config.set("api_credentials", "api_secret", api_secret)

    with open("config.ini", "w") as config_file:
        config.write(config_file)
    
    config.read("config.ini")

    with open("contacts.csv", "w") as contacts_file:
        fieldnames = ["name", "phone_number"]

        writer = csv.DictWriter(contacts_file, fieldnames = fieldnames)
        writer.writeheader()

# TODO: configure this in the if __name__ == "__main__" section before calling main
#       this way it would be accessible to other functions, and be organized as well
client = vonage.Client(key = config["api_credentials"]["api_key"], secret = config["api_credentials"]["api_secret"])
sms = vonage.Sms(client)

def send_sms(name, number, text, count):
    for x in range(count):
        responseData = sms.send_message(
            {
                "from": name,
                "to": number,
                "text": text,
            }
        )

    if responseData["messages"][0]["status"] == "0":
        print("SMS sent successfully.")
    else:
        print(f"SMS failed with error: {responseData['messages'][0]['error-text']}")

def dial_number():
    sender_name = input("Sender name: ")
    victim_number = input("Victim number: ").replace("+", "").replace(" ", "")

    sms_text = input("Text of SMS: ")
    sms_count = int(input("How much SMS do you want to send: "))

    send_sms(sender_name, victim_number, sms_text, sms_count)

def contacts():
    # TODO: Call clear at the start of the loop once instead of here
    clear()

    with open("contacts.csv", "r") as contacts_file:
        reader = csv.DictReader(contacts_file)

        for i, row in enumerate(reader):
            print(f"[{i + 1}]", row["name"])

    print("\n[*] Create a new contact")
    print("[M] Back to Main menu")

    select = input("\nSelect task and press Enter: ")

    if select == "*":
        # TODO: Don't let contact_creating function call you here again, you can continue the flow normally after the contact is created
        #       Maybe add a loop here as well? until the user decides he wants to quit to menu or send an sms 
        contact_creating()
    elif select.lower() == "m":
        # TODO: NO, let the loop in the main function handle this, you can just return here
        menu()
    else:
        with open("contacts.csv", "r") as contacts_file:
            reader = csv.DictReader(contacts_file)
            rows = list(reader)

        # TODO: duplication of code here, this is the same as dial_number. 
        #       you can make dial_number configurable with an extra parameter.
        sender_name = input("Sender name: ")

        select_num = int(select) - 1
        victim_number = rows[select_num]["phone_number"]

        sms_text = input("Text of SMS: ")
        sms_count = int(input("How much SMS do you want to send: "))

        send_sms(sender_name, victim_number, sms_text, sms_count)

        # TODO: NO, let the loop in the main function handle this
        menu()

def contact_creating():
    contact_name = input("\nContact name: ")
    contact_number = input("Contact number: ").replace("+", "").replace(" ", "")
        
    with open("contacts.csv", "a", newline = "") as contacts_file:
        fieldnames = ["name", "phone_number"]

        writer = csv.DictWriter(contacts_file, fieldnames = fieldnames)
        writer.writerow({"name": contact_name, "phone_number": contact_number})

    # TODO: Don't let contact_creating function call the contacts again, you can continue the flow normally after the contact is created inside the calling function    
    contacts()

def change_api_credentials():
    api_key = input("\nType your new API Key: ")
    api_secret = input("Type your new API Secret: ")
        
    config.set("api_credentials", "api_key", api_key)
    config.set("api_credentials", "api_secret", api_secret)

    with open("config.ini", "w") as config_file:
        config.write(config_file)
    
    config.read("config.ini")

    # TODO: NO, let the loop in the main function handle this
    menu()

def menu():
    clear()

    print("[1] Phone number")
    print("[2] Contacts")
    print("[3] Change API credentials")

    menu_select = input("\nSelect task and press Enter: ")

    if menu_select == "1":
        dial_number()
    elif menu_select == "2":
        contacts()
    elif menu_select == "3":
        change_api_credentials()
    else:
        menu()

# TODO: create a main function with a while loop that handles the menu selection, with an option to exit the progam. (you can just change name from menu to main and add a loop)
#       don't do a call to menu inside menu!!! (recursion) 
#       At the start of the loop call the clear function. (dont call it inside functions, handling of the ui logic should always be in the main function)
#       at the end of the main loop add a blocking message. like ("to continue press any key") in order for the status messages to show. (like on send_sms) 

if __name__ == "__main__":
    menu()