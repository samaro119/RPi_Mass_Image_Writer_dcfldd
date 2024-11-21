# Raspberry_Pi_Mass_Image_Writer
Raspberry Pi 5 that writes to many USB drives in one go. Use the LCD Keypad buttons to select the stored disk image to copy as well as reboot the device. 

Up and Down buttons are used to navigate the menu, Select button is used to confirm. When given a confirmation choice the Select button confirms the choice and any other button will cancel.

Disk images are transferred to the Raspberry Pi via a Samba shared folder. The selected image is then written in to all the drives using the ```dcfldd``` command.

## How to use?

1. Login to the shared folder on the Pi
2. Transfer image files to the "compressedImages" shared folder ```/home/MassImageWriter/Desktop/images/compressedImages```
3. Plug in all devices to write image files onto.
4. Use the Up and Down buttons to cycle between the menu options: ("Select img file to install?", "Find connected devices?", "Reboot?", "Shutdown")
5. Use the Select button to chose an option.
6. Verify your devices are correctly connected first with "Find connected devices?".
7. The select "Select img file to install?" which will scan the ```/home/MassImageWriter/Desktop/images/compressedImages``` folder and list the files found.
8. Use the select button on the img file you want to write to begin the operation, the current progress will be displayed on the LCD display.
