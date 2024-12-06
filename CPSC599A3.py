import serial
import time
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Connect to Arduino
arduino_port = "COM3"  # Change this to your Arduino's port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Wait for Arduino to initialize

# Sound file mapping
sounds = {
    "block": r"C:\Users\hossa\Documents\599A3\CPSC599A3\block.mp3",
    "punch": r"C:\Users\hossa\Documents\599A3\CPSC599A3\Punch.mp3",
    "powerUp": r"C:\Users\hossa\Documents\599A3\CPSC599A3\PowerUp.mp3",
    "superBlock": r"C:\Users\hossa\Documents\599A3\CPSC599A3\SuperBlock.mp3",
    "combination": r"C:\Users\hossa\Documents\599A3\CPSC599A3\combinationAttack.mp3"
}

print("Connected to Arduino.")
print("Type commands ('win' or 'loss') to send to Arduino. Type 'exit' to quit.")

while True:
    user_input = input("Enter command (win/loss/exit): ").strip().lower()

    if user_input == "exit":
        print("Exiting program...")
        break

    # Send the input to the Arduino
    ser.write(user_input.encode('utf-8'))
    print(f"Sent '{user_input}' to Arduino.")

    # Wait for a response from Arduino
    command = None
    while not ser.in_waiting:  # Wait until data is available
        time.sleep(0.1)

    command = ser.readline().decode('utf-8').strip()
    print(f"Received command: {command}")

    if command in sounds:
        print(f"Playing sound for: {command}")
        
        # Stop any currently playing sound
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # Load and play the new sound
        pygame.mixer.music.load(sounds[command])
        pygame.mixer.music.play()

        # Wait until the sound finishes playing before proceeding
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    else:
        print(f"No sound mapped for command: {command}")


# Close the serial connection
ser.close()
