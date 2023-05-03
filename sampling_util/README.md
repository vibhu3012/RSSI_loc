Readme file to record the offline fingerprint data for radio map.

To access the rssi module we need to access the 'recorder.py' file in the sampling_util folder of the main RSSI_LOC repo.

STEP 1:

To start the program, one can directly open the repo in any code editor like virtual studio code and click the run button on recorder.py file 

OR 

One can go to the terminal and after opening the sampling_util folder using cd commands, execute "python3 recorder.py"

NOTE: YOU MIGHT NEED TO INSTALL PYTHON3 OR PIP3 IN ORDER TO PROCEED

STEP 2:
The program executes now and requests user to input the room, exact location within the room, and the orientation which is either North, East, West, South
```
which room you are at : A2
what is your current location : 1
[normal mode] start collecting sample#1.
Please Face North! Press Enter To Continue
Password:
```
NOTE: After confirming the orientation, you might need to enter the password of your device once.

This starts the rssi gathering using the Airport utility of MacOS, and dumps the triad consisting of the bssid, fingerprint, and timestamp to a json file that is created in the main RSSI_LOC folder.

This json file can be used to create the radio map which will be used in the other programs to get the exact location of the user.

Follow the prompts on the terminal, and continue for all the orientations. 

This completes the offline data collection for one location.


YOU CAN CONTINUE FOR THE NEXT LOCATION OR CLICK CTRL^C TO END THE PROGRAM.


