# Project Progress Log

**Author**: Charlie Hall (ch555)
**Date**: 1st May 2025

## Preliminary Stage

### Week 7th–13th October
#### **Overview**
- **Logistics**  
  - Completed project proposal submission form.  
  - Held the first meeting with the supervisor.  

- **Research**  
  - Investigated key properties of an internet voting system.  
  - Explored methods for maintaining voter anonymity, such as zero-knowledge proofs.  
  - Investigated the use of blockchain for transparency and trust in voting systems.  

- **Initial Report**  
  - Began listing software components along with their functional and non-functional requirements.  

#### **Next Week Goals**
- Design a preliminary system mock-up in diagram form.  
- Decide which characteristics of a voting system to focus on for the final product.  

---

### Week 14th–20th October
#### **Overview**
- **Decisions**  
  - Decided to focus on implementing a transparent voting system.  

- **Initial Report**  
  - Started writing the literature survey and defining system requirements.  

#### **Next Week Goals**
- Hold a meeting with the supervisor.  

---

### Week 21st–28th October
#### **Overview**
- **Progress**  
  - Began breaking down key software components and defining their functions.  
  - Added, formatted, and summarized information sources for the report.  
  - Held a meeting with the supervisor to discuss progress.  

#### **Next Week Goals**
- Continue working on the interim report.  

---

### Week 28th October–18th November
#### **Overview**
- **Interim Report**  
  - Completed the interim report.  
  - Developed a Gantt chart to plan the software development timeline.  
  - Finalized a basic outline of software components, including UML diagrams.  

#### **Next Week Goals**
- Start implementing the initial stage of software, focusing on core class implementation as per the Gantt chart.  

---

### Week 18th–25th November
#### **Overview**
- **Progress**  
  - Completed the interim report (final checks).  
  - Began setting up the technical stack.  

#### **Next Week Goals**
- Begin class implementation for the software.  

---

## Development Stage

### Week 25th November - 2nd December

#### Review of targets for the week
-  [x] Begin class implementation for the software.
#### **Overview**
- Setup Springboot project with required dependencies.
- Implemented Model class for users.
- Implemented Repository & Service layers for manipulating User model class.
- Implemented API endpoints; /register and /login to create and return user cookie respectively.
#### **Next Week Goals**
- Implement an election Model class and associated Repo and Service layer for manipulation of this class.
- Implement an Administrator role for creating elections.

---

### Week 2nd December - 9th December

#### Review of targets for the week
- [x] Implement an election Model class and associated Repo and Service layer for manipulation of this class.
- [ ] Implement an Administrator role for creating elections. -_this task is still outstanding and will be carried forward to next week_
#### **Overview**
- Implemented Model class for elections
- Implemented Controller class for elections 
- Implemented Repository & Basic Service layer for creating election and giving a user access to an election.

#### **Next Week Goals**
- Finish implementing Administrator role
- Work on a basic front-end interface for testing purposes
- Implement all endpoints as listed on the planning document in interim report

### Weeks - 9th December - 23rd December

#### Review of targets for the week
- [ ] Finish implementing Administrator role
- [ ] Work on a basic front-end interface for testing purposes
- [ ] Implement all endpoints as listed on the planning document in interim report
#### **Overview**
- Progress was slow over this period.
- Most development time spent experimenting with a peer-to-peer server implementation.
- For now the development on the Springboot side will be slowed because the project is in early stages of development I want to take this opputinity to experiment more.
#### **Next Week Goals**
- Keep working on p2p server 

---

### Weeks - 23rd December - 30th December

#### **Overview**
- Over the last weeks project development has slowed due to the realisation that the project I was on track to develop was not much more than a simple CRUD app with a small touch of centralized blockchain. To make this project more challenging I've made the project division to expand the aims of this project. The new aim will be to implement a decentralized blockchain system for the election system.

- Implemented a peer to peer server with gossip protocol.

