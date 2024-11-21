import subprocess
import sys
import time
import os
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.color = [102, 51, 153]

now_writing = False
program_state = 0
submenu_state = 0

last_pressed_time = time.time()

find_devices_command = """
for device in /dev/sd[a-z]; do
echo "$device"
done
"""

# Define the path to the compressedImages folder
compressed_images_folder = os.path.join(os.path.dirname(__file__), "compressedImages")
found_file_names = []

lcd.clear()
#lcd.message = "MassImageWriter\nPress up/down..."
print("Mass Image Writer program start...")
lcd.message = "MassImageWriter\nPress up/down..."

def powerOff():
    lcd.clear()
    lcd.message = "Rebooting"
    time.sleep(0.5)
    lcd.message = "Rebooting."
    time.sleep(0.5)
    lcd.message = "Rebooting.."
    time.sleep(0.5)
    lcd.message = "Rebooting..."
    time.sleep(0.5)
    lcd.clear()
    lcd.color = [0, 0, 0]
    subprocess.run(["sudo","reboot"], capture_output=True, text=True)

# Reads all files in the compressedImages folder and saves their names to a list.
def get_compressed_images():

    if not os.path.exists(compressed_images_folder):
        print("\nError: 'compressedImages' folder not found.")
        lcd.message = "'compressedImages'\nfolder not found!"
        return []

    # Get the list of files in the folder
    file_names = [
        file_name for file_name in os.listdir(compressed_images_folder)
        if os.path.isfile(os.path.join(compressed_images_folder, file_name))
    ]

    if not file_names:
        print("\nNo files found in the 'compressedImages' folder.")
        lcd.message = "No files found"
        return []

    print(f"\nFiles found in 'compressedImages' folder:\n{file_names}")
    lcd.message = f"Found {len(file_names)} files...\nup/down to chose"
    return file_names

def find_and_display_devices():
    lcd.clear()
    # Run the find devices command and capture the output
    devices_found = subprocess.run(["bash", "-c", find_devices_command], capture_output=True, text=True)

    # Access the output and process
    output_devices_found = devices_found.stdout
    output_device_lines = output_devices_found.splitlines()
    output_device_count = len(output_device_lines)

    # Output number of devices
    print(f"\nFound {output_device_count} devices:")
    lcd.message = "Found " + str(output_device_count) + " devices: "

    # Output each device name found
    for device in output_device_lines:
        print(f"{device}")
        lcd.message = "Found " + str(output_device_count) + " devices:\n" + device
        time.sleep(1)

