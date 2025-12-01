# kaggle-google-capstone
Kaggle Gemini Goole AI workshop capstone project
This project contains the core logic for Agent Nifty, a multi-agent system designed to analyse nifty NSE index using APIs provided by exchange. The agent is built using Google Agent Development Kit (ADK) and follows a modular architecture.

There are three aspects. One agent analyses the index data pulled from exchange api. The second pulls the investment flow in and out of exchange index and the third provides the latest financial headlines. A parallel agent then aggregates and summarizes with a prediction brief for the next trading day.

It's a multi agent, with two apis fetching data from stock exchange with parallel and Sequential agent to aggregate and summarize
Just run the script niftyagent.py ( tested on python 3.12)