Future Goals for the blockchain:

- The blockchain will be used by the election servers not the users themselves.
- The blockchain will use a proof of authority consensus control using round robin time quantisation.
- Observers will be able to connect to the blockchain for auditing purposes.

#### **Next Week Goals**
- Add blockchain implementation to peer to peer server.

### Weeks 30th December - 20th January

#### **Overview**

In these weeks the initial groundwork for a peer-2-peer network was laid.

##### Features added:
- Terminal interface
- Logging
- Peer Discovery via gossip protocal 
- Improved connection protocal for nodes (connections will be rejected if too many connections running with suggestions of nodes that are known to have space)
- Implementation of blockchain classes to store local state.

##### Features planned for following week:
- Add ability to add validators to the blockchain.

### Weeks 20th January - 27th January

#### **Overview**

##### Features added:
- Improved message formatting so all messages will have same format in a json
- Added public/private keys for all nodes
- Added verification for message signatures.

##### Features planned for following week:
- Include initial handshake for excahnging public keys at the start.

### Weeks 27th January - 7th February

#### **Overview**
These weeks were very development heavy, and the features that were planned were implemented plus alot more.

##### Features added:
- An initial handshake procedure for excahnging public-keys was implemented, specifically the approach implemented uses encryption to secure the initial join request to establish a secure connection.
- blockchain snapshot class was added, this class will be used by normal nodes to get the blockchain state without the need to download the whole chain.
- Support for direct messaging to non connected nodes has been implemented using temporary connections.
- TTL broadcasting was implemented, this will be used to propergate important information to all nodes in the blockchain.
- blockchain serialization methods have been implemented in preperation for blockchain syncronisation.
- Some utilitiy commands for the terminal were implemented to complement the features added.

##### Features planned for following week:
- Add blockchain syncronisation and proposal in a single validator enviroment.

Outside of development also began preperation for the initial interview.

### Weeks 7th February - 17th February
- Add blockchain state snapshot.
- Added test blockchain transactions.
- Blocks are syncronised with all nodes on the network with a single validator.
- Created a simple testing framework.
- Spent some time refactoring code for organisation.

### Gap In Project Development

During these two weeks I really struggled with motivation for my project and was also really ill so not much work was completed.


### Weeks 10th March - 17th March
- add a electoral role system of public_keys and private_keys for each elector 
- add an elector_snapshot datastructure, this will complement the normal snapshot datastructure but will allow for faster look up of elector state (if an elector has voted or not).
- add a system to suggest alternative nodes to connect to if the initial connected node is full.
- add a heartbeat system that will be broadcasted by all nodes so validators can keep track of what nodes are alive and also keep track of their ip and port for connection suggestions.
- add ability to add candidates for the election
- add an initial vote system so nodes can propose votes

##### Features planned for following week:
- start work on an front end gui.

### Weeks 17th March - 24th March
- add front end index page.
- add connect and host page.
- add blockchain viewer page.
- add an event system for server_events to connect events to ui actions.

##### Features planned for following week:
- start work on an front end gui.

### Weeks 24th March - 31 March
#### Features
- fixed issue with command runner (syntax error)
- updated message codes to use enum instead of a dict
- add a intergration testing system and wrote first initial test.
- add a node connection recommendation.
- add ui event handling

### Weeks 31 March - 7 April
#### Features
- Add vote handling for validators
- Add vote proposal for nodes.
- Add first server creation intergration test.

### Weeks 7th April - 14th April
#### Features
- Add UI -> Server communication
- Add HTTP Server.
- Add NFCScannerApp intital setup
- Change vote crednetials to use ecdsa keys.
- Add linking between mobile and desktip app.

### Weeks 14th April - 21st April
#### Features
- Fixed issue with blockchain sync.
- Add submit vote button and make it functional.
- add vote tally page.
- add add_validator command

### Weeks 21st April - 2nd
#### Features
- Polishing code
- Finishing report




