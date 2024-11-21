# Raspberry_Pi_Mass_Image_Writer
Raspberry Pi 5 that writes to many USB drives in one go. Use the LCD Keypad buttons to select the stored disk image to copy as well as reboot the device. 

Up and Down buttons are used to navigate the menu, Select button is used to confirm. When given a confirmation choice the Select button confirms the choice and any other button will cancel.

Disk images are transferred to the Raspberry Pi via a Samba shared folder. The selected image is then written in to all the drives using the ```dcfldd``` command.

## How to use?

    Login to shared folder
    Transfer image files via samba to shared folder
    Plug in all USB flash drives to write to
    Hit left button to enumerate all images and drives
    Use up/down buttons to select image
    Press the right button to start writing to drives. You can press it again to terminate writing.
    Press the select button (extreme left) to shutdown device properly to prevent data corruption. The words "Shutting down" will remain even after the device has completely shutdown, so just wait for the activity light to turn off before pulling the power.
