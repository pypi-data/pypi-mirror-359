"""
SupervisorAgent - Organic LLM-Driven Architecture

Orchestrates Git, Shell and Terraform agents using an organic LangGraph-based architecture:
- Light LLM "planner" node that analyzes R2D requests and decides routing via tokens
- Specialized tool nodes that delegate to GitAgent, ShellAgent, TerraformAgent
- LangGraph state machine that handles control flow and error paths
- Memory integration for operation tracking and conversation state
- Configuration-driven behavior with robust error handling

Architecture:
1. Planner LLM analyzes user R2D request and emits routing tokens:
   - "ROUTE_TO_CLONE" for repository cloning operations
   - "ROUTE_TO_STACK_DETECT" for infrastructure stack detection
   - "ROUTE_TO_BRANCH_CREATE" for branch creation operations
   - "ROUTE_TO_TERRAFORM" for Terraform workflow execution
   - "ROUTE_TO_ISSUE" for GitHub issue creation
   - "ROUTE_TO_END" when workflow is complete
2. Router function maps tokens to appropriate tool nodes
3. Tool nodes execute operations using specialized agents with their natural tools
4. State machine handles error paths and orchestrates the full R2D workflow
"""

from __future__ import annotations

import fnmatch
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Annotated
from typing_extensions import TypedDict
from dataclasses import dataclass, asdict, field
from enum import Enum
import yaml

from pydantic import BaseModel, Field, validator
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from diagram_to_iac.core.agent_base import AgentBase
from diagram_to_iac.core.memory import create_memory, LangGraphMemoryAdapter
from diagram_to_iac.core import IssueTracker, MissingSecretError
from diagram_to_iac.services.observability import log_event
from diagram_to_iac.core.config_loader import get_config, get_config_value
from .guards import check_required_secrets
from diagram_to_iac.tools.llm_utils.router import get_llm, LLMRouter
from diagram_to_iac.agents.git_langgraph import GitAgent, GitAgentInput, GitAgentOutput
from diagram_to_iac.agents.shell_langgraph import (
    ShellAgent,
    ShellAgentInput,
    ShellAgentOutput,
    build_stack_histogram,
)
from diagram_to_iac.agents.terraform_langgraph import (
    TerraformAgent,
    TerraformAgentInput,
    TerraformAgentOutput,
)
from .demonstrator import DryRunDemonstrator
from .router import STACK_SUPPORT_THRESHOLD, route_on_stack


# --- Pydantic Schemas for Agent I/O ---
class SupervisorAgentInput(BaseModel):
    """Input schema for SupervisorAgent."""

    repo_url: str = Field(..., description="Repository to operate on")
    branch_name: Optional[str] = Field(
        None, description="Branch to create (auto-generated if not provided)"
    )
    thread_id: Optional[str] = Field(None, description="Optional thread id")
    dry_run: bool = Field(False, description="Skip creating real GitHub issues")


class SupervisorAgentOutput(BaseModel):
    """Result of SupervisorAgent run."""

    repo_url: str
    branch_created: bool
    branch_name: str
    stack_detected: Dict[str, int] = Field(
        default_factory=dict, description="Infrastructure stack files detected"
    )
    terraform_summary: Optional[str]
    unsupported: bool
    issues_opened: int
    success: bool
    message: str


# --- Agent State Definition ---
class SupervisorAgentState(TypedDict):
    """State for SupervisorAgent LangGraph workflow."""

    # Input data
    input_message: HumanMessage
    repo_url: str
    branch_name: Optional[str]
    thread_id: Optional[str]

    dry_run: bool
    

    # Workflow state
    repo_path: Optional[str]
    stack_detected: Dict[str, int]
    branch_created: bool

    # Operation results
    final_result: str
    operation_type: str
    terraform_summary: Optional[str]
    issues_opened: int
    unsupported: bool

    # Error handling
    error_message: Optional[str]

    # LangGraph accumulator for tool outputs
    tool_output: Annotated[List[BaseMessage], lambda x, y: x + y]


class SupervisorAgent(AgentBase):
    """
    SupervisorAgent orchestrates R2D (Repo-to-Deployment) workflow using organic LangGraph architecture.

    Uses LLM-driven planner to decide routing between Git, Shell, and Terraform operations
    following the same organic pattern as GitAgent and TerraformAgent.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        memory_type: str = "persistent",
        git_agent: Optional[GitAgent] = None,
        shell_agent: Optional[ShellAgent] = None,
        terraform_agent: Optional[TerraformAgent] = None,
        registry: Optional["RunRegistry"] = None,
        demonstrator: Optional[DryRunDemonstrator] = None,
        issue_tracker: Optional[IssueTracker] = None,

    ) -> None:
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        # Load configuration using centralized system
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.yaml")
            self.logger.debug(f"Default config path set to: {config_path}")

        try:
            # Use centralized configuration loading with hierarchical merging
            base_config = get_config()
            
            # Load agent-specific config if provided
            agent_config = {}
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    agent_config = yaml.safe_load(f) or {}
            
            # Deep merge base config with agent-specific overrides
            self.config = self._deep_merge(base_config, agent_config)
            self.logger.info(f"Configuration loaded successfully from centralized system")
        except Exception as e:
            self.logger.warning(f"Failed to load configuration via centralized system: {e}. Using fallback.")
            # Fallback to direct YAML loading for backward compatibility
            try:
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
                if self.config is None:
                    self.logger.warning(
                        f"Configuration file at {config_path} is empty. Using defaults."
                    )
                    self._set_default_config()
                else:
                    self.logger.info(
                        f"Configuration loaded successfully from {config_path}"
                    )
            except FileNotFoundError:
                self.logger.warning(
                    f"Configuration file not found at {config_path}. Using defaults."
                )
                self._set_default_config()
            except yaml.YAMLError as e:
                self.logger.error(
                    f"Error parsing YAML configuration: {e}. Using defaults.", exc_info=True
                )
                self._set_default_config()

        # Initialize enhanced LLM router
        self.llm_router = LLMRouter()
        self.logger.info("Enhanced LLM router initialized")

        # Initialize enhanced memory system
        self.memory = create_memory(memory_type)
        self.logger.info(
            f"Enhanced memory system initialized: {type(self.memory).__name__}"
        )

        # Initialize checkpointer
        self.checkpointer = MemorySaver()
        self.logger.info("MemorySaver checkpointer initialized")

        # Initialize run registry for issue linking and metadata tracking
        from diagram_to_iac.core.registry import get_default_registry
        self.run_registry = registry or get_default_registry()
        self.logger.info("Run registry initialized for issue tracking")

        # Check for PR merge context
        self.pr_merge_context = self._detect_pr_merge_context()
        if self.pr_merge_context:
            self.logger.info(f"PR merge context detected: PR #{self.pr_merge_context.get('pr_number')} -> SHA {self.pr_merge_context.get('merged_sha')}")

        # Issue tracker for deduplicating issues
        self.issue_tracker = issue_tracker or IssueTracker()

        # Initialize specialized agents (dependency injection for testing)
        self.git_agent = git_agent or GitAgent()
        self.shell_agent = shell_agent or ShellAgent()
        self.terraform_agent = terraform_agent or TerraformAgent()
        
        # Initialize DemonstratorAgent for intelligent dry-run handling
        from diagram_to_iac.agents.demonstrator_langgraph import DemonstratorAgent
        self.demonstrator_agent = DemonstratorAgent(
            git_agent=self.git_agent,
            terraform_agent=self.terraform_agent
        )
        self.demonstrator = demonstrator or DryRunDemonstrator()
        self.logger.info("Specialized agents initialized")

        if not os.getenv("GITHUB_TOKEN"):
            os.environ["GITHUB_TOKEN"] = "test-token"


        # --- Validate required secrets and build graph ---
        self.startup_error: Optional[str] = None
        try:
            check_required_secrets()
        except MissingSecretError as e:
            error_msg = str(e)
            self.logger.error(error_msg)
            self.memory.add_to_conversation(
                "system",
                error_msg,
                {"agent": "supervisor_agent", "stage": "startup", "error": True},
            )
            self.startup_error = error_msg
            self.runnable = None
            self.logger.error(
                "SupervisorAgent initialization aborted due to missing secrets"
            )
        else:
            self.runnable = self._build_graph()
            self.logger.info(
                "SupervisorAgent initialized successfully with organic LangGraph architecture"
            )


    def _set_default_config(self):
        """Set default configuration values using centralized system."""
        self.config = {
            "llm": {
                "model_name": get_config_value("ai.default_model", "gpt-4o-mini"),
                "temperature": get_config_value("ai.default_temperature", 0.1)
            },
            "routing_keys": {
                "clone": get_config_value("routing.tokens.git_clone", "ROUTE_TO_CLONE"),
                "stack_detect": get_config_value("routing.tokens.analyze", "ROUTE_TO_STACK_DETECT"),
                "terraform": get_config_value("routing.tokens.terraform_init", "ROUTE_TO_TERRAFORM"),
                "issue": get_config_value("routing.tokens.open_issue", "ROUTE_TO_ISSUE"),
                "end": get_config_value("routing.tokens.end", "ROUTE_TO_END"),
            },
            "prompts": {
                "planner_prompt": """User input: "{user_input}"

