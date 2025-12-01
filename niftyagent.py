import os
import pdb
#from kaggle_secrets import UserSecretsClient
from niftytools import Nifty50Tracker
from google.adk.tools.google_search_tool import google_search
from google.adk.plugins.logging_plugin import ( LoggingPlugin,)  
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent

import asyncio

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search, AgentTool, ToolContext
from google.adk.code_executors import BuiltInCodeExecutor

import matplotlib.pyplot as plt
import io
from contextlib import redirect_stdout
import asyncio

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter.scrolledtext import ScrolledText
import io
from contextlib import redirect_stdout
import asyncio
import threading

print("✅ ADK components imported successfully.")

class NiftyAgent:
    def __init__(self):
        try:
            GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
            print("✅ Gemini API key and News API setup complete.")
            self.retry_config=types.HttpRetryOptions(
                attempts=5,  # Maximum retry attempts
                exp_base=7,  # Delay multiplier
                initial_delay=1, # Initial delay before first retry (in seconds)
                http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
            )
        except Exception as e:
            print(
                f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to your secrets. Details: {e}"
            )

    def prediction_agent(self):
            self.google_search_agent = Agent(
                name="google_search_agent",
                model=Gemini(
                    model="gemini-2.5-flash-lite",
                    retry_options=self.retry_config
                ),
                description="A simple agent that can answer general questions.",
                instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
                tools=[google_search],
                output_key = "finance_news",
            )
            self.tracker = Nifty50Tracker()
            #print(tracker.display())
            self.nifty_analysis_agent = LlmAgent(
                name="nifty_analysis_agent",
                model=Gemini(model="gemini-2.5-flash-lite", retry_options=self.retry_config),
                instruction="""You are a helpful assistant specialized in providing financial analysis and news.
                1. use the `tracker.index_data` tool to fetch the latest trading data dictionary string of NSE Nifty 50 index and analyse what stocks added and declined and contributed to index nifty 50 with a smart brief.
                2. to fetch latest financial news on index Nifty 50 for tomorrow use the 'google_search_agent'.""",
                tools = [self.tracker.index_data,AgentTool(agent=self.google_search_agent)],
                output_key = "nifty_analysis",
#code_executor=BuiltInCodeExecutor(),
            )
            self.nifty_flow_agent = LlmAgent(
                name="nifty_flow_agent",
                model=Gemini(model="gemini-2.5-flash-lite", retry_options=self.retry_config),
                instruction="""You are a helpful assistant specialized in providing market flow data.
                1. use the 'tracker.fiidii_flow' tool to fetch fii and dii inflow and outflow to and from nifty 50 index.""",
                tools = [self.tracker.fiidii_flow],
                output_key = "nifty_flow",
                )

            self.aggregator_agent = Agent(
                name="AggregatorAgent",
                model=Gemini(
                    model="gemini-2.5-flash-lite",
                    retry_options=self.retry_config
                ),
                # It uses placeholders to inject the outputs from the parallel agents, which are now in the session state.
                instruction="""Combine these two  into a single executive summary:

                **Nifty Analysis:**
                {nifty_analysis}
                
                **Nifty FII DII Flow:**
                {nifty_flow}
                
                Your summary should highlight common themes, surprising connections, and the most important key takeaways from all three reports. The final summary should be around 200 words.""",
                output_key="executive_summary",  # This will be the final output of the entire system.
            )

            print("✅ aggregator_agent created.")

# The ParallelAgent runs all its sub-agents simultaneously.
            self.parallel_research_team = ParallelAgent(
                name="ParallelResearchTeam",
                sub_agents=[self.nifty_analysis_agent, self.nifty_flow_agent],
            )

# This SequentialAgent defines the high-level workflow: run the parallel team first, then run the aggregator.
            self.root_agent = SequentialAgent(
                name="ResearchSystem",
                sub_agents=[self.parallel_research_team, self.aggregator_agent],
            )

            print("✅ Parallel and Sequential Agents created.")
            print("✅ Root Agent defined.")
            #runner = InMemoryRunner(agent=root_agent)
            print("✅ Runner created.")
            self.runner = InMemoryRunner(agent=self.root_agent,plugins=[LoggingPlugin()],)

# --- 1. Function to capture output (from previous response) ---
    async def capture_output_and_run(self):
        self.prediction_agent()
        #query = input("Enter query:")
        query = "analyse stocks and fetch latest fii dii flow and financial headlines for indian market"
        #response = await runner.run_debug(query + str(Nifty50Tracker().display()))
        f = io.StringIO()
        with redirect_stdout(f):
            await self.runner.run_debug(query)
        output = f.getvalue()
        return output
        #pdb.set_trace()
        #response = await runner.run_debug("What's the weather and pollution in Delhi?")
        #print(response[0].content.parts[0].text)

# Note: Replace 'self.runner' with the actual runner object.
# Define the 'main', 'capture_output_and_run', and 'display_on_matplotlib'
# methods within a class structure or as standalone functions with appropriate arguments.
# --- 2. Function to display content using Tkinter ---

    def display_gui(self,output_string):
        """
        Creates a scrollable Tkinter GUI window to display a string output.
        """
        root = tk.Tk()
        root.title("Gemini Runner Output Display")
        root.geometry("800x600")

        # Create a ScrolledText widget for automatic scrolling and text wrapping
        output_text_widget = ScrolledText(root, wrap=tk.WORD, state=tk.NORMAL, bg="white", font=("Consolas", 10), padx=5, pady=5)
        output_text_widget.pack(expand=True, fill=tk.BOTH)

        # Insert the fetched output string
        output_text_widget.insert(tk.END, output_string)
        
        # Disable editing by the user
        output_text_widget.configure(state=tk.DISABLED)

        # Start the Tkinter event loop
        root.mainloop()
# --- 3. Execution function (needs your runner object) ---

    def run_integration(self):
        # We need to run the async capture function in a separate thread
        # because Tkinter runs in its own main loop.
        async def async_wrapper():
            captured_text = await self.capture_output_and_run()
            # Pass the captured text to the GUI display function
            # This function must be called from the main thread if needed,
            # but here we start the GUI after the capture is done.
            self.display_gui(captured_text)

        # Use asyncio to run the async part
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_wrapper())
        loop.close()

# --- Example Usage (How to call this in your script) ---


# Example call:
if __name__ == "__main__":
    NiftyAgent().run_integration()

"""
if __name__ == "__main__":
    asyncio.run(NiftyAgent().main())
"""
