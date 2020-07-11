# Instrumentality Blockchain API

This project aims to provide an API on top of Hyperledger Iroha to implement a network where developers can build a trustworthy profile of their skills.

In a nutshell, we want to provide a system so that when you complete tasks in Instrumentality, your skill level is tracked and updated, 
in the end providing the future employers with a bigger picture of your skillset and skill levels.

## Bringing up the node

---

**NOTE: Please be aware that the sha-3 keys provided in the `iroha` folder are just for testing purposes. Do not use them when setting up an Instrumentality node.**

**NOTE: Remember that setting up a node doesn't mean you are part of the network. Since we want to create a safe environment for business practices, the Instrumentality network is not public.**
**All companies wishing to run a node must contact us in order to be added to the network. While all the nodes are the same, ony our account has the permission to add peers.**
**In the future we may come up with better ways to verify if a company wanting to join the network is legitimate or not.**

---

### Requirements

- Docker
- docker-compose
- Python 3

### Follow the next steps if you just need to test the API:

1. Clone the repository: `git clone https://gitlab.com/instrumentality-foundation/instrumentality-blockchain-api.git && cd instrumentality-blockchain-api`
2. `docker-compose -f docker-compose.yaml up` to bring up the node
3. run `python app.py` to start the API server