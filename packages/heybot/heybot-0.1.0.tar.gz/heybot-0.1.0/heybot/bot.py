import pywhatkit

def run_bot():
    print("WhatsApp Bot Activated!\n")

    number = input("Enter recipient number (with +91 or your country code): ")
    message = input("Enter your message: ")
    hour = int(input("Enter hour (24-hour format): "))
    minute = int(input("Enter minute: "))

    try:
        pywhatkit.sendwhatmsg(number, message, hour, minute)
        print(" Message scheduled successfully!")
    except Exception as e:
        print(f" Error: {e}")