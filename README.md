# Internet Voting System

**Author:** Charlie Hall (CH555)  
**Date of Submission:** May 1, 2025

## Demo Videos
As this is a more abstract and hader to test system with multiple interacting components, I’ve created a set of demo videos to help illustrate key functionalities. Full running instructions and instructions to recreate the demo are found in `/P2P-Server/Node/README.md`.

**Voting Procedure and Setup**: (https://youtu.be/jHIvQARsmWs) <- not mentioned in the video the venv requires python installed.\
**Validator Delegation**: (https://youtu.be/HI7ED-iMmp4) \
**Blockchain Syncing** : (https://youtu.be/-iLHE2zwnvc) \
**Lead Validator Reassingment**: (https://youtu.be/gdjAVq_YR0o) <- Shows the mitigation for the single point of failure.


**NFC Companion App**: (https://youtube.com/shorts/FZLyiiy-5tM?feature=share)\


## Repository Overview

This repository contains the source files for the two primary software components of the Internet Voting System:

- **Desktop Client:**
  - Location: `/P2P-Server/Node`

- **Mobile Application:**
  - Location: `/NFCScannerApp`

## Directory Structure

```
Internet Voting System/
├── NFCScannerApp/
│   └── [Mobile application source files] <- Android Studio Project
├── P2P-Server/
│    └── Node/
│       └── [Desktop client source files]
└─── NFCScanner.apk
```

## Mobile Application

_Note : The mobile app forms an optional usability feature for the desktop client; however, the desktop client can still function without the app._

### Requirements
- Android mobile device or emulator
- Target API level: 31
- Minimum API level: 24
- Device must have:
    - NFC scanner
    - Camera

### Running Instructions

- Either Download ```NFCScanner.apk``` onto a device that meets the requirements.
- Or launch Android Studio with the NFCScannerApp project and launch from there to an emulator or device meeting the requirements. 

### Access source code

You can access the source code by opening the /NFCScannerApp folder as the project root in Android Studio.

**Troubleshooting!** : For the mobile app to connect to the desktop client it must be on the same network.

## Desktop Client

### Requirements
- Python 3.12.6
- Windows OS
- Dependencies \w Versions -> See requirements.txt

### Running Instructions

For running instructions see `/P2P-Server/Node/README.md`.

### Access source code

The source code can be accessed using any IDE by opening `/P2P-Server/Node` as the project root. Visual Studio Code is recommended, as it was used during development, but any IDE should work.



