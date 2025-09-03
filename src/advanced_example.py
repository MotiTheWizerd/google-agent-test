"""Advanced example demonstrating different agent types and workflows."""

import asyncio
import os
from dotenv import load_dotenv

# Add src to Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager
from modules.core.workflow_builder import WorkflowBuilder


# Load environment variables
load_dotenv()


def get_stock_price(symbol: str) -> str:
    """Mock tool to get stock price."""
    prices = {
        "AAPL": "$192.55",
        "GOOGL": "$165.73",
        "MSFT": "$342.53",
        "TSLA": "$248.22"
    }
    return f"The current price of {symbol} is {prices.get(symbol, 'Unknown')}"


def get_news_sentiment(topic: str) -> str:
    """Mock tool to get news sentiment."""
    sentiments = {
        "technology": "positive",
        "economy": "mixed",
        "politics": "negative"
    }
    return f"The current sentiment for {topic} is {sentiments.get(topic.lower(), 'neutral')}"


def calculate_portfolio_risk(portfolio: str) -> str:
    """Mock tool to calculate portfolio risk."""
    return f"Portfolio risk assessment for '{portfolio}': Moderate risk with potential for 8-12% annual returns"


async def main():
    """Main advanced example function."""
    # Create agents manager
    manager = AgentsManager(app_name="advanced_example_app")
    
    # Register tools
    manager.register_tool("get_stock_price", get_stock_price)
    manager.register_tool("get_news_sentiment", get_news_sentiment)
    manager.register_tool("calculate_portfolio_risk", calculate_portfolio_risk)
    
    # Create a financial analysis workflow
    builder = manager.create_workflow_builder("financial_analysis")
    builder.set_description("Comprehensive financial analysis workflow")
    
    # Add a stock research agent
    builder.add_llm_agent(
        name="stock_researcher",
        model="gemini-2.0-flash",
        instruction="You are a financial analyst. Use the get_stock_price tool to research stock prices. Focus on technology stocks. Save your findings in the session state under 'stock_data'.",
        tools=["get_stock_price"],
        output_key="stock_data"
    )
    
    # Add a sentiment analysis agent
    builder.add_llm_agent(
        name="sentiment_analyst",
        model="gemini-2.0-flash",
        instruction="You are a market sentiment analyst. Use the get_news_sentiment tool to analyze market sentiment for technology sector. Save your findings in the session state under 'market_sentiment'.",
        tools=["get_news_sentiment"],
        output_key="market_sentiment"
    )
    
    # Add a risk assessment agent
    builder.add_llm_agent(
        name="risk_assessor",
        model="gemini-2.0-flash",
        instruction="You are a risk assessment specialist. Use the calculate_portfolio_risk tool to evaluate portfolio risk. Save your findings in the session state under 'risk_assessment'.",
        tools=["calculate_portfolio_risk"],
        output_key="risk_assessment"
    )
    
    # Add a parallel agent to gather data simultaneously
    builder.add_parallel_agent(
        name="data_collector",
        sub_agents=["stock_researcher", "sentiment_analyst", "risk_assessor"]
    )
    
    # Add a summary agent
    builder.add_llm_agent(
        name="financial_analyst",
        model="gemini-2.0-flash",
        instruction="You are a senior financial analyst. Synthesize the stock data, market sentiment, and risk assessment to provide a comprehensive financial analysis. Be concise but thorough."
    )
    
    # Add a sequential agent to orchestrate the flow
    builder.add_sequential_agent(
        name="financial_analysis_orchestrator",
        sub_agents=["data_collector", "financial_analyst"]
    )
    
    # Set entry point and build
    workflow = builder.set_entry_point("financial_analysis_orchestrator").build()
    
    # Register the workflow
    manager.register_workflow(workflow)
    
    # Print workflow info
    manager.print_workflow_info("financial_analysis")
    
    # Run the workflow
    portfolio = "technology stocks including Apple, Google, and Microsoft"
    try:
        result = await manager.run_workflow(
            workflow_name="financial_analysis", 
            input_text=f"Analyze this portfolio: {portfolio}",
            user_id="analyst_001",
            session_id="analysis_session_001"
        )
        print("\nWorkflow completed successfully!")
    except Exception as e:
        print(f"Error running workflow: {e}")


if __name__ == "__main__":
    print("🚀 Starting Advanced Agents Manager Example 🚀")
    asyncio.run(main())
    print("\n✅ Advanced example completed!")