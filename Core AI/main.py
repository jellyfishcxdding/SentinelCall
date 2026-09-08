import asyncio
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, cartesia, silero

# 1. Define the Medical Agent (Specialist)
medical_agent = VoicePipelineAgent(
    vad=silero.VAD.load(),
    stt=deepgram.STT(),
    llm=openai.LLM.with_groq(model="llama-3.1-70b-versatile"),
    tts=cartesia.TTS(),
    system_prompt="You are a medical logging agent. Ask the user which pills they took, log it, and return to the main companion."
)

# 2. Define the Routing Tools
class TriageTools(llm.FunctionContext):
    @llm.ai_callable(description="Transfer the user to the Medical Specialist when they mention medication, pills, or feeling unwell.")
    async def transfer_to_medical(self):
        print("Executing sub-250ms handoff to Medical Agent...")
        # The string is spoken by the current agent right before the transfer happens
        return (medical_agent, "Let me get your medical log book right now.")

# 3. Define the Triage Agent (Primary)
async def entrypoint(ctx: JobContext):
    triage_agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM.with_groq(model="llama-3.1-70b-versatile"),
        tts=cartesia.TTS(),
        fnc_ctx=TriageTools(),
        system_prompt="You are Aura, a friendly companion. Chat warmly about their day. If they mention medicine, use your tool to transfer them."
    )
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    triage_agent.start(ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))