def write_to_devices(file_location):

    # Run the find devices command and capture the output
    devices_found = subprocess.run(["bash", "-c", find_devices_command], capture_output=True, text=True)

    # Access the output and process
    output_devices_found = devices_found.stdout
    output_device_lines = output_devices_found.splitlines()
    output_device_count = len(output_device_lines)

    # Output number of devices
    print(f"\nWriting to {output_device_count} devices:")
    lcd.clear()
    lcd.message = "Writing to \n" + str(output_device_count) + " devices:"
    time.sleep(1)
    # Output each device name found
    for device in output_device_lines:
        print(f"\nWriting {file_location} to {device}...")
        # Find file size
        file_size_raw = subprocess.run(["du","-m", f"compressedImages/{file_location}"], capture_output=True, text=True)
        file_size = file_size_raw.stdout
        file_size = file_size.split("\t")[0]
        # Write command for dcfldd
        write_command = ["sudo", "dcfldd",f"if=compressedImages/{file_location}",f"of={device}","bs=4M","status=on","statusinterval=5"]

        # Run the write command
        process  = subprocess.Popen(write_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Process the output line by line
        for line in process.stderr:
            if "Mb" in line:
                try:
                    # Extract the megabytes written
                    megabytes_written = line.strip().split()[2]
                    megabytes_written = megabytes_written.strip('()').replace('Mb', '')
                    percentage_progress = int((int(megabytes_written) / int(file_size)) // 0.01)

                    lcd.clear()
                    lcd.message = f"{percentage_progress}% {device}\n{megabytes_written}Mb / {file_size}Mb"

                    print(f"Progress for {device}: {percentage_progress}%")
                except IndexError:
                    pass  # Handle unexpected line formats gracefully

        # Wait for the process to complete
        process.wait()
        # Check for any errors
        lcd.clear()
        if process.returncode != 0:
            print("Error running dcfldd: \n", process.stderr.read())
            lcd.message = "Error writing to\n" + device
        else:
            print(f"dcfldd completed successfully for {device}: \n", process.stdout.read())
            lcd.message = "dcfldd completed successfully \nfor "+ device
    lcd.clear()
    print("\nWrite operation finished")
    lcd.message = "Write complete!!!"
    program_state = 0

while True:
    #time.sleep(0.01) #To prevent excessive CPU use
    current_time = time.time()
    # Button debounce implementation
    if (current_time - last_pressed_time) >= 0.5:

        # program state 1, select between find devices, select img, shutdown
        if program_state == 1:
            # Display submenu options
            if submenu_state == 0:
                lcd.message = "select img file\nto install?"
            elif submenu_state == 1:
                lcd.message = "Find connected\ndevices?"
            elif submenu_state == 2:
                lcd.message = "Reboot?"

            # Menu item is selected
            if lcd.select_button:
                lcd.clear()
                last_pressed_time = current_time
                # Select img file to install
                if submenu_state == 0:
                    program_state = 2
                    submenu_state = 0
                    # select img file
                    found_file_names = get_compressed_images()
                # Find connected devices
                if submenu_state == 1:
                    program_state = 0
                    # Display connected devices
                    find_and_display_devices()
                # Shutdown Pi
                if submenu_state == 2:
                    # Powers down the Pi
                    powerOff()

            # iterate forward to next menu item
            elif lcd.up_button:
                lcd.clear()
                last_pressed_time = current_time
                if submenu_state == 2:
                    submenu_state = 0
                else:
                    submenu_state += 1
            # iterate forward to next menu item
            elif lcd.down_button:
                lcd.clear()
                last_pressed_time = current_time
                if submenu_state == 0:
                    submenu_state = 2
                else:
                    submenu_state -= 1

        # Program state 2, select img file to write to devices
        elif program_state == 2:
            if lcd.select_button and not now_writing:
                lcd.clear()
                last_pressed_time = current_time
                print(f"\nConfirm write {found_file_names[submenu_state]} to found devices with the select button")
                lcd.message = "Start write?\n" + found_file_names[submenu_state]
                program_state = 3
            # iterate forward to next menu item
            elif lcd.up_button:
                lcd.clear()
                last_pressed_time = current_time
                if submenu_state == len(found_file_names)-1:
                    submenu_state = 0
                else:
                    submenu_state += 1
                lcd.message = "Select file " + str(submenu_state) + "?\n" + found_file_names[submenu_state]
            # iterate forward to next menu item
            elif lcd.down_button:
                lcd.clear()
                last_pressed_time = current_time
                if submenu_state == 0:
                    submenu_state = len(found_file_names)-1
                else:
                    submenu_state -= 1
                lcd.message = "Select file " + str(submenu_state) + "?\n" + found_file_names[submenu_state]

            elif lcd.left_button or lcd.right_button:
                lcd.clear()
                last_pressed_time = current_time
                program_state = 1
                submenu_state = 0

        # Final verification state before write
        elif program_state == 3:
            if lcd.select_button and not now_writing:
                lcd.clear()
                last_pressed_time = current_time

                now_writing = True
                write_to_devices(found_file_names[submenu_state])
                now_writing = False

            elif lcd.up_button or lcd.down_button or lcd.left_button or lcd.right_button:
                if not now_writing:
                    last_pressed_time = current_time
                    program_state = 0

        # Program state 0, float state after action is finished
        elif program_state == 0:
            if lcd.select_button or lcd.up_button or lcd.down_button or lcd.left_button or lcd.right_button:
                lcd.clear()
                last_pressed_time = current_time
                program_state = 1
                submenu_state = 0
