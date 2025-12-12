"""Council agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .base import Agent
from ..core.llm_router import get_llm_router
from ..core.state import NexusFactoryState
from ..integrations.memory import NexusMemory
from ..integrations.github_client import GitHubClient
from ..utils.tokens import update_token_usage
from ..utils.status import save_status_snapshot
from ..config import get_settings


@dataclass
class ReviewerOpinion:
    """Structure for a reviewer's opinion."""
    
    reviewer: str
    model: str
    score: int
    reasoning: str
    concerns: List[str]


class CouncilAgent(Agent):
    """The Council: Validates quality and decides next step."""
    
    def __init__(self):
        """Initialize Council agent."""
        super().__init__()
        settings = get_settings()
        self.memory = NexusMemory(memory_path=settings.memory_file)
        self.github_client: GitHubClient | None = None
        self.settings = settings
    
    def _get_github_client(self) -> GitHubClient:
        """Get or create GitHub client."""
        if self.github_client is None:
            self.github_client = GitHubClient()
        return self.github_client
    
    def execute(self, state: NexusFactoryState) -> Dict[str, Any]:
        """
        Review code quality using multi-LLM debate system.
        
        Phase 1: Get independent reviews from Grok, Gemini, and Claude
        Phase 2: Final arbitration by Claude based on all opinions
        
        Args:
            state: Current factory state
        
        Returns:
            State updates with quality score and detailed feedback
        """
        self.log_execution("Starting multi-LLM council review")
        
        env = state.get("env_mode", "DEV")
        spec = state.get("spec_document", "")
        
        # Phase 1: Get independent reviews from each model
        self.log_execution("Phase 1: Gathering independent reviews")
        opinions = self._gather_independent_reviews(spec)
        
        # Phase 2: Final arbitration by Claude
        self.log_execution("Phase 2: Final arbitration")
        final_score, arbitration_reasoning, usage_total = self._arbitrate_reviews(
            spec, opinions
        )
        
        # Generate detailed report
        report = self._generate_report(opinions, final_score, arbitration_reasoning)
        self.logger.info(f"\n{report}")
        
        new_tokens = update_token_usage(state.get("total_tokens", {}), usage_total)
        
        self.logger.info(f"Final quality score: {final_score}/100")
        
        # Check for approval
        is_approved = (
            (env == "DEV" and final_score > self.settings.dev_quality_threshold) or
            (env == "PROD" and final_score > self.settings.prod_quality_threshold)
        )
        
        if is_approved:
            self.log_execution("APPROVAL GRANTED - Archiving lesson")
            
            # Store lesson in memory
            try:
                self.memory.store_lesson(
                    topic="Feature Implementation",
                    context=spec[:50] + "...",
                    outcome="Success",
                    solution=f"Multi-LLM review: {final_score}/100 - {arbitration_reasoning[:100]}"
                )
            except Exception as e:
                self.logger.error(f"Failed to store lesson: {e}")
            
            # Push to GitHub
            self._push_to_github(env)
        else:
            self.log_execution(
                f"Quality threshold not met ({final_score}). Requesting revision."
            )
        
        state_update = {
            "current_status": "Agent: The Council (Multi-LLM Review Complete)",
            "quality_score": final_score,
            "council_report": report,
            "feedback_loop_count": state.get("feedback_loop_count", 0) + 1,
            "total_tokens": new_tokens
        }
        
        save_status_snapshot({**state, **state_update})
        
        return state_update
    
    def _gather_independent_reviews(self, spec: str) -> List[ReviewerOpinion]:
        """
        Gather independent reviews from Grok, Gemini, and Claude.
        
        Args:
            spec: The specification to review
        
        Returns:
            List of ReviewerOpinion objects
        """
        router = get_llm_router()
        opinions = []
        
        # Define reviewers with their agent names
        reviewers = [
            ("GPT-4", "council_gpt4"),
            ("Gemini", "council_gemini"),
            ("Claude", "council_claude")
        ]
        
        review_prompt_template = """You are a strict code auditor reviewing a specification.

SPECIFICATION:
{spec}

EVALUATION CRITERIA:
1. Clarity - Is the specification clear and unambiguous?
2. Security - Does it address security concerns?
3. Robustness - Is it designed for reliability and edge cases?
4. Completeness - Are all necessary details included?

Provide your review in this exact format:
SCORE: [integer 0-100]
REASONING: [1-2 sentences explaining your score]
CONCERNS: [comma-separated list of specific concerns, or "None"]"""
        
        for reviewer_name, agent_name in reviewers:
            try:
                response, _ = router.call(
                    prompt=review_prompt_template.format(spec=spec[:1500]),
                    agent_name=agent_name,
                    system_prompt="You are a strict code auditor. Be thorough and critical."
                )
                
                # Parse the response
                score = self._extract_score(response)
                reasoning = self._extract_reasoning(response)
                concerns = self._extract_concerns(response)
                
                # Get model name from router
                config = router.AGENT_MODEL_MAPPING.get(agent_name)
                model = config.provider.value if config else "unknown"
                
                opinion = ReviewerOpinion(
                    reviewer=reviewer_name,
                    model=model,
                    score=score,
                    reasoning=reasoning,
                    concerns=concerns
                )
                opinions.append(opinion)
                
                self.logger.info(
                    f"{reviewer_name} ({model}): Score={score}, "
                    f"Concerns={len(concerns)}"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to get review from {reviewer_name}: {e}")
                # Add a default opinion to continue
                opinions.append(ReviewerOpinion(
                    reviewer=reviewer_name,
                    model="error",
                    score=50,
                    reasoning=f"Review failed: {str(e)[:50]}",
                    concerns=["Review error"]
                ))
        
        return opinions
    
    def _arbitrate_reviews(
        self,
        spec: str,
        opinions: List[ReviewerOpinion]
    ) -> Tuple[int, str, Dict[str, int]]:
        """
        Use Claude to arbitrate between the different reviews.
        
        Args:
            spec: The specification being reviewed
            opinions: List of reviewer opinions
        
        Returns:
            Tuple of (final_score, reasoning, token_usage)
        """
        router = get_llm_router()
        
        # Prepare opinions summary
        opinions_text = "\n\n".join([
            f"**{op.reviewer} ({op.model})**\n"
            f"Score: {op.score}/100\n"
            f"Reasoning: {op.reasoning}\n"
            f"Concerns: {', '.join(op.concerns)}"
            for op in opinions
        ])
        
        arbitration_prompt = f"""You are the lead arbitrator in a code review council.

Three expert reviewers have evaluated a specification. Your job is to synthesize their 
opinions and provide a final, definitive quality score.

SPECIFICATION EXCERPT:
{spec[:800]}

REVIEWER OPINIONS:
{opinions_text}

Consider:
- Areas of agreement and disagreement
- Severity of concerns raised
- Overall consensus
- Your own expert judgment

Provide your arbitration in this exact format:
FINAL_SCORE: [integer 0-100]
REASONING: [2-3 sentences explaining your final decision]"""
        
        try:
            response, usage = router.call(
                prompt=arbitration_prompt,
                agent_name="council_claude",
                system_prompt="You are the lead arbitrator. Synthesize opinions objectively."
            )
            
            final_score = self._extract_score(response)
            reasoning = self._extract_reasoning(response)
            
            return final_score, reasoning, usage
            
        except Exception as e:
            self.logger.error(f"Arbitration failed: {e}")
            # Fallback: use average of reviewer scores
            avg_score = sum(op.score for op in opinions) // len(opinions)
            return avg_score, f"Arbitration failed, using average: {e}", {}
    
    def _extract_score(self, response: str) -> int:
        """Extract numeric score from LLM response."""
        try:
            # Look for SCORE: or FINAL_SCORE:
            for line in response.split('\n'):
                if 'SCORE:' in line.upper() or 'FINAL_SCORE:' in line.upper():
                    # Extract digits
                    score_str = ''.join(filter(str.isdigit, line))
                    if score_str:
                        return min(100, max(0, int(score_str)))
            
            # Fallback: extract any number
            score_str = ''.join(filter(str.isdigit, response[:200]))
            if score_str:
                return min(100, max(0, int(score_str)))
            
            return 70  # Default
            
        except (ValueError, AttributeError):
            return 70
    
    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning from LLM response."""
        try:
            lines = response.split('\n')
            for i, line in enumerate(lines):
                if 'REASONING:' in line.upper():
                    # Get the reasoning part (may span multiple lines)
                    reasoning_parts = [line.split(':', 1)[1].strip()]
                    # Get subsequent lines until we hit another field
                    for next_line in lines[i+1:]:
                        if ':' in next_line and next_line.split(':')[0].strip().isupper():
                            break
                        if next_line.strip():
                            reasoning_parts.append(next_line.strip())
                    return ' '.join(reasoning_parts)
            
            # Fallback: return first substantial line
            for line in lines:
                if len(line.strip()) > 20:
                    return line.strip()[:200]
            
            return "No reasoning provided"
            
        except Exception:
            return "Failed to extract reasoning"
    
    def _extract_concerns(self, response: str) -> List[str]:
        """Extract concerns from LLM response."""
        try:
            for line in response.split('\n'):
                if 'CONCERNS:' in line.upper():
                    concerns_text = line.split(':', 1)[1].strip()
                    if concerns_text.lower() == 'none':
                        return []
                    # Split by comma and clean up
                    concerns = [c.strip() for c in concerns_text.split(',')]
                    return [c for c in concerns if c]
            
            return []
            
        except Exception:
            return []
    
    def _generate_report(
        self,
        opinions: List[ReviewerOpinion],
        final_score: int,
        arbitration: str
    ) -> str:
        """
        Generate a detailed report with opinion table.
        
        Args:
            opinions: List of reviewer opinions
            final_score: Final arbitrated score
            arbitration: Arbitration reasoning
        
        Returns:
            Formatted report string
        """
        report_lines = [
            "\n" + "="*70,
            "COUNCIL MULTI-LLM REVIEW REPORT",
            "="*70,
            "",
            "INDIVIDUAL REVIEWS:",
            "-"*70
        ]
        
        # Add table header
        report_lines.extend([
            f"{'Reviewer':<15} {'Model':<20} {'Score':<8} {'Concerns':<10}",
            "-"*70
        ])
        
        # Add reviewer rows
        for op in opinions:
            concerns_count = len(op.concerns) if op.concerns else 0
            report_lines.append(
                f"{op.reviewer:<15} {op.model:<20} {op.score:>3}/100   {concerns_count:>2}"
            )
        
        report_lines.extend([
            "-"*70,
            "",
            "DETAILED OPINIONS:",
            "-"*70
        ])
        
        # Add detailed opinions
        for op in opinions:
            report_lines.extend([
                f"\n{op.reviewer} ({op.model}):",
                f"  Score: {op.score}/100",
                f"  Reasoning: {op.reasoning}",
                f"  Concerns: {', '.join(op.concerns) if op.concerns else 'None'}",
            ])
        
        report_lines.extend([
            "",
            "-"*70,
            "FINAL ARBITRATION (Claude):",
            "-"*70,
            f"Final Score: {final_score}/100",
            f"Reasoning: {arbitration}",
            "="*70,
            ""
        ])
        
        return '\n'.join(report_lines)
    
    def _push_to_github(self, env: str) -> None:
        """
        Push generated files to GitHub.
        
        Args:
            env: Current environment mode
        """
        try:
            github_client = self._get_github_client()
            repo = github_client.get_or_create_repo("nexus-prime-workspace")
            
            # Push workspace files
            workspace_dir = self.settings.workspace_dir
            files = ["app_dev.py", "app_prod.py"]
            
            for fname in files:
                fpath = os.path.join(workspace_dir, fname)
                if os.path.exists(fpath):
                    github_client.push_local_file(
                        repo,
                        fpath,
                        fname,
                        f"Update {fname} by NexusPrime"
                    )
            
            self.log_execution("Files pushed to GitHub successfully")
            
        except Exception as e:
            self.logger.error(f"GitHub push failed: {e}")
