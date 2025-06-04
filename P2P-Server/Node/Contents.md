# Python Files Summary Template
**Author**: Charlie Hall\
**Date:**: May 2025

## Summary of Python Files in Directory

### Directory Path
`root\P2PServer\Node`

### Python Files Overview
| File \ Directory Name       | Description/Functionality Summary |
|------------------|-----------------------------------|
| `main.py` | Application entry point. |
| `\blockchain` | All blockchain model classes are found in this directory, These classes are "pure" classes they dont have any network interaction, that is implemented through other classes |
| `server.py` | This the main blockchain server class that holds the server state|
| `\messaging` | The modules in this directory handles message processing for sending and also processes incoming messages. |
| `\ui` | All the userinterface classes are implemented |
| `\threads` | This directory stores the QThreads which are the threads that each software componenet run on. |
| `\handlers` | This directory stores component classes and modules that manipulat the server class. |