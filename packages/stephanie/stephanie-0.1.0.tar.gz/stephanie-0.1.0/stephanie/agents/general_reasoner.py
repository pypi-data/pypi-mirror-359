from stephanie.agents.base_agent import BaseAgent
from stephanie.agents.mixins.scoring_mixin import ScoringMixin
from stephanie.analysis.rubric_classifier import RubricClassifierMixin
from stephanie.constants import GOAL, GOAL_TEXT


class GeneralReasonerAgent(ScoringMixin, RubricClassifierMixin, BaseAgent):
    def __init__(self, cfg, memory, logger):
        super().__init__(cfg, memory, logger)

    async def run(self, context: dict) -> dict:
        goal = context.get(GOAL)

        self.logger.log("AgentRunStarted", {"goal": goal})

        # Generate hypotheses (if needed)
        if self.cfg.get("thinking_mode") == "generate_and_judge":
            hypotheses = self.generate_hypotheses(context)
        else:
            hypotheses = self.get_hypotheses(context)

        context["hypotheses"] = hypotheses
        context["scoring"] = []

        dimension_scores = []
        for hyp in hypotheses:
            scored = self.score_hypothesis(hyp, context, metrics="reasoning_cor")
            hyp["final_score"] = scored.aggregate()
            hyp["dimension_scores"] = scored.to_dict()
            dimension_scores.append(scored.to_dict())
        context["dimension_scores"] = dimension_scores


        best_hypothesis = max(hypotheses, key=lambda h: h["final_score"])
        
        # Classify with rubrics and store pattern stats
        pattern = self.classify_with_rubrics(
            hypothesis=best_hypothesis,
            context=context,
            prompt_loader=self.prompt_loader,
            cfg=self.cfg,
            logger=self.logger
        )


        summarized = self._summarize_pattern(pattern)
        context["pattern"] = summarized

        pattern_stats = self.generate_pattern_stats(
            goal=goal,
            hypothesis=best_hypothesis,
            pattern_dict=summarized,
            cfg=self.cfg,
            agent_name=self.name,
            confidence_score=best_hypothesis.get("confidence")
        )

        self.memory.pattern_stats.insert(pattern_stats)
        context["pattern_stats"] = summarized

        context[self.output_key] = best_hypothesis
        context["ranked_hypotheses"] = sorted(hypotheses, key=lambda h: h["final_score"], reverse=True)

        return context

    def generate_hypotheses(self, context: dict) -> list[dict]:
        """Generates multiple hypotheses using different strategies"""
        goal = context.get(GOAL)
        question = goal.get(GOAL_TEXT)

        strategies = self.cfg.get("generation_strategy_list", ["cot"])
        merged = {**context, "question": question}

        hypotheses = []
        for strategy in strategies:
            prompt = self.prompt_loader.from_file(
                f"strategy_{strategy}.txt", self.cfg, merged
            )
            response = self.call_llm(prompt, merged)
            hypothesis = self.save_hypothesis(
                {
                    "text": response,
                    "strategy": strategy,
                    "features": {"strategy": strategy},
                    "source": self.name,
                },
                context=context,
            )

            hypotheses.append(hypothesis.to_dict())
        return hypotheses

    def _summarize_pattern(self, pattern: dict):
        stats = {}
        for dimension, label in pattern.items():
            stats[label] = stats.get(label, 0) + 1
        return stats
