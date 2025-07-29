# Copyright (c) 2025 Microsoft Corporation.
"""Module for generating personas, tasks, and entities for activity question generation in AutoQ."""

import asyncio
import json
import logging
import uuid
from pathlib import Path
from string import Template
from typing import Any

import tiktoken

import benchmark_qed.config.defaults as defs
from benchmark_qed.autod.data_model.text_unit import TextUnit
from benchmark_qed.autod.data_processor.embedding import TextEmbedder
from benchmark_qed.autod.data_processor.text_utils import try_parse_json_object
from benchmark_qed.autod.summarization.base import BaseSummarizer
from benchmark_qed.autod.summarization.global_summarizer import GlobalSummarizer
from benchmark_qed.autoq.data_model.activity import ActivityContext, TaskContext
from benchmark_qed.autoq.prompts.activity_questions import activity_context
from benchmark_qed.autoq.question_gen.activity_questions.context_gen.entity_extractor import (
    EntityExtractor,
)
from benchmark_qed.config.utils import load_template_file
from benchmark_qed.llm.type.base import ChatModel

log: logging.Logger = logging.getLogger(__name__)

CONTEXT_PROMPTS = Path(activity_context.__file__).parent


class ActivityContextGen:
    """Class to generate personas, tasks, and entities for activity question generation."""

    def __init__(
        self,
        llm: ChatModel,
        text_embedder: TextEmbedder,
        text_units: list[TextUnit],
        token_encoder: tiktoken.Encoding | None = None,
        data_summarizer: BaseSummarizer | None = None,
        entity_extractor: EntityExtractor | None = None,
        activity_identification_prompt: Template | None = None,
        map_system_prompt: Template | None = None,
        map_user_prompt: Template | None = None,
        reduce_system_prompt: Template | None = None,
        reduce_user_prompt: Template | None = None,
        entity_extractor_map_system_prompt: Template | None = None,
        entity_extractor_map_user_prompt: Template | None = None,
        entity_extractor_reduce_system_prompt: Template | None = None,
        entity_extractor_reduce_user_prompt: Template | None = None,
        llm_params: dict[str, Any] = defs.LLM_PARAMS,
        concurrent_coroutines: int = 32,
        json_mode: bool = True,
    ) -> None:
        self.llm = llm
        self.text_embedder = text_embedder
        self.text_units = text_units
        self.token_encoder = token_encoder
        self.llm_params = llm_params
        self.activity_identification_prompt: Template = (
            activity_identification_prompt
            or load_template_file(
                CONTEXT_PROMPTS / "activity_identification_prompt.txt"
            )
        )
        self.concurrent_coroutines = concurrent_coroutines
        self.json_mode = json_mode
        if json_mode:
            self.llm_params["response_format"] = {"type": "json_object"}
        else:
            self.llm_params.pop("response_format", None)

        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(concurrent_coroutines)

        if data_summarizer is not None:
            self.data_summarizer: BaseSummarizer = data_summarizer
        else:
            self.data_summarizer: BaseSummarizer = GlobalSummarizer(
                llm=llm,
                map_system_prompt=map_system_prompt,
                map_user_prompt=map_user_prompt,
                reduce_system_prompt=reduce_system_prompt,
                reduce_user_prompt=reduce_user_prompt,
                token_encoder=token_encoder,
                map_llm_params=llm_params,
                reduce_llm_params=llm_params,
                concurrent_coroutines=concurrent_coroutines,
            )

        if entity_extractor is not None:
            self.entity_extractor: EntityExtractor = entity_extractor
        else:
            self.entity_extractor: EntityExtractor = EntityExtractor(
                llm=llm,
                token_encoder=token_encoder,
                map_llm_params=llm_params,
                reduce_llm_params=llm_params,
                concurrent_coroutines=concurrent_coroutines,
                map_system_prompt=entity_extractor_map_system_prompt,
                map_user_prompt=entity_extractor_map_user_prompt,
                reduce_system_prompt=entity_extractor_reduce_system_prompt,
                reduce_user_prompt=entity_extractor_reduce_user_prompt,
            )

    async def agenerate(
        self,
        num_personas: int = 5,
        num_tasks: int = 5,
        num_entities_per_task: int = 5,
        include_entity_description: bool = True,
        oversample_factor: float = defs.OVERSAMPLE_FACTOR,
        use_representative_samples_only: bool = True,
    ) -> ActivityContext:
        """Generate personas, associated tasks, and entities for generating activity-based questions."""
        # if use_representative_samples_only is True, filter text_units to only include representative samples
        if use_representative_samples_only:
            rep_text_units = [
                text_unit
                for text_unit in self.text_units
                if text_unit.attributes is not None
                and text_unit.attributes.get("is_representative", True)
            ]
            if len(rep_text_units) == 0:
                log.warning(
                    "No representative samples found. Using all text units instead."
                )
                rep_text_units = self.text_units
        else:
            rep_text_units = self.text_units

        # generate dataset description
        msg = f"Generating dataset summary from {len(rep_text_units)} representative texts..."
        log.info(msg)
        dataset_description = await self.data_summarizer.asummarize(
            text_units=rep_text_units
        )
        summary_str = (
            dataset_description.summary
            if isinstance(dataset_description.summary, str)
            else json.dumps(dataset_description.summary)
        )
        msg = f"Dataset summary: {summary_str}"
        log.info(msg)

        # generate personas and tasks
        # oversample to account for tasks that do not have relevant entities
        activity_messages = [
            {
                "role": "system",
                "content": self.activity_identification_prompt.substitute(
                    user_count=int(num_personas * oversample_factor),
                    task_count=num_tasks,
                    dataset_description=summary_str,
                ),
            },
        ]
        activities_response = await self.llm.chat(
            messages=activity_messages, **self.llm_params
        )
        parsed_activities, j = try_parse_json_object(activities_response.output.content)
        if j == {}:
            msg = f"Failed to parse activities response: {activities_response.output.content}"
            log.warning(msg)
            return ActivityContext(dataset_description=summary_str, task_contexts=[])

        parsed_activities = json.loads(parsed_activities)

        persona_tasks = []
        for activity in parsed_activities.get("personas", []):
            persona = activity.get("persona", "")
            if persona != "":
                tasks = activity.get("tasks", [])
                persona_tasks.extend(
                    {"persona": persona, "task": task} for task in tasks
                )
        msg = f"Generated {len(persona_tasks)} tasks."
        log.info(msg)

        if not include_entity_description:
            task_contexts = [
                TaskContext(
                    persona=activity["persona"], task=activity["task"], entities=[]
                )
                for activity in persona_tasks
            ]
        else:
            msg = f"Extracting entities for {len(persona_tasks)} tasks..."
            log.info(msg)
            task_contexts = []
            for i in range(0, len(persona_tasks), self.concurrent_coroutines):
                batch = persona_tasks[i : i + self.concurrent_coroutines]
                batch_results = await asyncio.gather(*[
                    self._aextract_entities(
                        text_units=rep_text_units,
                        persona=activity["persona"],
                        num_entities=num_entities_per_task,
                        task=activity["task"],
                    )
                    for activity in batch
                ])
                task_contexts.extend(batch_results)

            # filter out tasks that do not have entities, which is indication that the task is not relevant
            task_contexts = [
                task_context
                for task_context in task_contexts
                if len(task_context.entities) > 0
            ]
        return ActivityContext(
            dataset_description=summary_str, task_contexts=task_contexts
        )

    async def _aextract_entities(
        self,
        text_units: list[TextUnit],
        persona: str,
        task: str,
        num_entities: int = 5,
    ) -> TaskContext:
        """Extract entities from the persona and task descriptions."""
        async with self.semaphore:
            extraction_result = await self.entity_extractor.aextract(
                text_units=text_units,
                persona=persona,
                task=task,
                num_entities=num_entities,
            )
            if (
                extraction_result.entities is None
                or len(extraction_result.entities) == 0
            ):
                msg = f"No entities found for persona: {persona}, task: {task}"
                log.warning(msg)
                return TaskContext(persona=persona, task=task, entities=[])
            # embed all entities in extraction_result.entities
            entities = extraction_result.entities
            entity_text_units = [
                TextUnit(
                    text=entity.to_str(), id=str(uuid.uuid4()), short_id=str(index)
                )
                for index, entity in enumerate(entities)
            ]
            entity_text_embeddings = await self.text_embedder.embed_batch(
                entity_text_units
            )

            for entity, embedding in zip(
                entities, entity_text_embeddings, strict=False
            ):
                entity.embedding = embedding.text_embedding
            return TaskContext(persona=persona, task=task, entities=entities)
