# Node
**Author:** Charlie Hall (CH555)\
**Date of Submission:** May 1, 2025 

_Note: See Contents.md in this directory for a run down of files._ 

_Note: See the main README.md under the root directory to see a set of demo videos._ 

### Development Environment
- Python 3.12.6
- Windows 11
- Dependencies \w Versions -> See requirements.txt

The application wasn't tested on any operating systems or versions of Python other than those listed above. I believe it would work, but to guarantee compatibility when running from .py, I recommended using a Python version and requirements, including the versions listed.

# Running Instructions

## Option 1: Use the launch.bat with virtual environment

Use the `launch.bat`, which uses a virtual environment to install dependencies and ensure version compatibility.

This method still requires a Python version of 3.12.6 or higher for best compatibility.

## Option 2: Run from Source

Ensure you have Python installed on the system and that the dependencies are installed correctly.

You can install the dependencies using the requirments.txt in this directory using;

```
pip install -r requirements.txt
```

Alternatively, run the application directly from the source using Python:

```bash
python main.py
```
# Full Usage Instructions

## Start a network with a bootstrap node.
Instructions to launch a network as the bootstrap node:
- Launch the app.
- Select Create Election Server.
- Choose an unused port.

## Connect to a network's bootstrap node.
Instructions to launch a node and join a network through a bootstrap node:

- Launch the app.
- Select Join Election Server.
- Input the target host: if running on the same local network, use `127.0.0.1`; otherwise, you use the IPV4 address of the network.
- Input the target port that was used to launch the Bootstrap node for the network.
- Choose an unused port for the Node Port; this is the port the new node will launch on.

## Add candidates
Instructions to add a candidate to the blockchain.
- On the lead validator:
- Select "Advanced Options" -> "Add Candidate".
- Input the name of the candidate and submit.
- When a new block is posted, the candidate will be shown on future ballots and shown on the "View Candidates" Option

**This step only needs to be completed once on the network on the lead validator, and then it will propergate to all nodes.**

## Load Electors
Instructions to load electors to the blockchain.
- On the lead validator:
- Select "Advanced Options" -> "Load Electors".
- There is already an electors.json file to use in the directory a new one can be generated with `generate_electors.py`
- Electors will be loaded and should display in the terminal.

**This step only needs to be completed once on the network on the lead validator, and then it will propergate to all nodes.**

## Election setup on a validator node.
To setup a network ready for election:
- Create a network with a bootstrap node.
- Load electors.
- Add candidates.

## Voting

- Once the election setup has been done on the network:
- connect using a normal node:
- select "Cast Vote"
- use load from file to load credentials to load elector credentials; the load from mobile can be used with an NFC and the mobile companion app to send the credentials to the desktop client.
- Select a candidate from the drop-down.
- Submit the ballot
- The client will display an alert when the vote is detected on a blockchain block.

## View Node Directory
- Select "Advanced Options" -> "Node Directory".
- Nodes will be displayed in the node directory.

## View Blockchain
- Select "Advanced Options" -> "Node Directory".
- Blocks will be displayed in order in pages of 10.
- Each block can be selected to show list of transactions in each block
- Transcations can also be viewed to see the data of the transaction.

# Terminal Help

Use `help` command on termianl to see a list of all commands.

# Running Tests
## Unit testing

Run `python -m unittest discover -p "*_test.py"` in `testing\unit` from terminal for all unit tests.

## Intergration Testing
**Note the tests take quite a long time to run**

Run `python runner.py` in `testing\intergration` from terminal for all intergration tests.

Or run `python runner.py --test-name <TEST-NAME-HERE>` for a specific named test.

# Generate Electors Script

`generate_electors.py` is a small Python script that allows you to create a set of electors for testing and development purposes.

To run the script, use the following command:

```bash
python generate_electors.py
``` 

You can indicate the number of electors that are generated and this will be output to `electors.json`.

Use the `launch.bat`, which uses a virtual environment to install dependencies and ensure compatibility.
