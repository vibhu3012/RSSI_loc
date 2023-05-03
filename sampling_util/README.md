**Readme file to record the offline fingerprint data for radio map.**

To access the rssi capturing module we need to access the `./recorder.py` file in the `sampling_util/` folder of the main RSSI_LOC repo.

**STEP 1:**

- To start the program, one can directly open the repo in any code editor like virtual studio code and click the run button on the `./recorder.py` file 

OR 

- One can go to the terminal and after opening the `sampling_util/` folder using cd commands, execute 

    - `python3 recorder.py`

 *Note: You might need to install Python3 and pip3 to continue* 

**STEP 2:**

The program executes now and requests user to input the room, exact location within the room, and the orientation which is either North, East, West, South
```
which room you are at : A2
what is your current location : 1
[normal mode] start collecting sample#1.
Please Face North! Press Enter To Continue
Password:
```
#### *NOTE: After confirming the orientation, you might need to enter the password of your device once.*

```
// ADD THE TERMINAL OUTPUT AND HOW THINGS LOOK
```

- This starts the rssi gathering using the Airport utility of MacOS, and dumps the triad consisting of the orientation, fingerprint, and timestamp to a json file that is created in the `sampling_util/` folder.

- This json file can be used to create the radio map which will be used in the other programs to get the exact location of the user.

- Follow the prompts on the terminal, and continue for all the orientations. 

This completes the offline data collection for *one reference point*.

**At the time of data collection one should be sure of the areas which want to add to the offline data radio map and accordingly name the room number and location.**

*You can continue for the next location or Ctrl^C to end.*

