import speech_recognition as sr
import pyautogui
import time

r = sr.Recognizer()
typing_enabled = False

print("Say 'type' to start typing at cursor")
print("Say 'stop typing' to pause")
print("Say 'exit' to quit")

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source)

            text = r.recognize_google(audio).lower()
            print("Recognized:", text)

            if "exit" in text:
                print("Exiting program...")
                break

            if "type" in text:
                typing_enabled = True
                print("Typing enabled — place cursor anywhere")
                continue

            if "stop typing" in text:
                typing_enabled = False
                print("Typing paused")
                continue

            if typing_enabled:
                time.sleep(0.1)
                pyautogui.write(text + " ", interval=0.04)

    except sr.UnknownValueError:
        pass

    except sr.RequestError as e:
        print("API error:", e)

    except KeyboardInterrupt:
        break