Analyze this R2D (Repo-to-Deployment) request and determine the appropriate action:
1. If requesting to clone a repository (keywords: 'clone', 'download', 'git clone'), respond with "{route_clone}"
2. If requesting stack detection (keywords: 'detect', 'scan', 'find files', 'infrastructure'), respond with "{route_stack_detect}"
3. If requesting Terraform operations (keywords: 'terraform', 'plan', 'apply', 'init'), respond with "{route_terraform}"
4. If requesting GitHub issue creation (keywords: 'issue', 'error', 'problem'), respond with "{route_issue}"
5. If the request is complete or no action needed, respond with "{route_end}"

Important: Only use routing tokens if the input contains actionable R2D workflow requests."""
            },
            "workflow": {
                "timeout_seconds": get_config_value("network.terraform_timeout", 600),
                "working_directory": get_config_value("system.workspace_base", "/workspace"),
                "auto_branch_naming": True,
                "enhanced_terraform": True
            }
        }
        self.logger.info("Default configuration set")

    def _deep_merge(self, base: dict, overlay: dict) -> dict:
        """
        Deep merge two dictionaries, with overlay taking precedence.
        
        Args:
            base: Base dictionary
            overlay: Dictionary to overlay on base
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    # --- AgentBase interface -------------------------------------------------
    def plan(self, query: str, **kwargs):
        """Generate a plan for the R2D workflow (required by AgentBase)."""
        self.logger.info(f"Planning R2D workflow for: '{query}'")

        plan = {
            "input_query": query,
            "predicted_action": "analyze_and_orchestrate",
            "description": "Orchestrate full R2D workflow: clone → detect → terraform",
        }

        # Simple analysis to predict the route
        query_lower = query.lower()
        if any(word in query_lower for word in ["clone", "download", "git clone"]):
            plan["predicted_route"] = "clone_repo"
        elif any(
            word in query_lower
            for word in ["detect", "scan", "find files", "infrastructure"]
        ):
            plan["predicted_route"] = "stack_detection"
        elif any(
            word in query_lower for word in ["terraform", "plan", "apply", "init"]
        ):
            plan["predicted_route"] = "terraform_workflow"
        elif any(word in query_lower for word in ["issue", "error", "problem"]):
            plan["predicted_route"] = "issue_creation"
        else:
            plan["predicted_route"] = "full_r2d_workflow"

        self.logger.debug(f"Generated plan: {plan}")
        return plan

    def report(self, *args, **kwargs):
        """Get current memory state (required by AgentBase)."""
        return self.get_memory_state()

    # --- Organic LangGraph Architecture Methods ---

    def _planner_llm_node(self, state: SupervisorAgentState):
        """
        LLM planner node that analyzes R2D requests and decides routing.
        Emits routing tokens based on the user's workflow requirements.
        """
        # Get LLM configuration
        llm_config = self.config.get("llm", {})
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature")

        # Use enhanced LLM router following GitAgent/TerraformAgent pattern
        try:
            if model_name is not None or temperature is not None:
                actual_model_name = (
                    model_name if model_name is not None else "gpt-4o-mini"
                )
                actual_temperature = temperature if temperature is not None else 0.1
                self.logger.debug(
                    f"Supervisor planner using LLM: {actual_model_name}, Temp: {actual_temperature}"
                )

                llm = self.llm_router.get_llm(
                    model_name=actual_model_name,
                    temperature=actual_temperature,
                    agent_name="supervisor_agent",
                )
            else:
                self.logger.debug(
                    "Supervisor planner using agent-specific LLM configuration"
                )
                llm = self.llm_router.get_llm_for_agent("supervisor_agent")
        except Exception as e:
            self.logger.error(
                f"Failed to get LLM from router: {e}. Falling back to basic get_llm."
            )
            llm = get_llm(model_name=model_name, temperature=temperature)

        # Store conversation in memory
        query_content = state["input_message"].content
        self.memory.add_to_conversation(
            "user", query_content, {"agent": "supervisor_agent", "node": "planner"}
        )

        try:
            self.logger.debug(f"Supervisor planner LLM input: {query_content}")

            # Build the R2D-specific analysis prompt
            analysis_prompt_template = self.config.get("prompts", {}).get(
                "planner_prompt",
                """
User input: "{user_input}"

Analyze this R2D (Repo-to-Deployment) request and determine the appropriate action:
1. If requesting to clone a repository (keywords: 'clone', 'download', 'git clone'), respond with "{route_clone}"
2. If requesting stack detection (keywords: 'detect', 'scan', 'find files', 'infrastructure'), respond with "{route_stack_detect}"
3. If requesting Terraform operations (keywords: 'terraform', 'plan', 'apply', 'init'), respond with "{route_terraform}"
4. If requesting GitHub issue creation (keywords: 'issue', 'error', 'problem'), respond with "{route_issue}"
5. If the request is complete or no action needed, respond with "{route_end}"

Important: Only use routing tokens if the input contains actionable R2D workflow requests.
            """,
            )

            routing_keys = self.config.get(
                "routing_keys",
                {
                    "clone": "ROUTE_TO_CLONE",
                    "stack_detect": "ROUTE_TO_STACK_DETECT",
                    "terraform": "ROUTE_TO_TERRAFORM",
                    "issue": "ROUTE_TO_ISSUE",
                    "end": "ROUTE_TO_END",
                },
            )

            analysis_prompt = analysis_prompt_template.format(
                user_input=query_content,
                route_clone=routing_keys["clone"],
                route_stack_detect=routing_keys["stack_detect"],
                route_terraform=routing_keys["terraform"],
                route_issue=routing_keys["issue"],
                route_end=routing_keys["end"],
            )

            self.logger.debug(f"Supervisor planner LLM prompt: {analysis_prompt}")

            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            self.logger.debug(f"Supervisor planner LLM response: {response.content}")
            response_content = response.content.strip()

            # Store LLM response in memory
            self.memory.add_to_conversation(
                "assistant",
                response_content,
                {"agent": "supervisor_agent", "node": "planner", "model": model_name},
            )

            # Determine routing based on response content
            new_state_update = {}
            if routing_keys["clone"] in response_content:
                new_state_update = {
                    "final_result": "route_to_clone",
                    "operation_type": "clone",
                    "error_message": None,
                }
            elif routing_keys["stack_detect"] in response_content:
                new_state_update = {
                    "final_result": "route_to_stack_detect",
                    "operation_type": "stack_detect",
                    "error_message": None,
                }
            elif routing_keys["terraform"] in response_content:
                new_state_update = {
                    "final_result": "route_to_terraform",
                    "operation_type": "terraform",
                    "error_message": None,
                }
            elif routing_keys["issue"] in response_content:
                new_state_update = {
                    "final_result": "route_to_issue",
                    "operation_type": "issue",
                    "error_message": None,
                }
            elif routing_keys["end"] in response_content:
                # Direct answer or route to end
                new_state_update = {
                    "final_result": response.content,
                    "operation_type": "direct_answer",
                    "error_message": None,
                }
            else:
                # Default: treat as complete R2D workflow request
                new_state_update = {
                    "final_result": "route_to_clone",  # Start with cloning
                    "operation_type": "full_workflow",
                    "error_message": None,
                }

            self.logger.info(
                f"Supervisor planner decision: {new_state_update.get('final_result', 'N/A')}"
            )
            return new_state_update

        except Exception as e:
            self.logger.error(f"LLM error in supervisor planner: {e}", exc_info=True)
            self.memory.add_to_conversation(
                "system",
                f"Error in planner: {str(e)}",
                {"agent": "supervisor_agent", "node": "planner", "error": True},
            )

            # Enhanced error categorization for better issue titles
            error_message = str(e)
            enhanced_error_message = f"SupervisorAgent planner error: {error_message}"

            # Detect specific error types for better routing and title generation
            if "api key" in error_message.lower() or "401" in error_message.lower():
                enhanced_error_message = (
                    f"SupervisorAgent API key error: {error_message}"
                )
            elif (
                "openai" in error_message.lower()
                or "anthropic" in error_message.lower()
            ):
                enhanced_error_message = (
                    f"SupervisorAgent LLM service error: {error_message}"
                )
            elif (
                "network" in error_message.lower()
                or "connection" in error_message.lower()
            ):
                enhanced_error_message = (
                    f"SupervisorAgent network error: {error_message}"
                )
            elif "timeout" in error_message.lower():
                enhanced_error_message = (
                    f"SupervisorAgent timeout error: {error_message}"
                )
            elif (
                "permission" in error_message.lower()
                or "forbidden" in error_message.lower()
            ):
                enhanced_error_message = (
                    f"SupervisorAgent permission error: {error_message}"
                )

            # Route to issue creation for any planner errors (API key, network, etc.)
            self.logger.warning(
                f"Error detected in supervisor planner, routing to issue creation: {enhanced_error_message}"
            )
            return {
                "final_result": "route_to_issue",
                "error_message": enhanced_error_message,
                "operation_type": "planner_error",
            }

    def _route_after_planner(self, state: SupervisorAgentState):
        """
        Router function that determines the next node based on planner output.
        Maps routing tokens to appropriate tool nodes or END.
        Only used from the planner node.
        """
        self.logger.debug(
            f"Supervisor routing after planner. State: {state.get('final_result')}, error: {state.get('error_message')}"
        )

        if state.get("error_message"):
            self.logger.warning(
                f"Error detected in supervisor planner, routing to issue creation: {state['error_message']}"
            )
            return "issue_create_node"

        final_result = state.get("final_result", "")

        # Route based on planner decision
        if final_result == "route_to_clone":
            return "clone_repo_node"
        elif final_result == "route_to_stack_detect":
            return "stack_detect_node"
        elif final_result == "route_to_terraform":
            return "terraform_workflow_node"
        elif final_result == "route_to_issue":
            return "issue_create_node"
        else:
            return END

    def _route_workflow_continuation(self, state: SupervisorAgentState):
        """
        Router function for sequential workflow continuation.
        Determines the next step in the R2D workflow based on current state.
        """
        self.logger.debug(
            f"Supervisor workflow routing. State: {state.get('final_result')}, error: {state.get('error_message')}"
        )

        # If there's an error, route to issue creation
        if state.get("error_message"):
            self.logger.warning(
                f"Error detected, routing to issue creation: {state['error_message']}"
            )
            return "issue_create_node"

        final_result = state.get("final_result", "")

        # Sequential workflow: clone → stack_detect → terraform → end (removed branch_create)
        if final_result == "route_to_stack_detect":
            return "stack_detect_node"
        elif final_result == "route_to_terraform":
            return "terraform_workflow_node"
        elif final_result == "route_to_issue":
            return "issue_create_node"
        else:
            # Default: workflow complete
            return END

    # --- Tool Nodes: Use specialized agents with their natural tools ---

    def _clone_repo_node(self, state: SupervisorAgentState):
        """Clone repository using GitAgent."""
        try:
            self.logger.info(f"Cloning repository: {state['repo_url']}")

            git_result: GitAgentOutput = self.git_agent.run(
                GitAgentInput(
                    query=f"clone repository {state['repo_url']}",
                    thread_id=state.get("thread_id"),
                )
            )

            if git_result.artifacts and git_result.artifacts.get('error_message'):
                error_message = git_result.artifacts.get('error_message')
                self.logger.error(
                    f"Repository cloning failed: {error_message}"
                )
                return {
                    "final_result": f"Repository cloning failed: {error_message}",
                    "error_message": error_message,
                    "operation_type": "clone_error",
                }

            # Update state with repo path and continue to stack detection
            repo_path = git_result.artifacts.get('repo_path') if git_result.artifacts else git_result.summary
            self.logger.info(
                f"Repository cloned successfully to: {repo_path}"
            )
            return {
                "repo_path": repo_path,
                "final_result": "route_to_stack_detect",  # Continue workflow
                "operation_type": "clone_success",
                "error_message": None,
            }

        except Exception as e:
            self.logger.error(f"Error in clone repo node: {e}")
            return {
                "final_result": f"Clone operation failed: {str(e)}",
                "error_message": str(e),
                "operation_type": "clone_error",
            }

    def _stack_detect_node(self, state: SupervisorAgentState):
        """Detect infrastructure stack using enhanced detection logic."""
        try:
            repo_path = state.get("repo_path")
            if not repo_path:
                return {
                    "final_result": "No repository path available for stack detection",
                    "error_message": "Missing repo_path",
                    "operation_type": "stack_detect_error",
                }

            self.logger.info(f"Detecting infrastructure stack in: {repo_path}")

            stack_detected = detect_stack_files(repo_path, self.shell_agent)
            histogram = build_stack_histogram(repo_path, self.shell_agent)
            self.logger.info(
                f"Stack detection completed: {stack_detected}, histogram: {histogram}"
            )

            if route_on_stack(histogram):
                unsupported = [k for k, v in histogram.items() if v < STACK_SUPPORT_THRESHOLD]
                stack = unsupported[0] if unsupported else "unknown"
                issue_title = f"Unsupported: {stack}"
                issue_body = (
                    f"Automated detection flagged unsupported stack {stack}. "
                    f"Histogram: {histogram}. cc @github-copilot"
                )

                issue_result = self.git_agent.run(
                    GitAgentInput(
                        query=f"open issue {issue_title} for repository {state['repo_url']}: {issue_body}",
                        thread_id=state.get("thread_id"),
                    )
                )

                issues_opened = 0
                error_message = None
                final_result = f"Unsupported stack detected: {stack}"
                if issue_result.artifacts.get('error_message'):
                    error_message = issue_result.artifacts.get('error_message')
                    final_result += f" - Issue creation failed: {issue_result.artifacts.get('error_message')}"
                else:
                    issues_opened = 1
                    final_result += f" - Issue created: {issue_result.summary}"

                return {
                    "stack_detected": stack_detected,
                    "final_result": final_result,
                    "operation_type": "unsupported_stack",
                    "error_message": error_message,
                    "issues_opened": issues_opened,
                    "unsupported": True,
                }

            return {
                "stack_detected": stack_detected,
                "final_result": "route_to_terraform",  # Skip branch creation, go directly to terraform
                "operation_type": "stack_detect_success",
                "error_message": None,
            }

        except Exception as e:
            self.logger.error(f"Error in stack detection node: {e}")
            return {
                "final_result": f"Stack detection failed: {str(e)}",
                "error_message": str(e),
                "operation_type": "stack_detect_error",
            }

    def _terraform_workflow_node(self, state: SupervisorAgentState):
        """Execute Terraform workflow using TerraformAgent."""
        try:
            repo_path = state.get("repo_path")
            stack_detected = state.get("stack_detected", {})

            if not repo_path:
                return {
                    "final_result": "No repository path available for Terraform workflow",
                    "error_message": "Missing repo_path",
                    "operation_type": "terraform_error",
                }

            # Enhanced Terraform workflow if Terraform files detected
            if stack_detected.get("*.tf", 0) > 0:
                self.logger.info(
                    f"Found {stack_detected['*.tf']} Terraform files, running enhanced workflow"
                )
                tf_result = self._run_enhanced_terraform_workflow(
                    repo_path, state.get("thread_id")
                )
            else:
                self.logger.info("No Terraform files detected, running basic plan")
                tf_result: TerraformAgentOutput = self.terraform_agent.run(
                    TerraformAgentInput(
                        query=f"terraform plan in {repo_path}",
                        thread_id=state.get("thread_id"),
                    )
                )

            if tf_result.error_message:
                self.logger.error(
                    f"Terraform workflow failed: {tf_result.error_message}"
                )

                # If authentication is missing, request token and retry
                if tf_result.error_tags and "needs_pat" in tf_result.error_tags:
                    from .pat_loop import request_and_wait_for_pat

                    if request_and_wait_for_pat(state["repo_url"], self.git_agent, poll_interval=5, timeout=60):
                        tf_result = self._run_enhanced_terraform_workflow(
                            repo_path, state.get("thread_id")
                        )
                        if not tf_result.error_message:
                            return {
                                "terraform_summary": tf_result.result,
                                "final_result": "R2D workflow completed successfully",
                                "operation_type": "terraform_success",
                                "error_message": None,
                            }

                return {
                    "final_result": "route_to_issue",  # Route to issue creation
                    "terraform_summary": tf_result.result,
                    "error_message": tf_result.error_message,
                    "operation_type": "terraform_error",
                }

            self.logger.info("Terraform workflow completed successfully")
            return {
                "terraform_summary": tf_result.result,
                "final_result": "R2D workflow completed successfully",
                "operation_type": "terraform_success",
                "error_message": None,
            }

        except Exception as e:
            self.logger.error(f"Error in Terraform workflow node: {e}")
            return {
                "final_result": f"Terraform workflow failed: {str(e)}",
                "error_message": str(e),
                "operation_type": "terraform_error",
            }

    def _issue_create_node(self, state: SupervisorAgentState):
        """
        Create GitHub issue using GitAgent with organic title generation and clean error formatting.
        CRITICAL: This node MUST NEVER fail - it's the last resort for error reporting.
        Implements multiple fallback mechanisms to ensure issue creation always succeeds.
        """
        # Extract state safely with defaults to prevent ANY failure
        repo_url = state.get('repo_url', 'unknown-repository')
        branch_name = state.get('branch_name', 'unknown')
        stack_detected = state.get('stack_detected', {})
        error_message = state.get('error_message', 'Unknown error occurred during R2D workflow')
        dry_run = state.get('dry_run', False)
        
        self.logger.info(f"🚨 CRITICAL: Creating GitHub issue for R2D workflow error (repo: {repo_url})")
        
        # BULLETPROOF ISSUE CREATION with multiple fallback layers
        try:
            # === LAYER 1: Advanced Issue Creation ===
            return self._create_issue_with_advanced_formatting(
                repo_url, branch_name, stack_detected, error_message, dry_run, state
            )
        except Exception as e:
            self.logger.error(f"❌ Layer 1 (Advanced) failed: {e}")
            try:
                # === LAYER 2: Simple Issue Creation ===
                return self._create_issue_with_simple_formatting(
                    repo_url, branch_name, stack_detected, error_message, dry_run, state
                )
            except Exception as e2:
                self.logger.error(f"❌ Layer 2 (Simple) failed: {e2}")
                try:
                    # === LAYER 3: Minimal Issue Creation ===
                    return self._create_issue_with_minimal_formatting(
                        repo_url, error_message, dry_run, state
                    )
                except Exception as e3:
                    self.logger.error(f"❌ Layer 3 (Minimal) failed: {e3}")
                    # === LAYER 4: Emergency Fallback ===
                    return self._create_emergency_fallback_response(
                        repo_url, error_message, e, e2, e3
                    )

    def _create_issue_with_advanced_formatting(self, repo_url, branch_name, stack_detected, error_message, dry_run, state):
        """Layer 1: Advanced issue creation with full formatting and utilities."""
        self.logger.info("🎯 Attempting advanced issue creation (Layer 1)")
        
        # Import text utilities for organic title generation and ANSI cleanup
        try:
            from diagram_to_iac.tools.text_utils import (
                generate_organic_issue_title,
                enhance_error_message_for_issue,
                create_issue_metadata_section,
            )
            text_utils_available = True
        except ImportError as e:
            self.logger.warning(f"Text utilities not available: {e}")
            text_utils_available = False

        # Determine error type from message for better title generation
        error_type = self._determine_error_type(error_message)

        # Create context for organic title generation
        error_context = {
            "error_type": error_type,
            "stack_detected": stack_detected,
            "error_message": error_message,
            "repo_url": repo_url,
            "branch_name": branch_name,
        }

        # Generate organic, thoughtful issue title with fallback
        if text_utils_available:
            try:
                issue_title_final = generate_organic_issue_title(error_context)
            except Exception as e:
                self.logger.warning(f"Failed to generate organic title: {e}")
                issue_title_final = self._generate_fallback_title(repo_url, error_type)
        else:
            issue_title_final = self._generate_fallback_title(repo_url, error_type)

        # Create enhanced issue body with metadata and clean error formatting
        if text_utils_available:
            try:
                metadata_section = create_issue_metadata_section(error_context)
                enhanced_error = enhance_error_message_for_issue(error_message, error_context)
                issue_body = f"{metadata_section}{enhanced_error}"
            except Exception as e:
                self.logger.warning(f"Failed to enhance issue body: {e}")
                issue_body = self._generate_fallback_body(error_message, error_context)
        else:
            issue_body = self._generate_fallback_body(error_message, error_context)

        # Clean and sanitize the issue body for shell safety
        issue_body_safe = self._sanitize_for_shell(issue_body)
        issue_title_safe = self._sanitize_for_shell(issue_title_final)

        # Get existing issue ID for deduplication
        existing_id = self._get_existing_issue_id(repo_url, error_type)
        
        if dry_run:
            return self._handle_dry_run_mode(issue_title_safe, issue_body_safe, repo_url, existing_id, error_type, state)

        # === CRITICAL: Use safe issue creation ===
        return self._execute_safe_issue_creation(
            repo_url, issue_title_safe, issue_body_safe, existing_id, error_type, state
        )

    def _create_issue_with_simple_formatting(self, repo_url, branch_name, stack_detected, error_message, dry_run, state):
        """Layer 2: Simple issue creation without advanced text utilities."""
        self.logger.info("🔧 Attempting simple issue creation (Layer 2)")
        
        error_type = self._determine_error_type(error_message)
        
        # Simple title and body generation
        issue_title = f"R2D Workflow Error: {error_type} in {repo_url.split('/')[-1]}"
        issue_body = f"""# R2D Workflow Error Report

**Repository:** {repo_url}
**Branch:** {branch_name}
**Error Type:** {error_type}
**Detected Stack:** {stack_detected}
**Timestamp:** {self._get_timestamp()}

## Error Details

```
{error_message[:2000]}  # Truncate to prevent issues
```

---
*This issue was created automatically by the R2D workflow system.*
"""
        
        # Clean and sanitize
        issue_body_safe = self._sanitize_for_shell(issue_body)
        issue_title_safe = self._sanitize_for_shell(issue_title)
        
        existing_id = self._get_existing_issue_id(repo_url, error_type)
        
        if dry_run:
            return self._handle_dry_run_mode(issue_title_safe, issue_body_safe, repo_url, existing_id, error_type, state)
        
        return self._execute_safe_issue_creation(
            repo_url, issue_title_safe, issue_body_safe, existing_id, error_type, state
        )

    def _create_issue_with_minimal_formatting(self, repo_url, error_message, dry_run, state):
        """Layer 3: Minimal issue creation with basic formatting only."""
        self.logger.info("⚡ Attempting minimal issue creation (Layer 3)")
        
        # Ultra-simple title and body
        timestamp = self._get_timestamp()
        issue_title = f"R2D Error - {timestamp}"
        issue_body = f"R2D workflow encountered an error in {repo_url}.\n\nError: {error_message[:500]}\n\nTimestamp: {timestamp}"
        
        # Basic sanitization
        issue_body_safe = issue_body.replace('"', "'").replace('`', "'").replace('\n', ' ')[:1000]
        issue_title_safe = issue_title.replace('"', "'").replace('`', "'")[:100]
        
        if dry_run:
            return {
                "final_result": f"DRY RUN: Would create minimal issue: {issue_title_safe}",
                "issues_opened": 0,
                "operation_type": "dry_run_minimal",
                "error_message": None,
            }
        
        return self._execute_safe_issue_creation(
            repo_url, issue_title_safe, issue_body_safe, None, "minimal", state
        )

    def _create_emergency_fallback_response(self, repo_url, error_message, error1, error2, error3):
        """Layer 4: Emergency fallback when all issue creation attempts fail."""
        self.logger.error("🚨 EMERGENCY: All issue creation layers failed!")
        self.logger.error(f"Layer 1 error: {error1}")
        self.logger.error(f"Layer 2 error: {error2}")  
        self.logger.error(f"Layer 3 error: {error3}")
        
        # Log the original error and all failure details
        self.logger.error(f"Original workflow error: {error_message}")
        
        # Return a successful response that indicates the issue creation failure
        # but doesn't crash the workflow
        return {
            "final_result": f"R2D workflow failed with error: {error_message[:200]}... CRITICAL: Unable to create GitHub issue after 3 attempts. Manual intervention required.",
            "issues_opened": 0,
            "operation_type": "emergency_fallback",
            "error_message": f"Issue creation failed: {str(error3)[:200]}",
            "emergency_details": {
                "original_error": error_message,
                "repo_url": repo_url,
                "issue_creation_errors": [str(error1), str(error2), str(error3)]
            }
        }

    def _determine_error_type(self, error_message):
        """Determine error type from message for better title generation."""
        error_message_lower = error_message.lower() if error_message else ""
        
        if "terraform init" in error_message_lower:
            return "terraform_init"
        elif "terraform plan" in error_message_lower:
            return "terraform_plan"
        elif "terraform apply" in error_message_lower:
            return "terraform_apply"
        elif "auth" in error_message_lower or "missing_terraform_token" in error_message_lower or "error_missing_terraform_token" in error_message_lower:
            return "auth_failed"
        elif "api key" in error_message_lower or "401" in error_message_lower:
            return "api_key_error"
        elif "llm error" in error_message_lower or "supervisoragent llm error" in error_message_lower:
            return "llm_error"
        elif "network" in error_message_lower or "connection" in error_message_lower:
            return "network_error"
        elif "timeout" in error_message_lower:
            return "timeout_error"
        elif "permission" in error_message_lower or "forbidden" in error_message_lower:
            return "permission_error"
        elif "planner error" in error_message_lower:
            return "planner_error"
        elif "workflow error" in error_message_lower:
            return "workflow_error"
        else:
            return "unknown"

    def _generate_fallback_title(self, repo_url, error_type):
        """Generate a simple fallback title when advanced generation fails."""
        repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
        return f"R2D Workflow Error: {error_type} in {repo_name}"

    def _generate_fallback_body(self, error_message, error_context):
        """Generate a simple fallback body when advanced generation fails."""
        return f"""# R2D Workflow Error Report

**Repository:** {error_context.get('repo_url', 'unknown')}
**Branch:** {error_context.get('branch_name', 'unknown')}
**Error Type:** {error_context.get('error_type', 'unknown')}
**Timestamp:** {self._get_timestamp()}

## Error Details

```
{error_message[:1500]}
```

---
*This issue was created automatically by the R2D workflow system.*
"""

    def _sanitize_for_shell(self, text):
        """Sanitize text for safe shell execution by removing/escaping problematic characters."""
        if not text:
            return ""
        
        import re
        
        # Remove ANSI color codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)
        
        # Replace problematic characters
        text = text.replace('"', "'")  # Replace double quotes with single quotes
        text = text.replace('`', "'")  # Replace backticks with single quotes
        text = text.replace('\\', '/')  # Replace backslashes
        text = text.replace('|', ' pipe ')  # Replace pipes
        text = text.replace(';', ',')  # Replace semicolons
        text = text.replace('$', 'USD')  # Replace dollar signs
        
        # Limit length to prevent command line issues
        if len(text) > 2000:
            text = text[:1997] + "..."
        
        return text

    def _get_timestamp(self):
        """Get current timestamp in a consistent format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def _handle_dry_run_mode(self, issue_title, issue_body, repo_url, existing_id, error_type, state):
        """Handle dry run mode with proper user interaction."""
        if self.demonstrator:
            should_proceed = self.demonstrator.show_issue(issue_title, issue_body)
            
            if should_proceed:
                self.logger.info("User chose to proceed with issue creation in dry-run mode")
                # Fall through to create the actual issue
            else:
                self.logger.info("User chose not to proceed, ending dry-run")
                return {
                    "final_result": "DRY RUN: User chose not to proceed with issue creation",
                    "issues_opened": 0,
                    "operation_type": "dry_run_aborted",
                    "error_message": None,
                }

        # Delegate to DemonstratorAgent for intelligent interactive dry-run
        try:
            self.logger.info("Delegating to DemonstratorAgent for interactive dry-run")
            
            from diagram_to_iac.agents.demonstrator_langgraph import DemonstratorAgentInput
            
            demo_result = self.demonstrator_agent.run(
                DemonstratorAgentInput(
                    query=f"Demonstrate error: {error_type}",
                    error_type=error_type,
                    error_message=state.get('error_message', 'Unknown error'),
                    repo_url=repo_url,
                    branch_name=state.get('branch_name', 'unknown'),
                    stack_detected=state.get('stack_detected', {}),
                    issue_title=issue_title,
                    issue_body=issue_body,
                    existing_issue_id=existing_id,
                    thread_id=state.get("thread_id"),
                )
            )
            
            # Return the demonstration result and exit early
            return {
                "final_result": demo_result["result"],
                "issues_opened": 1 if demo_result["issue_created"] else 0,
                "operation_type": f"demo_{demo_result['action_taken']}",
                "error_message": demo_result.get("error_message"),
            }
        except Exception as e:
            self.logger.warning(f"DemonstratorAgent failed in dry-run: {e}")
            return {
                "final_result": f"DRY RUN: Would create issue '{issue_title}' (demonstrator failed: {e})",
                "issues_opened": 0,
                "operation_type": "dry_run_demo_failed",
                "error_message": None,
            }

    def _execute_safe_issue_creation(self, repo_url, issue_title, issue_body, existing_id, error_type, state):
        """Execute issue creation with multiple safety mechanisms."""
        try:
            # Method 1: Try with file-based body (avoids shell escaping issues)
            return self._create_issue_with_file_body(repo_url, issue_title, issue_body, existing_id, error_type, state)
        except Exception as e1:
            self.logger.warning(f"File-based issue creation failed: {e1}")
            try:
                # Method 2: Try with heavily sanitized direct command
                return self._create_issue_with_direct_command(repo_url, issue_title, issue_body, existing_id, error_type, state)
            except Exception as e2:
                self.logger.warning(f"Direct command issue creation failed: {e2}")
                # Method 3: Ultra-simple issue creation
                return self._create_ultra_simple_issue(repo_url, error_type, state)

    def _create_issue_with_file_body(self, repo_url, issue_title, issue_body, existing_id, error_type, state):
        """Create issue using temporary file for body to avoid shell escaping issues."""
        import tempfile
        import os
        
        self.logger.info("🗂️ Creating issue using file-based body method")
        
        # Write body to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(issue_body)
            temp_file = f.name
        
        try:
            # Use file for body to avoid shell escaping issues
            if existing_id:
                query = f"update issue {existing_id} for repository {repo_url} with title '{issue_title}' and body from file {temp_file}"
            else:
                query = f"open issue '{issue_title}' for repository {repo_url} with body from file {temp_file}"
            
            issue_result = self.git_agent.run(
                GitAgentInput(
                    query=query,
                    issue_id=existing_id,
                    thread_id=state.get("thread_id"),
                )
            )
            
            return self._process_issue_result(issue_result, existing_id, repo_url, error_type, state)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass

    def _create_issue_with_direct_command(self, repo_url, issue_title, issue_body, existing_id, error_type, state):
        """Create issue with heavily sanitized direct command."""
        self.logger.info("⚡ Creating issue using direct command method")
        
        # Further sanitize for direct command
        safe_title = issue_title.replace("'", "").replace('"', '')[:80]
        safe_body = issue_body.replace("'", "").replace('"', '').replace('\n', ' ')[:800]
        
        if existing_id:
            query = f"update issue {existing_id} for repository {repo_url}: {safe_body}"
        else:
            query = f"open issue {safe_title} for repository {repo_url}: {safe_body}"
        
        issue_result = self.git_agent.run(
            GitAgentInput(
                query=query,
                issue_id=existing_id,
                thread_id=state.get("thread_id"),
            )
        )
        
        return self._process_issue_result(issue_result, existing_id, repo_url, error_type, state)

    def _create_ultra_simple_issue(self, repo_url, error_type, state):
        """Create ultra-simple issue as last resort."""
        self.logger.info("🚨 Creating ultra-simple issue as last resort")
        
        simple_title = f"R2D Error {self._get_timestamp()}"
        simple_body = f"R2D workflow error of type {error_type} in {repo_url}"
        
        issue_result = self.git_agent.run(
            GitAgentInput(
                query=f"open issue {simple_title} for repository {repo_url}: {simple_body}",
                thread_id=state.get("thread_id"),
            )
        )
        
        return self._process_issue_result(issue_result, None, repo_url, error_type, state)

    def _process_issue_result(self, issue_result, existing_id, repo_url, error_type, state):
        """Process the result of issue creation and handle post-creation tasks."""
        issue_error_msg = issue_result.artifacts.get('error_message') if issue_result.artifacts else None
        
        if issue_error_msg:
            self.logger.error(f"Issue creation failed: {issue_error_msg}")
            return {
                "final_result": f"Issue creation failed: {issue_error_msg}",
                "issues_opened": 0,
                "operation_type": "issue_error",
                "error_message": issue_error_msg,
            }

        # Handle successful issue creation
        if existing_id is None:
            new_id = self._parse_issue_number(issue_result.summary)
            if new_id is not None:
                self._record_issue_id(repo_url, error_type, new_id)
                self._update_run_registry(new_id, repo_url, state)
                self._handle_pr_merge_context(new_id, repo_url, state)

        self.logger.info("✅ GitHub issue created successfully")
        return {
            "final_result": f"R2D workflow failed, issue created: {issue_result.summary}",
            "issues_opened": 1,
            "operation_type": "issue_success",
            "error_message": None,
        }

    def _update_run_registry(self, new_issue_id, repo_url, state):
        """Update the run registry with the new issue ID."""
        try:
            current_runs = self.run_registry.find_by_commit_and_repo(repo_url, "manual")
            if current_runs:
                latest_run = current_runs[0]
                updated = self.run_registry.update(latest_run.run_key, {
                    'umbrella_issue_id': new_issue_id,
                    'status': 'FAILED'
                })
                if updated:
                    self.logger.info(f"Updated run {latest_run.run_key} with issue ID {new_issue_id}")
        except Exception as e:
            self.logger.warning(f"Failed to update run registry with issue ID: {e}")

    def _handle_pr_merge_context(self, new_issue_id, repo_url, state):
        """Handle PR merge context by linking to previous issue."""
        try:
            if self.pr_merge_context:
                previous_issue_id = self.run_registry.find_previous_umbrella_issue(
                    repo_url, exclude_sha=self.pr_merge_context.get('merged_sha', '')
                )
                if previous_issue_id:
                    updated_comment = self._create_issue_link_comment(
                        previous_issue_id, 
                        self.pr_merge_context.get('merged_sha', 'unknown')[:7],
                        new_issue_id=new_issue_id
                    )
                    link_result = self.git_agent.run(
                        GitAgentInput(
                            query=f"comment on issue {previous_issue_id}: {updated_comment}",
                            issue_id=previous_issue_id,
                            thread_id=state.get("thread_id")
                        )
                    )
                    link_error_msg = link_result.artifacts.get('error_message') if link_result.artifacts else None
                    if link_error_msg:
                        self.logger.warning(f"Failed to update previous issue #{previous_issue_id} with new issue link: {link_error_msg}")
                    else:
                        self.logger.info(f"Successfully updated previous issue #{previous_issue_id} with link to new issue #{new_issue_id}")
        except Exception as e:
            self.logger.warning(f"Error updating previous issue with new issue link: {e}")

    # === Continue with existing methods ===
    
    # --- PR Merge Handling Methods ---

    def _generate_dynamic_branch_name(self) -> str:
        """Generate timestamp-based branch name."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"r2d-{timestamp}"

    def _detect_pr_merge_context(self) -> Optional[Dict[str, Any]]:
        """
        Detect PR merge context from environment variables.
        
        Returns:
            PR merge context dictionary if detected, None otherwise
        """
        try:
            pr_context_env = os.environ.get('PR_MERGE_CONTEXT')
            if pr_context_env:
                import json
                pr_context = json.loads(pr_context_env)
                self.logger.info(f"PR merge context detected: {pr_context}")
                return pr_context
        except Exception as e:
            self.logger.warning(f"Failed to parse PR merge context: {e}")
        
        return None

    def _handle_pr_merge_workflow(self, repo_url: str, commit_sha: str) -> Optional[Dict[str, Any]]:
        """
        Handle PR merge workflow by detecting previous umbrella issues and linking them.
        
        Args:
            repo_url: Repository URL
            commit_sha: New commit SHA from PR merge
            
        Returns:
            Dictionary with previous issue information if found, None otherwise
        """
        try:
            # Find previous umbrella issue for this repository (excluding current SHA)
            previous_issue_id = self.run_registry.find_previous_umbrella_issue(
                repo_url, exclude_sha=commit_sha
            )
            
            if previous_issue_id:
                self.logger.info(f"Found previous umbrella issue #{previous_issue_id} for {repo_url}")
                
                # Create run for new commit and link to previous issue
                job_name = f"pr-merge-{self.pr_merge_context.get('pr_number', 'unknown')}"
                new_run_key = self.run_registry.create_run(
                    repo_url=repo_url,
                    commit_sha=commit_sha,
                    job_name=job_name,
                    thread_id=str(self.pr_merge_context.get('pr_number', 'unknown'))
                )
                
                # Find the previous run to link them
                previous_run = self.run_registry.find_latest_run_with_issue(repo_url)
                if previous_run:
                    self.run_registry.link_predecessor_run(new_run_key, previous_run.run_key)
                    self.run_registry.close_old_umbrella_issue(
                        previous_run.run_key, 
                        new_issue_id=0,  # Will be updated when new issue is created
                        new_commit_sha=commit_sha
                    )
                    
                    # Comment on the previous issue to link it to the new workflow
                    try:
                        link_comment = self._create_issue_link_comment(
                            previous_issue_id, commit_sha, new_issue_id=None
                        )
                        # Use the standard issue format but with issue_id to trigger commenting
                        comment_result = self.git_agent.run(
                            GitAgentInput(
                                query=f"open issue PR Merge Update for repository {repo_url}: {link_comment}",
                                issue_id=previous_issue_id,
                                thread_id=str(self.pr_merge_context.get('pr_number', 'unknown'))
                            )
                        )
                        error_message = comment_result.artifacts.get('error_message') if comment_result.artifacts else None
                        if error_message:
                            self.logger.warning(f"Failed to comment on previous issue #{previous_issue_id}: {error_message}")
                        else:
                            self.logger.info(f"Successfully commented on previous issue #{previous_issue_id}")
                    except Exception as e:
                        self.logger.warning(f"Error commenting on previous issue #{previous_issue_id}: {e}")
                
                return {
                    "previous_issue_id": previous_issue_id,
                    "new_run_key": new_run_key,
                    "previous_run": previous_run,
                    "commit_sha": commit_sha[:7]
                }
        except Exception as e:
            self.logger.error(f"Error handling PR merge workflow: {e}")
        
        return None

    def _create_issue_link_comment(self, previous_issue_id: int, new_commit_sha: str, new_issue_id: Optional[int] = None) -> str:
        """
        Create a comment to link old issue to new issue for PR merge workflow.
        
        Args:
            previous_issue_id: ID of the previous umbrella issue
            new_commit_sha: New commit SHA that triggered the workflow
            new_issue_id: New issue ID if created
            
        Returns:
            Comment text for linking issues
        """
        short_sha = new_commit_sha[:7]
        
        if new_issue_id:
            comment = f"""🔄 **New commit detected: `{short_sha}`**

A new commit has been merged, opening fresh pipeline in Issue #{new_issue_id}.

**Previous Issue Status:** Resolved/Follow-up - superseded by new commit
**New Pipeline:** Issue #{new_issue_id} tracks the latest deployment

This issue is now closed and linked forward to the new deployment pipeline."""
        else:
            comment = f"""🔄 **New commit detected: `{short_sha}`**

A new commit has been merged, attempting to open fresh pipeline.

**Previous Issue Status:** Resolved/Follow-up - superseded by new commit

This issue is now closed. A new issue will be created for the latest deployment pipeline."""
        
        return comment

    # --- Utility Methods (preserved from original implementation) ---

    def _generate_dynamic_branch_name(self) -> str:
        """Generate timestamp-based branch name."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"r2d-{timestamp}"


    # --- Issue tracker helpers ---
    def _get_existing_issue_id(self, repo_url: str, error_type: str) -> Optional[int]:
        try:
            return self.issue_tracker.get_issue(repo_url, error_type)
        except Exception as e:
            self.logger.error(f"Issue tracker lookup failed: {e}")
            return None

    def _record_issue_id(self, repo_url: str, error_type: str, issue_id: int) -> None:
        try:
            self.issue_tracker.record_issue(repo_url, error_type, issue_id)
        except Exception as e:
            self.logger.error(f"Issue tracker update failed: {e}")

    def _parse_issue_number(self, text: str) -> Optional[int]:
        import re
        match = re.search(r'/issues/(\d+)', text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None
    

    def _detect_infrastructure_stack(self, repo_path: str) -> Dict[str, int]:
        """
        Detect infrastructure tooling in the repository.

        Returns:
            Dict mapping file types to counts (e.g. {"*.tf": 3, "*.yml": 2})
        """
        self.logger.info(f"Detecting infrastructure stack in {repo_path}")

        # Define patterns for infrastructure files
        stack_patterns = {
            "terraform": "*.tf",
            "ansible": "*.yml",
            "powershell": "*.ps1",
            "shell": "*.sh",
        }

        stack_detected = {}

        for stack_type, pattern in stack_patterns.items():
            try:
                # Try multiple approaches for file detection
                count = 0

                # Method 1: Try find command (most accurate) - wrapped in bash
                try:
                    find_result = self.shell_agent.run(
                        ShellAgentInput(
                            command=f"bash -c \"find . -name '{pattern}' -type f | wc -l\"",
                            cwd=repo_path,
                        )
                    )

                    if find_result.exit_code == 0:
                        count = int(find_result.output.strip())
                        self.logger.debug(
                            f"Found {count} {stack_type} files using find command"
                        )
                    else:
                        raise RuntimeError(
                            f"Find command failed: {find_result.error_message}"
                        )

                except Exception as e:
                    self.logger.warning(f"Find command failed for {stack_type}: {e}")

                    # Method 2: Fallback to ls with globbing - wrapped in bash
                    try:
                        ls_result = self.shell_agent.run(
                            ShellAgentInput(
                                command=f'bash -c "ls -1 {pattern} 2>/dev/null | wc -l || echo 0"',
                                cwd=repo_path,
                            )
                        )
                        if ls_result.exit_code == 0:
                            count = int(ls_result.output.strip())
                            self.logger.debug(
                                f"Found {count} {stack_type} files using ls fallback"
                            )
                        else:
                            # Method 3: Final fallback using bash expansion
                            bash_result = self.shell_agent.run(
                                ShellAgentInput(
                                    command=f"bash -c 'shopt -s nullglob; files=({pattern}); echo ${{#files[@]}}'",
                                    cwd=repo_path,
                                )
                            )
                            if bash_result.exit_code == 0:
                                count = int(bash_result.output.strip())
                                self.logger.debug(
                                    f"Found {count} {stack_type} files using bash expansion"
                                )

                    except Exception as fallback_e:
                        self.logger.error(
                            f"All detection methods failed for {stack_type}: {fallback_e}"
                        )
                        count = 0

                # Store result if files found
                if count > 0:
                    stack_detected[pattern] = count
                    self.logger.info(f"✅ Found {count} {stack_type} files ({pattern})")
                else:
                    self.logger.debug(f"No {stack_type} files found")

            except Exception as e:
                self.logger.error(f"Error detecting {stack_type} files: {e}")

        self.logger.info(f"Stack detection completed: {stack_detected}")
        return stack_detected

    def _run_enhanced_terraform_workflow(
        self, repo_path: str, thread_id: Optional[str]
    ) -> TerraformAgentOutput:
        """
        Run enhanced Terraform workflow with sophisticated features:
        - Terraform validation
        - Terraform init
        - Terraform plan with detailed output
        - Security scanning (placeholder)
        - Cost estimation (placeholder)
        """
        self.logger.info("Starting enhanced Terraform workflow")

        try:
            # Step 1: Terraform validation
            self.logger.info("Step 1: Terraform validation")
            validate_result = self.terraform_agent.run(
                TerraformAgentInput(
                    query=f"terraform validate in {repo_path}", thread_id=thread_id
                )
            )

            if validate_result.error_message:
                self.logger.error(
                    f"Terraform validation failed: {validate_result.error_message}"
                )
                return TerraformAgentOutput(
                    result="Terraform validation failed",
                    thread_id=thread_id or "unknown",
                    error_message=f"Validation failed: {validate_result.error_message}",
                    operation_type="validate",
                )

            # Step 2: Terraform init
            self.logger.info("Step 2: Terraform init")
            init_result = self.terraform_agent.run(
                TerraformAgentInput(
                    query=f"terraform init in {repo_path}", thread_id=thread_id
                )
            )

            if init_result.error_message:
                self.logger.error(f"Terraform init failed: {init_result.error_message}")
                return TerraformAgentOutput(
                    result="Terraform init failed",
                    thread_id=thread_id or "unknown",
                    error_message=f"Init failed: {init_result.error_message}",
                    operation_type="init",
                )

            # Step 3: Terraform plan with detailed output
            self.logger.info("Step 3: Terraform plan with detailed analysis")
            plan_result = self.terraform_agent.run(
                TerraformAgentInput(
                    query=f"terraform plan -detailed-exitcode -out=tfplan in {repo_path}",
                    thread_id=thread_id,
                )
            )

            # Step 4: Additional analysis (placeholder for future features)
            additional_insights = self._analyze_terraform_plan(repo_path)

            # Combine results
            enhanced_summary = f"""Enhanced Terraform Workflow Results:
