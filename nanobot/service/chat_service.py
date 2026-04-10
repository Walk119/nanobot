"""Chat service for handling agent chat requests."""
from typing import Optional, Dict, Any
import asyncio
from nanobot.agent.loop import AgentLoop
from nanobot.bus.queue import MessageBus
from nanobot.cron.service import CronService
from nanobot.cli.commands import _load_runtime_config, _make_provider, is_default_workspace, _migrate_cron_store


class ChatService:
    """Service for handling chat requests with the agent."""
    
    def __init__(self, config_path: Optional[str] = None, workspace: Optional[str] = None):
        """Initialize the ChatService.
        
        Args:
            config_path: Path to config file
            workspace: Path to workspace directory
        """
        self.config_path = config_path
        self.workspace = workspace
        self.agent_loop: Optional[AgentLoop] = None
    
    async def initialize(self):
        """Initialize the agent loop."""
        # Load configuration
        runtime_config = _load_runtime_config(self.config_path, self.workspace)
        
        # Create necessary services
        bus = MessageBus()
        provider = _make_provider(runtime_config)
        
        # Migrate cron store if needed
        if is_default_workspace(runtime_config.workspace_path):
            _migrate_cron_store(runtime_config)
        
        # Create cron service
        cron_store_path = runtime_config.workspace_path / "cron" / "jobs.json"
        cron = CronService(cron_store_path)
        
        # Initialize agent loop
        self.agent_loop = AgentLoop(
            bus=bus,
            provider=provider,
            workspace=runtime_config.workspace_path,
            model=runtime_config.agents.defaults.model,
            max_iterations=runtime_config.agents.defaults.max_tool_iterations,
            context_window_tokens=runtime_config.agents.defaults.context_window_tokens,
            web_config=runtime_config.tools.web,
            context_block_limit=runtime_config.agents.defaults.context_block_limit,
            max_tool_result_chars=runtime_config.agents.defaults.max_tool_result_chars,
            provider_retry_mode=runtime_config.agents.defaults.provider_retry_mode,
            exec_config=runtime_config.tools.exec,
            cron_service=cron,
            restrict_to_workspace=runtime_config.tools.restrict_to_workspace,
            mcp_servers=runtime_config.tools.mcp_servers,
            channels_config=runtime_config.channels,
            timezone=runtime_config.agents.defaults.timezone,
            unified_session=runtime_config.agents.defaults.unified_session,
        )
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process a chat message.
        
        Args:
            message: Message to send to the agent
            session_id: Session ID
            
        Returns:
            Agent response
        """
        if not self.agent_loop:
            await self.initialize()
        
        # Process message directly
        response = await self.agent_loop.process_direct(
            message, session_id
        )
        
        # Return response
        return {
            'content': response.content if response else '',
            'metadata': response.metadata if response else None
        }
    
    async def close(self):
        """Close the agent loop."""
        if self.agent_loop:
            await self.agent_loop.close_mcp()
