import speech_recognition as sr
import pyautogui
import time
import argparse


def choose_microphone_index(microphone_names, requested_index=None):
    if requested_index is not None:
        if 0 <= requested_index < len(microphone_names):
            return requested_index
        raise ValueError(f"Invalid microphone index: {requested_index}")

    scored_devices = []
    for index, name in enumerate(microphone_names):
        lower_name = name.lower()
        score = 0

        if "mic" in lower_name or "microphone" in lower_name:
            score += 3
        if "headset" in lower_name or "usb" in lower_name:
            score += 2
        if "stereo mix" in lower_name or "virtual" in lower_name:
            score -= 3
        if "output" in lower_name or "speaker" in lower_name:
            score -= 2

        scored_devices.append((score, index))

    scored_devices.sort(reverse=True)
    best_score, best_index = scored_devices[0]
    if best_score <= 0:
        return None
    return best_index


def get_microphone_candidates(microphone_names, requested_index=None):
    if requested_index is not None:
        return [requested_index]

    candidates = []
    auto_pick = choose_microphone_index(microphone_names)
    if auto_pick is not None:
        candidates.append(auto_pick)

    if None not in candidates:
        candidates.append(None)

    for index in range(len(microphone_names)):
        if index not in candidates:
            candidates.append(index)

    return candidates


def main():
    parser = argparse.ArgumentParser(description="SPARSH voice typing")
    parser.add_argument("--mic-index", type=int, default=None, help="Microphone index to use")
    parser.add_argument("--list-mics", action="store_true", help="List all microphones and exit")
    args = parser.parse_args()

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 250
    typing_enabled = True

    print("Voice typing starts ON by default")
    print("Say 'type' or 'start typing' to resume typing")
    print("Say 'stop typing' to pause")
    print("Say 'exit' to quit")
    print("Initializing microphone...")

    microphones = sr.Microphone.list_microphone_names()
    print(f"Detected microphones: {len(microphones)}")

    if args.list_mics:
        for index, name in enumerate(microphones):
            print(f"[{index}] {name}")
        return

    try:
        candidates = get_microphone_candidates(microphones, args.mic_index)
        source = None

        for candidate in candidates:
            candidate_name = microphones[candidate] if candidate is not None else "System default input"
            candidate_source = sr.Microphone(device_index=candidate)
            try:
                candidate_source.__enter__()
                if candidate_source.stream is None:
                    raise OSError("Audio stream unavailable")

                recognizer.adjust_for_ambient_noise(candidate_source, duration=1.0)
                source = candidate_source
                print(f"Using microphone: {candidate_name}")
                break
            except Exception:
                if getattr(candidate_source, "stream", None) is not None:
                    try:
                        candidate_source.__exit__(None, None, None)
                    except Exception:
                        pass
                continue

        if source is None:
            print("Microphone error: Could not open any microphone input device.")
            return

        print("Microphone ready. Listening...")

        while True:
            try:
                audio = recognizer.listen(source, timeout=7, phrase_time_limit=8)
                text = recognizer.recognize_google(audio).lower().strip()
                print("Recognized:", text)

                if "exit" in text:
                    print("Exiting program...")
                    break

                if "stop typing" in text:
                    typing_enabled = False
                    print("Typing paused")
                    continue

                if text == "type" or "start typing" in text:
                    typing_enabled = True
                    print("Typing enabled — place cursor anywhere")
                    continue

                if typing_enabled:
                    time.sleep(0.1)
                    pyautogui.write(text + " ", interval=0.04)
                else:
                    print("Typing is paused. Say 'type' to enable.")

            except sr.WaitTimeoutError:
                print("No speech detected. Listening...")

            except sr.UnknownValueError:
                print("Could not understand audio. Try speaking clearly.")

            except sr.RequestError as e:
                print("API error:", e)

            except AssertionError:
                print("Microphone stream dropped. Restart voice control and try a different --mic-index.")
                break

        if getattr(source, "stream", None) is not None:
            try:
                source.__exit__(None, None, None)
            except Exception:
                pass

    except ValueError as e:
        print(e)
    except OSError as e:
        print("Microphone error:", e)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
