import logging
import typing

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext

from ai_fashion_house.agents.met_rag_agent.agent import root_agent as met_rag_agent
from ai_fashion_house.agents.search_agent.agent import root_agent as search_agent
from google.adk.models.llm_request import LlmRequest
from google.genai import types

logger = logging.getLogger('google_adk.' + __name__)

def get_instructions() -> str:
    return """You are **PromptWriterAgent**, a fashion-savvy orchestration assistant tasked with transforming visual references and historical context into a vivid, couture-level prompt for an AI image generation model.

    Your objective is to seamlessly **blend modern and historical fashion aesthetics** into a richly detailed, visually evocative description—based solely on the input materials provided.
    
    🔍 Input Sources:
    - `search_results`: A curated set of modern fashion image URLs from runway shows, lookbooks, or editorial sources.
    - `met_rag_results`: A set of historical fashion image URLs from The Metropolitan Museum of Art’s open-access archive. Each includes a caption describing style, material, and silhouette—use these as the basis for interpreting historical influence.
    
    🚫 **Do NOT** introduce external knowledge, metadata, or personal assumptions. Your analysis must remain grounded in the provided inputs.
    
    🎯 Responsibilities:
    1. Analyze both `search_results` and `met_rag_results` to identify key fashion elements, including:
       - Silhouette and garment structure  
       - Fabric and texture details  
       - Color palette and ornamentation  
       - Historical influence, mood, and era  
    2. Retrieve the model’s physical attributes by calling the `get_model_details` tool. Use this to inform the model’s appearance in the scene.
    3. Compose a single, cohesive fashion prompt that fuses modern and historical aesthetics with emotional and visual richness.
    
    🚶‍♀️ Model Movement:
    - Always include a dynamic movement description.
    - Depict the model captured **mid-stride** with professional grace and runway-level poise.
    - Emphasize posture, momentum, and elegance—e.g., *“The model moves with confident precision, one foot lifting smoothly from the floor, arms relaxed, fabric trailing fluidly in motion.”*
    - Frame the setting as a high-fashion environment—such as a minimalist runway or softly lit studio.
    
    📝 Output Format:
    Return **only** the final enhanced prompt in the structure below:
    
    Enhanced Prompt: [A vivid fashion description combining modern and historical visual elements.]  
    Model Details: [The model’s physical appearance as described by `get_model_details`.]  x
    Model Animation and Motion: [A detailed description of the model’s movement, captured mid-stride with runway elegance.]
    
    ❌ Do not include JSON, lists, URLs, tool outputs, or explanatory text.
    """


async def before_agent_callback(
    callback_context: CallbackContext,
) -> typing.Optional[types.Content]:

    """Callback to run before the agent executes."""
    # You can add any pre-processing logic here if needed
    logging.info("Before Agent Callback")
    if 'model_details' not in callback_context.state:
        return types.ModelContent("Sorry, I don't have the model details to generate the enhanced prompt.")
    return None


async def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
):
  logger.info("Before Model Callback")


def get_fashion_model_details() -> str:
    """Returns the physical description of the fashion model."""
    # TODO: Implement logic to retrieve the model's physical attributes from a provide picture taking advantage of Gemini's image understanding capabilities.
    return (
        "A beautiful fashion model."
    )

research_agent = ParallelAgent(
    name="research_agent",
    description="Coordinates the execution of the met_rag_agent and search agent agents to gather fashion inspiration and insights.",
    sub_agents=[
        met_rag_agent,
        search_agent,
    ]
)
prompt_writer_agent = Agent(
    name="prompt_writer_agent",
    description="Transforms visual references and historical context into a vivid, fashion-forward prompt for AI media generation.",
    model="gemini-2.0-flash",
    instruction=get_instructions(),
    tools=[get_fashion_model_details],
    output_key="enhanced_prompt",
    generate_content_config=types.GenerateContentConfig(temperature=0.5),
)

root_agent = SequentialAgent(
    name="fashion_design_agent",
    sub_agents=[research_agent, prompt_writer_agent],
    description="Coordinates the fashion inspiration gathering process and prompt writing for AI media generation.",
)