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

## Hardware

- Raspberry Pi 5 Model B ([CE Link](https://core-electronics.com.au/raspberry-pi-5-model-b-4gb.html)) (Any Pi with USB 3.0 ports will work just as well)
- Adafruit i2c 16x2 LCD Pi Plate with keypad ([CE Link](https://core-electronics.com.au/adafruit-blue-white-16x2-lcd-keypad-kit-for-raspberry-pi.html))
- USB hubs (not all hubs are supported well, use the ones from [this list](https://elinux.org/RPi_Powered_USB_Hubs))
- USB SD card adapters
- USB Gigabit adapter (optional)

## Setting up

Use the Raspberry Pi Imager ([Link](https://www.raspberrypi.com/software/)) to install Raspberry Pi OS (64-bit) onto an SD card that is large enough to store multiple large img files (32Gb or larger is recommended).

Use the following OS customisation settings:

GENERAL
- Username: MassImageWriter
- Password: MassImageWriter123
- Time zone: Australia/Sydney
- Keyboard layout: us

SERVICES
- Enable SSH
- Use password authentication

Once the Pi is booted with this SD card either open a terminal window on the Pi or SSD into it. Run the following commands on the Pi to install the required files:


    sudo apt update
    sudo apt-get upgrade
    sudo apt install dcfldd
    sudo apt-get install samba samba-common-bin
    pip3 install adafruit-circuitpython-charlcd


    

This will install the required packages for the dcfldd write command, the LCD display and the Samba shared folder. If the adafruit-circuitpython-charlcd install fails try this command instead:

    pip3 install adafruit-circuitpython-charlcd --break-system-packages

The I2C interface will need to be enabled to use the LCD display. 

    sudo raspi-config

Interface Options -> I2C -> Yes -> Ok -> Finish

More detailed instructions for enabling I2C can be found [here](https://www.raspberrypi-spy.co.uk/2014/11/enabling-the-i2c-interface-on-the-raspberry-pi/).

Create the folder to be shared on the network:

    mkdir -m 777 Desktop/images

Open the samba config file with the nano editor:

    sudo nano /etc/samba/smb.conf

Add the following text to the bottom of the smb.conf file:

    [images]
       comment= Pi Shared Image Folder
       path= /home/MassImageWriter/Desktop/images
       writeable=Yes
       create mask=0777
       directory mask=0777
       public=yes

Save and exit the config file with ```ctrl + S``` and ```ctrl + X```.

Setup the samba folder:

    sudo systemctl start smbd
    sudo smbpasswd -a MassImageWriter
    
You will be prompted to create a password for this user. Use the same password as the login password "MassImageWriter123"

    sudo systemctl restart smbd
    systemctl enable smbd

The enable command will prompt you to enter the user password a few times to authenticate.

You should be able to access this folder now over the network ([link for further instructions](https://pimylifeup.com/raspberry-pi-samba/)). 

To connect to your Samba on Windows, begin by opening up the “File Explorer“. Within the “File Explorer” click the “Computer” tab then click “Map network drive”. You will now be greeted by the dialog shown below asking you to enter some details.

Within the “Folder” textbox you will want to enter the following “\\raspberrypi\images“. If for any reason the connection fails, you can switch out “raspberrypi” with your Raspberry Pi’s local IP address (find this on the Pi using ```hostname -I```)

Once done, click the “Finish” button to finalize the connection.

Copy the "WriteImgSD.py" and "mass_image_writer.service" files into this folder and create a new folder called "compressedImages".

To setup this script to run on boot, add mass_image_writer.service to the /etc/systemd/system Folder. This file can be moved over from the files current directory by using:

    sudo mv Desktop/images/mass_image_writer.service /etc/systemd/system

Run the following commands to have this service run on boot:

    sudo systemctl daemon-reload
    
    sudo systemctl enable mass_image_writer.service
    
    sudo systemctl start mass_image_writer.service

When the last command is finished the LCD display should turn on and start the Mass Image Writer script. If you suspect an error has occured use the following command for troubleshooting:

    sudo systemctl status mass_image_writer.service

Thats it! reboot the system using the LCD display interface or with the command ```reboot```.

## References

- [dcfldd](https://dcfldd.sourceforge.net/)
- [Raspberry Pi config](https://www.raspberrypi.com/documentation/computers/configuration.html)
- [Core Electronics SD card](https://core-electronics.com.au/16gb-microsd-card-with-noobs-for-all-raspberry-pi-boards.html)
- [Samba installation tutorial](https://pimylifeup.com/raspberry-pi-samba/)
- [Adafruit LCD Keypad](https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/python-usage)
- [Adafruit LCD Keypad required files](https://github.com/adafruit/Adafruit_CircuitPython_CharLCD/blob/main/adafruit_character_lcd/character_lcd_rgb_i2c.py)
- [Previous Mass Image Writer Project](https://github.com/CoreElectronics/rpi-mass-image-writer)