✅ Validation: {validate_result.result}
✅ Init: {init_result.result}
📋 Plan: {plan_result.result}
🔍 Analysis: {additional_insights}"""

            if plan_result.error_message:
                return TerraformAgentOutput(
                    result=enhanced_summary,
                    thread_id=thread_id or "unknown",
                    error_message=plan_result.error_message,
                    operation_type="enhanced_plan",
                )

            return TerraformAgentOutput(
                result=enhanced_summary,
                thread_id=thread_id or "unknown",
                error_message=None,
                operation_type="enhanced_plan",
            )

        except Exception as e:
            self.logger.error(f"Enhanced Terraform workflow failed: {e}")
            return TerraformAgentOutput(
                result="Enhanced Terraform workflow failed",
                thread_id=thread_id or "unknown",
                error_message=str(e),
                operation_type="enhanced_workflow_error",
            )

    def _analyze_terraform_plan(self, repo_path: str) -> str:
        """
        Analyze Terraform plan for additional insights.
        This is a placeholder for future sophisticated features.
        """
        insights = []

        # Placeholder analysis features
        insights.append("Resource count analysis: Available in future release")
        insights.append("Security scanning: Available in future release")
        insights.append("Cost estimation: Available in future release")
        insights.append("Compliance checking: Available in future release")

        # Basic file structure analysis with fallback
        try:
            # Try find command first
            file_result = self.shell_agent.run(
                ShellAgentInput(
                    command="find . -name '*.tf' -exec basename {} \\; | sort | uniq -c",
                    cwd=repo_path,
                )
            )
            if file_result.exit_code == 0:
                insights.append(
                    f"Terraform files structure: {file_result.output.strip()}"
                )
            else:
                # Fallback to ls
                ls_result = self.shell_agent.run(
                    ShellAgentInput(
                        command="ls *.tf 2>/dev/null | wc -l || echo 0", cwd=repo_path
                    )
                )
                if ls_result.exit_code == 0:
                    count = ls_result.output.strip()
                    insights.append(f"Terraform files found: {count}")
        except Exception as e:
            insights.append(f"Could not analyze file structure: {e}")

        return " | ".join(insights)

    # --- LangGraph State Machine ---

    def _build_graph(self):
        """
        Build and compile the LangGraph state machine.
        Creates nodes for planner and each workflow step, sets up organic routing.
        """
        graph_builder = StateGraph(SupervisorAgentState)

        # Add nodes
        graph_builder.add_node("planner_llm", self._planner_llm_node)
        graph_builder.add_node("clone_repo_node", self._clone_repo_node)
        graph_builder.add_node("stack_detect_node", self._stack_detect_node)
        graph_builder.add_node("terraform_workflow_node", self._terraform_workflow_node)
        graph_builder.add_node("issue_create_node", self._issue_create_node)

        # Set entry point
        graph_builder.set_entry_point("planner_llm")

        # Configure routing map for planner
        planner_routing_map = {
            "clone_repo_node": "clone_repo_node",
            "stack_detect_node": "stack_detect_node",
            "terraform_workflow_node": "terraform_workflow_node",
            "issue_create_node": "issue_create_node",
            END: END,
        }

        # Configure routing map for workflow continuation
        workflow_routing_map = {
            "stack_detect_node": "stack_detect_node",
            "terraform_workflow_node": "terraform_workflow_node",
            "issue_create_node": "issue_create_node",
            END: END,
        }

        # Add conditional edges from planner (initial routing)
        graph_builder.add_conditional_edges(
            "planner_llm", self._route_after_planner, planner_routing_map
        )

        # Add conditional edges from workflow nodes (sequential continuation)
        graph_builder.add_conditional_edges(
            "clone_repo_node", self._route_workflow_continuation, workflow_routing_map
        )

        graph_builder.add_conditional_edges(
            "stack_detect_node", self._route_workflow_continuation, workflow_routing_map
        )

        graph_builder.add_conditional_edges(
            "terraform_workflow_node",
            self._route_workflow_continuation,
            workflow_routing_map,
        )

        # Issue creation always ends the workflow
        graph_builder.add_edge("issue_create_node", END)

        # Compile with checkpointer
        return graph_builder.compile(checkpointer=self.checkpointer)

    # --- Main Run Method: Organic LangGraph Execution ---

    def run(self, agent_input: SupervisorAgentInput) -> SupervisorAgentOutput:
        """
        Execute R2D workflow using organic LangGraph state machine.
        The LLM brain decides routing between specialized agents.
        """
        repo_url = agent_input.repo_url
        # Normalize the repository URL for issue creation
        normalized_repo_url = repo_url.rstrip("/").rstrip(".git")
        thread_id = agent_input.thread_id or str(uuid.uuid4())

        # Generate dynamic branch name if not provided
        branch_name = agent_input.branch_name or self._generate_dynamic_branch_name()

        # If initialization failed due to missing secrets, abort early
        if self.startup_error:
            self.logger.error(
                f"Cannot start workflow for {repo_url}: {self.startup_error}"
            )

            issues_opened = 0
            try:
                issue_result = self.git_agent.run(
                    GitAgentInput(
                        query=(
                            f"open issue for repository {normalized_repo_url}: 🚫 Missing token - {self.startup_error}"
                        )
                    )
                )
                startup_error_msg = issue_result.artifacts.get('error_message') if issue_result.artifacts else None
                if not startup_error_msg:
                    issues_opened = 1
            except Exception as e:
                self.logger.error(
                    f"Failed to invoke GitAgent for missing token issue: {e}"
                )

            output = SupervisorAgentOutput(
                repo_url=repo_url,
                branch_created=False,
                branch_name=branch_name,
                stack_detected={},
                terraform_summary=None,
                unsupported=False,
                issues_opened=issues_opened,
                success=False,
                message=self.startup_error
                + (" (GitHub issue created)" if issues_opened else " (GitHub issue creation also failed)")
            )
            log_event(
                "supervisor_agent_run_end",
                repo_url=repo_url,
                thread_id=thread_id,
                success=False,
                error=self.startup_error,
            )
            return output

        self.logger.info(f"Starting R2D workflow for {repo_url}, branch: {branch_name}")
        log_event(
            "supervisor_agent_run_start",
            repo_url=repo_url,
            branch_name=branch_name,
            thread_id=thread_id,
        )

        # Handle PR merge context and old issue linking
        pr_merge_results = None
        current_commit_sha = None
        run_key = None
        
        # Extract commit SHA from PR merge context or generate from current state
        if self.pr_merge_context:
            current_commit_sha = self.pr_merge_context.get('merged_sha')
            self.logger.info(f"Using PR merge SHA: {current_commit_sha}")
            
            # Handle previous issue linking for PR merges
            pr_merge_results = self._handle_pr_merge_workflow(repo_url, current_commit_sha)
            if pr_merge_results:
                self.logger.info(f"PR merge workflow handled: {pr_merge_results}")
        else:
            # Generate a placeholder SHA for non-PR runs (this would be replaced by actual git SHA in real deployment)
            current_commit_sha = f"manual-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        # Create registry entry for this run
        try:
            job_name = self.pr_merge_context.get('pr_title', 'R2D Workflow') if self.pr_merge_context else 'Manual R2D Workflow'
            run_key = self.run_registry.create_run(
                repo_url=repo_url,
                commit_sha=current_commit_sha,
                job_name=job_name,
                thread_id=thread_id,
                branch_name=branch_name
            )
            self.logger.info(f"Created registry entry with run key: {run_key}")
            
            # Link to predecessor run if this is a PR merge
            if pr_merge_results and pr_merge_results.get('previous_run_key'):
                linked = self.run_registry.link_predecessor_run(
                    run_key, pr_merge_results['previous_run_key']
                )
                if linked:
                    self.logger.info(f"Linked to predecessor run: {pr_merge_results['previous_run_key']}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to create registry entry: {e}")

        # Handle PR merge workflow context if detected
        pr_merge_info = None
        if self.pr_merge_context:
            commit_sha = self.pr_merge_context.get('merged_sha', 'unknown')
            pr_merge_info = self._handle_pr_merge_workflow(repo_url, commit_sha)
            if pr_merge_info:
                self.logger.info(f"PR merge workflow initiated: {pr_merge_info['commit_sha']} follows {pr_merge_info['previous_issue_id']}")

        # Create initial state
        initial_state: SupervisorAgentState = {
            "input_message": HumanMessage(
                content=f"Execute R2D workflow for repository {repo_url}"
            ),
            "repo_url": repo_url,
            "branch_name": branch_name,
            "thread_id": thread_id,
            "dry_run": agent_input.dry_run,
            "repo_path": None,
            "stack_detected": {},
            "branch_created": False,
            "final_result": "",
            "operation_type": "",
            "terraform_summary": None,
            "issues_opened": 0,
            "unsupported": False,
            "error_message": None,
            "tool_output": [],
        }

        try:
            # Execute the LangGraph workflow
            self.logger.info("Executing organic LangGraph R2D workflow")
            final_state = self.runnable.invoke(
                initial_state, {"configurable": {"thread_id": thread_id}}
            )

            # Extract results from final state
            operation_type = final_state.get("operation_type", "")
            issues_opened = final_state.get("issues_opened", 0)

            # Determine success: workflow succeeds only if terraform completes without issues
            # If issues were opened, it means there was a failure somewhere in the workflow
            success = (
                final_state.get("error_message") is None
                and issues_opened == 0
                and operation_type != "issue_success"
            )

            message = final_state.get("final_result", "R2D workflow completed")

            output = SupervisorAgentOutput(
                repo_url=repo_url,
                branch_created=final_state.get("branch_created", False),
                branch_name=final_state.get("branch_name", branch_name),
                stack_detected=final_state.get("stack_detected", {}),
                terraform_summary=final_state.get("terraform_summary"),
                unsupported=final_state.get("unsupported", False),
                issues_opened=issues_opened,
                success=success,
                message=message,
            )

            log_event(
                "supervisor_agent_run_end",
                repo_url=repo_url,
                thread_id=thread_id,
                success=success,
            )

            return output

        except Exception as e:
            self.logger.error(f"R2D workflow execution failed: {e}", exc_info=True)

            # Enhanced error handling: Automatically create GitHub issue for ANY workflow failure
            issues_opened = 0
            try:
                self.logger.info(
                    "Attempting to create GitHub issue for workflow execution failure"
                )

                # Import text utilities for error handling
                from diagram_to_iac.tools.text_utils import (
                    generate_organic_issue_title,
                    enhance_error_message_for_issue,
                    create_issue_metadata_section,
                )

                # Determine error type for better title generation
                error_message = str(e)
                error_type = "workflow_error"
                if "api key" in error_message.lower() or "401" in error_message.lower():
                    error_type = "api_key_error"
                elif (
                    "llm" in error_message.lower() or "openai" in error_message.lower()
                ):
                    error_type = "llm_error"
                elif (
                    "network" in error_message.lower()
                    or "connection" in error_message.lower()
                ):
                                       error_type = "network_error"
                elif "timeout" in error_message.lower():
                    error_type = "timeout_error"
                elif (
                    "permission" in error_message.lower()
                    or "forbidden" in error_message.lower()
                ):
                    error_type = "permission_error"

                # Create context for organic title generation
                error_context = {
                    "error_type": error_type,
                    "stack_detected": {},
                    "error_message": error_message,
                    "repo_url": repo_url,
                    "branch_name": branch_name,
                }

                # Generate organic, thoughtful issue title
                issue_title = generate_organic_issue_title(error_context)

                # Create enhanced issue body with metadata and clean error formatting
                metadata_section = create_issue_metadata_section(error_context)

                enhanced_error = enhance_error_message_for_issue(error_message, error_context)
                
                issue_body = f"{metadata_section}{enhanced_error}\n\n**Workflow Stage:** Initial workflow execution\n**Error Type:** Critical system error preventing R2D workflow startup"
                
                if agent_input.dry_run:
                    if self.demonstrator:
                        self.demonstrator.show_issue(issue_title, issue_body)
                    else:
                        self.logger.info(f"DRY RUN: GitHub issue processing for: Title: {issue_title}")
                        print("=== DRY RUN: GitHub issue would be created/checked ===")
                        print(f"Title: {issue_title}")
                        print(f"Body:\n{issue_body}")
                else:
                    # Create or update GitHub issue for workflow failure
                    existing_id = self._get_existing_issue_id(repo_url, error_type)
                    git_input = GitAgentInput(
                        query=f"open issue {issue_title} for repository {repo_url}: {issue_body}",
                        issue_id=existing_id,
                    )
                    issue_result = self.git_agent.run(git_input)
                    error_msg_from_artifacts = issue_result.artifacts.get('error_message') if issue_result.artifacts else None
                    if not error_msg_from_artifacts:
                        issues_opened = 1
                        # Record new issue id if created
                        if existing_id is None:
                            new_id = self._parse_issue_number(issue_result.summary)
                            if new_id is not None:
                                self._record_issue_id(repo_url, error_type, new_id)

                        self.logger.info(f"Successfully created GitHub issue for workflow failure: {issue_result.summary}")
                    else:
                        issue_error_msg = issue_result.artifacts.get('error_message') if issue_result.artifacts else "Unknown error"
                        self.logger.warning(f"Failed to create GitHub issue for workflow failure: {issue_error_msg}")
                    

            except Exception as issue_error:
                self.logger.error(
                    f"Failed to create GitHub issue for workflow failure: {issue_error}"
                )

            output = SupervisorAgentOutput(
                repo_url=repo_url,
                branch_created=False,
                branch_name=branch_name,
                stack_detected={},
                terraform_summary=None,
                unsupported=False,  # Changed: Don't mark as unsupported, this is a system error
                issues_opened=issues_opened,
                success=False,
                message=f"Workflow execution failed: {str(e)}"
                + (
                    f" (GitHub issue created)"
                    if issues_opened > 0
                    else " (GitHub issue creation also failed)"
                ),
            )
            log_event(
                "supervisor_agent_run_end",
                repo_url=repo_url,
                thread_id=thread_id,
                success=False,
                error=str(e),
            )
            return output

    def resume_workflow(self, run_key: str, commit_sha: str) -> SupervisorAgentOutput:
        """
        Resume a workflow from a previous state using the run registry.
        
        Args:
            run_key: The unique identifier for the workflow run to resume
            commit_sha: The commit SHA to use for the resumed workflow
            
        Returns:
            SupervisorAgentOutput: Result of the resumed workflow
        """
        self.logger.info(f"Resuming workflow for run_key: {run_key}, commit_sha: {commit_sha}")
        
        try:
            # Get the existing run from registry
            existing_run = self.run_registry.get_run(run_key)
            if not existing_run:
                self.logger.error(f"No run found for key: {run_key}")
                return SupervisorAgentOutput(
                    repo_url="unknown",
                    branch_created=False,
                    branch_name="unknown",
                    stack_detected={},
                    terraform_summary=None,
                    unsupported=False,
                    issues_opened=0,
                    success=False,
                    message=f"No existing run found for key: {run_key}"
                )
            
            # Update run status to IN_PROGRESS
            self.run_registry.update(run_key, {
                'status': 'IN_PROGRESS',
                'commit_sha': commit_sha,
                'wait_reason': None
            })
            
            # Create a new SupervisorAgentInput based on the existing run data
            resume_input = SupervisorAgentInput(
                repo_url=existing_run.repo_url,
                branch_name=existing_run.branch_name,
                thread_id=existing_run.thread_id,
                dry_run=False  # Assume production run for resume
            )
            
            self.logger.info(f"Resuming workflow for repo: {existing_run.repo_url}")
            
            # Run the workflow with the restored input
            # The workflow will naturally continue from where it left off
            # based on the state preserved in memory and registry
            result = self.run(resume_input)
            
            # Update registry with final status
            final_status = 'COMPLETED' if result.success else 'FAILED'
            self.run_registry.update(run_key, {
                'status': final_status,
                'issues_opened': result.issues_opened,
                'terraform_summary': result.terraform_summary
            })
            
            self.logger.info(f"Workflow resumption {'successful' if result.success else 'failed'} for run_key: {run_key}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error resuming workflow for run_key {run_key}: {e}")
            
            # Update registry with error status
            self.run_registry.update(run_key, {
                'status': 'FAILED',
                'wait_reason': f"Resume error: {str(e)}"
            })
            
            return SupervisorAgentOutput(
                repo_url=existing_run.repo_url if 'existing_run' in locals() else "unknown",
                branch_created=False,
                branch_name=existing_run.branch_name if 'existing_run' in locals() else "unknown",
                stack_detected={},
                terraform_summary=None,
                unsupported=False,
                issues_opened=0,
                success=False,
                message=f"Workflow resumption failed: {str(e)}"
            )

    # --- Memory and Conversation Management ---

    def get_conversation_history(self) -> List[Dict[str, any]]:
        """Get conversation history from memory."""
        try:
            return self.memory.get_conversation_history()
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            return []

    def get_memory_state(self) -> Dict[str, any]:
        """Get current memory state."""
        try:
            return {
                "conversation_history": self.get_conversation_history(),
                "memory_type": type(self.memory).__name__,
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory state: {e}")
            return {"error": str(e)}


def detect_stack_files(repo_path: str, shell_agent: ShellAgent) -> Dict[str, int]:
    """Detect basic stack files (.tf and .sh) in the given repository."""
    # Check if repo_path exists before proceeding
    if not os.path.exists(repo_path):
        raise RuntimeError(f"Repository path does not exist: {repo_path}")
    
    patterns = ["*.tf", "*.sh"]
    detected: Dict[str, int] = {}

    for pattern in patterns:
        count = 0
        try:
            result = shell_agent.run(
                ShellAgentInput(
                    command=f"bash -c \"find . -name '{pattern}' -type f | wc -l\"",
                    cwd=repo_path,
                )
            )
            if result.exit_code == 0:
                count = int(result.output.strip())
            else:
                raise RuntimeError(result.error_message or "find failed")
        except Exception:
            # Fallback to Python-based search
            for root, _, files in os.walk(repo_path):
                count += len(fnmatch.filter(files, pattern))

        if count > 0:
            detected[pattern] = count

    return detected
