#!/usr/bin/env python3

"""
Relationship YAML generation for creating OpenDD relationship definitions.
Converts detected relationships into proper YAML relationship structures.
Only generates relationships between ObjectTypes that are queryable (have Models or Query Commands).

KEY CHANGES:
1. Target-aware relationship naming to prevent duplicates
2. Improved conflict resolution with target entity context
3. Better handling of multiple targets for the same field
4. CRITICAL: Enhanced validation to prevent Commands from being relationship targets
5. ADDED: Centralized validation matching detector logic for all generation paths
"""

import logging
import os
import re
from typing import Dict, List, Any, Optional, Set, Tuple

from ..config import config
from ..utils.text_utils import to_camel_case, smart_pluralize

logger = logging.getLogger(__name__)


def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case.

    Examples:
    - entityApplicationsByPubliclyAccessible -> entity_applications_by_publicly_accessible
    - BusinessApplication -> business_application
    - userId -> user_id

    Args:
        text: Input text to convert

    Returns:
        snake_case version of the text
    """
    if not text:
        return text

    # Handle camelCase/PascalCase by inserting underscores before capitals
    # First, handle sequences of capitals (like XMLHttp -> xml_http)
    snake_text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', text)
    # Then handle lowercase followed by uppercase
    snake_text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', snake_text)

    # Convert to lowercase and clean up multiple underscores
    snake_text = snake_text.lower()
    snake_text = re.sub(r'_+', '_', snake_text)  # Replace multiple underscores with single
    snake_text = snake_text.strip('_')  # Remove leading/trailing underscores

    return snake_text


def smart_pluralize_snake(text: str) -> str:
    """
    Apply smart pluralization to snake_case text.

    Args:
        text: snake_case text to pluralize

    Returns:
        Pluralized snake_case text
    """
    if not text:
        return text

    # Split on underscores, pluralize the last word, rejoin
    parts = text.split('_')
    if parts:
        # Use the existing smart_pluralize on the last word (convert to camelCase temporarily)
        last_word_camel = to_camel_case(parts[-1], first_char_lowercase=True)
        pluralized_camel = smart_pluralize(last_word_camel)
        # Convert back to snake_case
        parts[-1] = to_snake_case(pluralized_camel)

    return '_'.join(parts)


class RelationshipGenerator:
    """
    Generates YAML relationship definitions from detected relationship patterns.

    This class takes the output from relationship detection and creates properly
    formatted OpenDD Relationship kind definitions that can be added to schema files.
    Only generates relationships between ObjectTypes that are queryable (have Models or Query Commands).
    """

    # Static class variable to track used relationship names across all instances
    _used_names_per_entity: Dict[str, Set[str]] = {}

    def __init__(self):
        """Initialize the relationship generator.

        Args:
            input_dir: Base directory for schema files (required for YAML validation)
        """
        self.generated_relationships: List[Dict[str, Any]] = []
        self.relationship_signatures: Set[Tuple] = set()
        self.input_dir = config.input_dir

    def _is_valid_relationship_target(self, target_qnk: str, target_info: Dict) -> bool:
        """
        Check if entity can be a valid relationship target.

        CRITICAL: Re-reads original YAML files to make validation decisions,
        bypassing potentially corrupted processed metadata.

        Args:
            target_qnk: Qualified name of target entity
            target_info: Target entity information (used for file path only)

        Returns:
            True if entity can be a relationship target, False otherwise

        Raises:
            Exception: If YAML file cannot be read (fatal - no fallback to processed metadata)
        """
        if not self.input_dir:
            raise ValueError("Generator input_dir not set - cannot validate relationship targets from original YAML")

        # Extract entity name from QNK
        entity_name = target_qnk.split('/')[-1] if '/' in target_qnk else target_qnk
        file_path = target_info.get('file_path')

        if not entity_name or not file_path:
            raise ValueError(f"Cannot validate {target_qnk} - missing entity name or file path")

        try:
            from ..utils.yaml_utils import load_yaml_documents

            # Construct full file path
            full_file_path = os.path.join(self.input_dir, file_path)

            # Load original YAML documents
            documents = load_yaml_documents(full_file_path)

            # Find entities in this file and analyze backing
            entities_in_file = {}

            for doc in documents:
                if isinstance(doc, dict) and doc.get('kind') in ['ObjectType', 'Model', 'Command']:
                    doc_name = doc.get('definition', {}).get('name') or doc.get('name')
                    if doc_name:
                        kind = doc.get('kind')
                        if doc_name not in entities_in_file:
                            entities_in_file[doc_name] = set()
                        entities_in_file[doc_name].add(kind)

            # Check if our target entity exists
            if entity_name not in entities_in_file:
                raise ValueError(f"Entity {entity_name} not found in file {full_file_path}")

            entity_kinds = entities_in_file[entity_name]

            # Validation logic based on original YAML entities

            # CRITICAL: Direct Commands cannot be relationship targets
            if 'Command' in entity_kinds and len(entity_kinds) == 1:
                logger.info(f"Generator: BLOCKED pure Command {target_qnk} cannot be relationship target")
                return False

            # CRITICAL: Command-only ObjectTypes cannot be relationship targets
            if 'ObjectType' in entity_kinds and 'Command' in entity_kinds and 'Model' not in entity_kinds:
                logger.info(
                    f"Generator: BLOCKED Command-only ObjectType {target_qnk} cannot be relationship target - no Model backing")
                return False

            # Models are always valid targets
            if 'Model' in entity_kinds:
                logger.debug(f"Generator: ALLOWED Model {target_qnk} as relationship target")
                return True

            # Model-backed ObjectTypes are valid targets
            if 'ObjectType' in entity_kinds and 'Model' in entity_kinds:
                logger.debug(f"Generator: ALLOWED Model-backed ObjectType {target_qnk} as relationship target")
                return True

            # Pure ObjectTypes (no backing) are not valid targets
            if 'ObjectType' in entity_kinds and len(entity_kinds) == 1:
                logger.info(
                    f"Generator: BLOCKED pure ObjectType {target_qnk} cannot be relationship target - no backing")
                return False

            # Any other combination - default to false for safety
            logger.warning(f"Generator: BLOCKED {target_qnk} - unexpected entity combination: {entity_kinds}")
            return False

        except Exception as e:
            # Fatal error - no fallback to processed metadata
            raise Exception(
                f"FATAL: Cannot validate relationship target {target_qnk} by reading {full_file_path}: {e}") from e

    def _generate_forward_relationship(self, fk_rel: Dict[str, Any],
                                       entities_map: Dict[str, Dict],
                                       use_target_aware: bool = False) -> Optional[Dict[str, Any]]:
        """Generate forward (many-to-one or one-to-one) relationship."""
        source_qnk = fk_rel['from_entity']
        target_qnk = fk_rel['to_entity']
        from_field = fk_rel['from_field']
        to_field = fk_rel['to_field_name']

        source_info = entities_map.get(source_qnk, {})
        target_info = entities_map.get(target_qnk, {})

        source_name = source_info.get('name')
        target_name = target_info.get('name')

        if not source_name or not target_name:
            return None

        # CRITICAL: Add validation before generating relationship
        if not self._is_valid_relationship_target(target_qnk, target_info):
            logger.info(f"Generator: Skipping forward relationship to invalid target {target_qnk}")
            return None

        # Additional check: Source must also be queryable
        if not source_info.get('is_queryable', False):
            logger.info(f"Generator: Skipping forward relationship from non-queryable source {source_qnk}")
            return None

        # Generate base relationship name
        base_rel_name = self.generate_relationship_name_from_field(
            from_field, target_name, "single", target_aware=False
        )

        # Use static class variable to track used names per entity
        if source_name not in RelationshipGenerator._used_names_per_entity:
            RelationshipGenerator._used_names_per_entity[source_name] = set()

        # ENHANCED CONFLICT DETECTION: Check against BOTH relationship names AND field names
        existing_relationship_names = RelationshipGenerator._used_names_per_entity[source_name]
        existing_field_names = {f.get('name', '').lower() for f in source_info.get('fields', []) if f.get('name')}
        all_existing_names = existing_relationship_names.union(existing_field_names)

        final_rel_name = base_rel_name
        if base_rel_name.lower() in {name.lower() for name in all_existing_names}:
            # Conflict with either field or relationship - append target entity name
            target_suffix = to_snake_case(target_name)
            base_rel_name_snake = to_snake_case(base_rel_name)
            final_rel_name = f"{base_rel_name_snake}_{target_suffix}"

            # Determine what type of conflict this was for logging
            conflict_type = "field" if base_rel_name.lower() in existing_field_names else "relationship"
            logger.info(
                f"Relationship name conflict with {conflict_type} for {source_name}.{base_rel_name} - using {final_rel_name}")

        # If still conflicts (check again against full namespace), use numbered suffix
        counter = 2
        original_final_name = final_rel_name
        while final_rel_name.lower() in {name.lower() for name in all_existing_names}:
            final_rel_name = f"{original_final_name}_{counter}"
            counter += 1
            if counter > 10:  # Safety break
                logger.warning(f"Could not resolve naming conflict for {source_name}.{base_rel_name} after 10 attempts")
                break

        # Track this name as used (only track relationship names, not field names)
        RelationshipGenerator._used_names_per_entity[source_name].add(final_rel_name)

        # Build target block
        target_block = {
            "name": target_name,
            "relationshipType": "Object"
        }

        # Add subgraph if cross-subgraph relationship
        if target_info.get('subgraph') and target_info.get('subgraph') != source_info.get('subgraph'):
            target_block['subgraph'] = target_info.get('subgraph')

        # Build relationship definition
        relationship_def = {
            "name": final_rel_name,
            "sourceType": source_name,
            "target": {"model": target_block},
            "mapping": [{
                "source": {"fieldPath": [{"fieldName": from_field}]},
                "target": {"modelField": [{"fieldName": to_field}]}
            }]
        }

        logger.debug(f"Generated forward relationship: {source_name}.{final_rel_name} -> {target_name} "
                     f"(via {from_field} -> {to_field})")

        return {
            'target_file_path': source_info.get('file_path'),
            'relationship_definition': self.create_relationship_yaml_structure(relationship_def)
        }

    def _generate_reverse_relationship(self, fk_rel: Dict[str, Any],
                                       entities_map: Dict[str, Dict],
                                       use_target_aware: bool = False) -> Optional[Dict[str, Any]]:
        """Generate reverse (one-to-many) relationship."""
        source_qnk = fk_rel['from_entity']
        target_qnk = fk_rel['to_entity']
        from_field = fk_rel['from_field']
        to_field = fk_rel['to_field_name']

        source_info = entities_map.get(source_qnk, {})
        target_info = entities_map.get(target_qnk, {})

        source_name = source_info.get('name')
        target_name = target_info.get('name')

        if not source_name or not target_name:
            return None

        # CRITICAL: Add validation before generating relationship
        if not self._is_valid_relationship_target(source_qnk, source_info):
            logger.info(f"Generator: Skipping reverse relationship - invalid target {source_qnk}")
            return None

        # Additional check: Source must also be queryable
        if not target_info.get('is_queryable', False):
            logger.info(f"Generator: Skipping reverse relationship - non-queryable source {target_qnk}")
            return None

        # Generate base reverse relationship name
        base_source_name = self._clean_field_name_for_relationship(from_field)
        if base_source_name:
            source_snake = to_snake_case(source_name)
            base_source_snake = to_snake_case(base_source_name)
            base_rel_name = f"{smart_pluralize_snake(source_snake)}_by_{base_source_snake}"
        else:
            base_rel_name = self.generate_relationship_name(source_name, "multiple")

        # Use static class variable to track used names per entity (reverse relationships go on target entity)
        if target_name not in RelationshipGenerator._used_names_per_entity:
            RelationshipGenerator._used_names_per_entity[target_name] = set()

        # ENHANCED CONFLICT DETECTION: Check against BOTH relationship names AND field names
        existing_relationship_names = RelationshipGenerator._used_names_per_entity[target_name]
        existing_field_names = {f.get('name', '').lower() for f in target_info.get('fields', []) if f.get('name')}
        all_existing_names = existing_relationship_names.union(existing_field_names)

        final_rel_name = base_rel_name
        if base_rel_name.lower() in {name.lower() for name in all_existing_names}:
            # Conflict with either field or relationship - append source entity name
            source_suffix = to_snake_case(source_name)
            base_rel_name_snake = to_snake_case(base_rel_name)
            final_rel_name = f"{base_rel_name_snake}_from_{source_suffix}"

            # Determine what type of conflict this was for logging
            conflict_type = "field" if base_rel_name.lower() in existing_field_names else "relationship"
            logger.info(
                f"Reverse relationship name conflict with {conflict_type} for {target_name}.{base_rel_name} - using {final_rel_name}")

        # If still conflicts (check again against full namespace), use numbered suffix
        counter = 2
        original_final_name = final_rel_name
        while final_rel_name.lower() in {name.lower() for name in all_existing_names}:
            final_rel_name = f"{original_final_name}_{counter}"
            counter += 1
            if counter > 10:  # Safety break
                logger.warning(
                    f"Could not resolve reverse naming conflict for {target_name}.{base_rel_name} after 10 attempts")
                break

        # Track this name as used (only track relationship names, not field names)
        RelationshipGenerator._used_names_per_entity[target_name].add(final_rel_name)

        # Build target block
        target_block = {
            "name": source_name,
            "relationshipType": "Array"
        }

        # Add subgraph if cross-subgraph relationship
        if source_info.get('subgraph') and source_info.get('subgraph') != target_info.get('subgraph'):
            target_block['subgraph'] = source_info.get('subgraph')

        # Build relationship definition
        relationship_def = {
            "name": final_rel_name,
            "sourceType": target_name,
            "target": {"model": target_block},
            "mapping": [{
                "source": {"fieldPath": [{"fieldName": to_field}]},
                "target": {"modelField": [{"fieldName": from_field}]}
            }]
        }

        logger.debug(f"Generated reverse relationship: {target_name}.{final_rel_name} -> {source_name}[] "
                     f"(via {to_field} <- {from_field})")

        return {
            'target_file_path': source_info.get('file_path'),
            'relationship_definition': self.create_relationship_yaml_structure(relationship_def)
        }

    def _generate_shared_field_relationship(self, source_qnk: str, target_qnk: str,
                                            shared_field: str,
                                            entities_map: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """Generate a shared field (many-to-many) relationship."""
        source_info = entities_map.get(source_qnk, {})
        target_info = entities_map.get(target_qnk, {})

        source_name = source_info.get('name')
        target_name = target_info.get('name')

        if not source_name or not target_name:
            return None

        # CRITICAL: Add validation before generating relationship
        if not self._is_valid_relationship_target(target_qnk, target_info):
            logger.info(f"Generator: Skipping shared field relationship - invalid target {target_qnk}")
            return None

        # Additional check: Source must also be queryable
        if not source_info.get('is_queryable', False):
            logger.info(f"Generator: Skipping shared field relationship - non-queryable source {source_qnk}")
            return None

        # Find original case field names
        source_field_name = self._find_original_field_name(shared_field, source_info)
        target_field_name = self._find_original_field_name(shared_field, target_info)

        if not source_field_name or not target_field_name:
            return None

        # Generate base relationship name
        base_target_name = self.generate_relationship_name(target_name, "multiple")
        shared_field_suffix = to_snake_case(shared_field)
        base_rel_name = f"{base_target_name}_by_{shared_field_suffix}"

        # Use static class variable to track used names per entity
        if source_name not in RelationshipGenerator._used_names_per_entity:
            RelationshipGenerator._used_names_per_entity[source_name] = set()

        # ENHANCED CONFLICT DETECTION: Check against BOTH relationship names AND field names
        existing_relationship_names = RelationshipGenerator._used_names_per_entity[source_name]
        existing_field_names = {f.get('name', '').lower() for f in source_info.get('fields', []) if f.get('name')}
        all_existing_names = existing_relationship_names.union(existing_field_names)

        final_rel_name = base_rel_name
        if base_rel_name.lower() in {name.lower() for name in all_existing_names}:
            # Conflict with either field or relationship - append target entity name
            target_suffix = to_snake_case(target_name)
            source_suffix = to_snake_case(source_name)
            base_rel_name_snake = to_snake_case(base_rel_name)
            insert_position = base_rel_name_snake.index('by_') + len('by_')
            final_rel_name = base_rel_name_snake[:insert_position] + source_suffix + '_' + base_rel_name_snake[insert_position:]

            # Determine what type of conflict this was for logging
            conflict_type = "field" if base_rel_name.lower() in existing_field_names else "relationship"
            logger.info(
                f"Shared field relationship name conflict with {conflict_type} for {source_name}.{base_rel_name} - using {final_rel_name}")

        # If still conflicts (check again against full namespace), use numbered suffix
        counter = 2
        original_final_name = final_rel_name
        while final_rel_name.lower() in {name.lower() for name in all_existing_names}:
            final_rel_name = f"{original_final_name}{counter}"
            counter += 1
            if counter > 10:  # Safety break
                logger.warning(
                    f"Could not resolve shared field naming conflict for {source_name}.{base_rel_name} after 10 attempts")
                break

        # Track this name as used (only track relationship names, not field names)
        RelationshipGenerator._used_names_per_entity[source_name].add(final_rel_name)

        # Build target block
        target_block = {
            "name": target_name,
            "relationshipType": "Array"  # Many-to-many relationship
        }

        # Add subgraph if cross-subgraph relationship
        if target_info.get('subgraph') and target_info.get('subgraph') != source_info.get('subgraph'):
            target_block['subgraph'] = target_info.get('subgraph')

        # Build relationship definition
        relationship_def = {
            "name": final_rel_name,
            "sourceType": source_name,
            "target": {"model": target_block},
            "mapping": [{
                "source": {"fieldPath": [{"fieldName": source_field_name}]},
                "target": {"modelField": [{"fieldName": target_field_name}]}
            }]
        }

        return {
            'target_file_path': source_info.get('file_path'),
            'relationship_definition': self.create_relationship_yaml_structure(relationship_def)
        }

    def generate_foreign_key_relationships(self, fk_relationships: List[Dict[str, Any]],
                                           entities_map: Dict[str, Dict],
                                           existing_signatures: Set[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Generate relationship YAML definitions for foreign key relationships.

        ENHANCED: Now properly handles existing relationships and deduplicates.
        ADDED: Validation before each append to prevent invalid relationships.

        Args:
            fk_relationships: List of detected foreign key relationships
            entities_map: Map of entity qualified names to entity info
            existing_signatures: Set of existing relationship signatures (optional)
        """
        generated = []

        for fk_rel in fk_relationships:
            # Generate forward relationship (many-to-one or one-to-one)
            forward_rel = self._generate_forward_relationship(fk_rel, entities_map)
            if forward_rel:
                # CRITICAL: Validate before adding
                target_qnk = fk_rel.get('to_entity')
                target_info = entities_map.get(target_qnk, {})
                if self._is_valid_relationship_target(target_qnk, target_info):
                    generated.append(forward_rel)
                else:
                    logger.info(f"Generator: Blocked forward relationship to invalid target {target_qnk}")

            # Generate reverse relationship (one-to-many)
            reverse_rel = self._generate_reverse_relationship(fk_rel, entities_map)
            if reverse_rel:
                # CRITICAL: Validate before adding
                target_qnk = fk_rel.get('from_entity')
                target_info = entities_map.get(target_qnk, {})
                if self._is_valid_relationship_target(target_qnk, target_info):
                    generated.append(reverse_rel)
                else:
                    logger.info(f"Generator: Blocked reverse relationship to invalid target {target_qnk}")

        # Deduplicate against existing relationships if signatures provided
        if existing_signatures:
            generated = self.deduplicate_relationships(generated, existing_signatures)

        logger.info(f"Generated {len(generated)} foreign key relationship definitions for queryable entities")
        return generated

    def generate_shared_field_relationships(self, shared_relationships: List[Dict[str, Any]],
                                            entities_map: Dict[str, Dict],
                                            existing_signatures: Set[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Generate relationship YAML definitions for shared field relationships.

        ENHANCED: Now properly handles existing relationships and deduplicates.
        ADDED: Validation before each append to prevent invalid relationships.
        """
        generated = []

        for shared_rel in shared_relationships:
            # Generate bidirectional many-to-many relationships
            rel1 = self._generate_shared_field_relationship(
                shared_rel['from_entity'], shared_rel['to_entity'],
                shared_rel['shared_field'], entities_map
            )
            if rel1:
                # CRITICAL: Validate before adding
                target_qnk = shared_rel.get('to_entity')
                target_info = entities_map.get(target_qnk, {})
                if self._is_valid_relationship_target(target_qnk, target_info):
                    generated.append(rel1)
                else:
                    logger.info(f"Generator: Blocked shared field relationship to invalid target {target_qnk}")

            rel2 = self._generate_shared_field_relationship(
                shared_rel['to_entity'], shared_rel['from_entity'],
                shared_rel['shared_field'], entities_map
            )
            if rel2:
                # CRITICAL: Validate before adding
                target_qnk = shared_rel.get('from_entity')
                target_info = entities_map.get(target_qnk, {})
                if self._is_valid_relationship_target(target_qnk, target_info):
                    generated.append(rel2)
                else:
                    logger.info(f"Generator: Blocked shared field relationship to invalid target {target_qnk}")

        # Deduplicate against existing relationships if signatures provided
        if existing_signatures:
            generated = self.deduplicate_relationships(generated, existing_signatures)

        logger.info(f"Generated {len(generated)} shared field relationship definitions for queryable entities")
        return generated

    @classmethod
    def fix_existing_relationship_conflicts(cls, file_paths: List[str]) -> Dict[str, Any]:
        """
        Fix existing relationship conflicts by reading and modifying files directly.

        Uses the same pattern as other relationship methods - re-reads files to get complete data.

        Args:
            file_paths: List of schema file paths to scan and fix

        Returns:
            Dictionary with conflict resolution statistics
        """
        from ..utils.yaml_utils import load_yaml_documents, save_yaml_documents

        logger.info("Scanning files for existing relationship conflicts...")

        # Track conflicts and modifications
        conflicts_found = 0
        conflicts_fixed = 0
        conflict_details = []
        files_modified = set()

        # Group relationships by source entity to find conflicts
        relationships_by_entity = {}
        file_documents = {}  # Track documents for each file

        # First pass: scan all files and group relationships by sourceType
        for file_path in file_paths:
            try:
                documents = load_yaml_documents(file_path)
                file_documents[file_path] = documents  # Store for later modification

                for doc_idx, doc in enumerate(documents):
                    if isinstance(doc, dict) and doc.get('kind') == 'Relationship':
                        definition = doc.get('definition', {})
                        source_type = definition.get('sourceType')  # Now accessible!
                        rel_name = definition.get('name')

                        if source_type and rel_name:
                            # Track the relationship
                            if source_type not in relationships_by_entity:
                                relationships_by_entity[source_type] = {}

                            if rel_name not in relationships_by_entity[source_type]:
                                relationships_by_entity[source_type][rel_name] = []

                            location_info = {
                                'file_path': file_path,
                                'doc_index': doc_idx,
                                'document': doc,
                                'definition': definition,
                                'target_name': definition.get('target', {}).get('model', {}).get('name', 'unknown')
                            }

                            relationships_by_entity[source_type][rel_name].append(location_info)

            except Exception as e:
                logger.error(f"Error scanning file {file_path} for conflicts: {e}")

        # Second pass: find and fix conflicts
        for source_type, relationships_by_name in relationships_by_entity.items():
            for rel_name, rel_instances in relationships_by_name.items():
                if len(rel_instances) > 1:
                    # Conflict found!
                    conflicts_found += 1
                    target_names = [inst['target_name'] for inst in rel_instances]

                    logger.info(
                        f"Found conflict: {source_type}.{rel_name} ({len(rel_instances)} instances) -> {', '.join(target_names)}")

                    # Apply prioritization to decide which keeps the simple name
                    prioritized_instances = cls._prioritize_existing_relationship_instances(rel_instances, rel_name)

                    # Rename conflicting relationships (all except the first/highest priority)
                    entity_used_names = set(relationships_by_name.keys())

                    for i, instance in enumerate(prioritized_instances):
                        if i == 0:
                            # Highest priority keeps the original name
                            logger.info(
                                f"  Keeping original name: {source_type}.{rel_name} -> {instance['target_name']}")
                            continue

                        # Generate new name for conflicting relationship
                        target_name = instance['target_name']
                        if target_name:
                            rel_name_snake = to_snake_case(rel_name)
                            target_snake = to_snake_case(target_name)
                            new_name = f"{rel_name_snake}_{target_snake}"
                        else:
                            new_name = f"{to_snake_case(rel_name)}_{i + 1}"  # Fallback to numbered

                        # Ensure the new name doesn't conflict with other existing names
                        counter = 2
                        original_new_name = new_name
                        while new_name.lower() in {name.lower() for name in entity_used_names}:
                            new_name = f"{original_new_name}{counter}"
                            counter += 1

                        # Update the relationship definition IN THE DOCUMENT
                        instance['document']['definition']['name'] = new_name
                        entity_used_names.add(new_name)
                        files_modified.add(instance['file_path'])

                        conflicts_fixed += 1
                        conflict_details.append({
                            'entity': source_type,
                            'old_name': rel_name,
                            'new_name': new_name,
                            'target': target_name,
                            'file': instance['file_path']
                        })

                        logger.info(
                            f"  Renamed: {source_type}.{rel_name} -> {source_type}.{new_name} (target: {target_name})")

        # Third pass: save modified files
        if conflicts_fixed > 0:
            files_saved = 0
            for file_path in files_modified:
                try:
                    documents = file_documents[file_path]
                    save_yaml_documents(documents, file_path)
                    files_saved += 1
                    logger.debug(f"Saved conflict fixes to {file_path}")
                except Exception as e:
                    logger.error(f"Error saving fixes to {file_path}: {e}")

            logger.info(f"Saved conflict fixes to {files_saved} files")

        statistics = {
            'conflicts_found': conflicts_found,
            'conflicts_fixed': conflicts_fixed,
            'conflict_details': conflict_details,
            'files_modified': len(files_modified)
        }

        logger.info(f"Conflict resolution complete: {conflicts_fixed}/{conflicts_found} conflicts fixed in files")
        return statistics

    @classmethod
    def _prioritize_existing_relationship_instances(cls, instances: List[Dict[str, Any]],
                                                    rel_name: str) -> List[Dict[str, Any]]:
        """
        Prioritize existing relationship instances to determine which keeps the simple name.

        Same logic as new relationship prioritization.
        """

        def priority_score(instance):
            definition = instance['definition']
            target_name = definition.get('target', {}).get('model', {}).get('name', '')

            if not target_name:
                return (999, target_name, instance['file_path'])  # Low priority

            # Calculate similarity to relationship name
            target_lower = target_name.lower()
            rel_name_lower = rel_name.lower()

            # Exact match gets highest priority
            if target_lower == rel_name_lower:
                return (0, target_name, instance['file_path'])

            # Contains relationship name gets second priority
            if rel_name_lower in target_lower:
                return (1, target_name, instance['file_path'])

            # Relationship name contains target gets third priority
            if target_lower in rel_name_lower:
                return (2, target_name, instance['file_path'])

            # Alphabetical order for the rest (including file path for deterministic ordering)
            return (3, target_name, instance['file_path'])

        return sorted(instances, key=priority_score)

    @staticmethod
    def _prioritize_relationship_candidates(candidates: List[Dict[str, Any]], rel_name: str) -> List[Dict[str, Any]]:
        """
        Prioritize relationship candidates to determine which gets the simple name.

        Args:
            candidates: List of relationship candidates with same simple name
            rel_name: The relationship name they're competing for

        Returns:
            Sorted list of candidates in priority order (highest priority first)
        """

        def priority_score(candidate):
            target_name = candidate.get('target_name', '')

            if not target_name:
                return (999, target_name, candidate.get('source_info', {}).get('file_path', ''))  # Low priority

            # Calculate similarity to relationship name
            target_lower = target_name.lower()
            rel_name_lower = rel_name.lower()

            # Exact match gets highest priority
            if target_lower == rel_name_lower:
                return (0, target_name, candidate.get('source_info', {}).get('file_path', ''))

            # Contains relationship name gets second priority
            if rel_name_lower in target_lower:
                return (1, target_name, candidate.get('source_info', {}).get('file_path', ''))

            # Relationship name contains target gets third priority
            if target_lower in rel_name_lower:
                return (2, target_name, candidate.get('source_info', {}).get('file_path', ''))

            # Alphabetical order for the rest (including file path for deterministic ordering)
            return (3, target_name, candidate.get('source_info', {}).get('file_path', ''))

        return sorted(candidates, key=priority_score)

    @staticmethod
    def _to_snake_case(text: str) -> str:
        """
        Simple snake_case conversion for conflict resolution.

        Note: This should use the same logic as to_snake_case from above
        """
        return to_snake_case(text)

    @classmethod
    def initialize_with_existing_relationships(cls, file_paths: List[str]):
        """
        Initialize the used names tracking with existing relationships from schema files.

        This must be called before generating any new relationships to avoid duplicates.

        Args:
            file_paths: List of schema file paths to scan for existing relationships
        """
        from ..utils.yaml_utils import load_yaml_documents

        # Clear any previous state
        cls._used_names_per_entity.clear()

        logger.info(f"Scanning {len(file_paths)} files for existing relationships...")

        existing_count = 0
        for file_path in file_paths:
            try:
                documents = load_yaml_documents(file_path)
                for doc in documents:
                    if isinstance(doc, dict) and doc.get('kind') == 'Relationship':
                        definition = doc.get('definition', {})
                        source_type = definition.get('sourceType')
                        rel_name = definition.get('name')

                        if source_type and rel_name:
                            # Track this relationship name as used
                            if source_type not in cls._used_names_per_entity:
                                cls._used_names_per_entity[source_type] = set()

                            cls._used_names_per_entity[source_type].add(rel_name)
                            existing_count += 1

                            logger.debug(f"Found existing relationship: {source_type}.{rel_name}")

            except Exception as e:
                logger.error(f"Error scanning file {file_path} for existing relationships: {e}")

        logger.info(f"Loaded {existing_count} existing relationship names from schema files")
        logger.info(f"Entities with existing relationships: {len(cls._used_names_per_entity)}")

    @classmethod
    def clear_used_names(cls):
        """
        Clear the used names tracking - useful for completely new schema runs.

        This should be called at the start of a new schema processing session
        to ensure clean state when processing a completely different schema.
        """
        cls._used_names_per_entity.clear()
        logger.info("Cleared static used names tracking for relationship generation")

    @classmethod
    def get_used_names_statistics(cls) -> Dict[str, Any]:
        """
        Get statistics about currently tracked used names.

        Returns:
            Dictionary with statistics about name usage across entities
        """
        total_entities = len(cls._used_names_per_entity)
        total_names = sum(len(names) for names in cls._used_names_per_entity.values())

        return {
            'entities_with_relationships': total_entities,
            'total_relationship_names': total_names,
            'average_relationships_per_entity': total_names / total_entities if total_entities > 0 else 0,
            'entities_with_most_relationships': sorted(
                [(entity, len(names)) for entity, names in cls._used_names_per_entity.items()],
                key=lambda x: x[1], reverse=True
            )[:5]  # Top 5
        }

    @staticmethod
    def _validate_entities_are_queryable(relationship: Dict[str, Any],
                                         entities_map: Dict[str, Dict]) -> bool:
        """
        Validate that entities in a relationship can participate in relationship generation.

        Sources: Can be any queryable entity (ObjectType, Model, or Command)
        Targets: Can only be ObjectTypes or Models backed by actual Models, NOT Commands or Command-only ObjectTypes

        Args:
            relationship: Relationship dictionary with from_entity and to_entity
            entities_map: Map of entity qualified names to entity info

        Returns:
            True if both entities can participate in the relationship, False otherwise
        """
        from_entity = relationship.get('from_entity')
        to_entity = relationship.get('to_entity')

        if not from_entity or not to_entity:
            logger.warning(f"Invalid relationship - missing entity references: {relationship}")
            return False

        from_info = entities_map.get(from_entity, {})
        to_info = entities_map.get(to_entity, {})

        # Source validation: any queryable entity can be a source
        from_is_queryable = from_info.get('is_queryable', False)
        if not from_is_queryable:
            logger.debug(f"Skipping relationship generation - source entity {from_entity} is not queryable")
            return False

        # Target validation: must be queryable AND have filtering semantics (i.e., backed by Model)
        target_kind = to_info.get('kind')
        target_is_queryable = to_info.get('is_queryable', False)

        if not target_is_queryable:
            logger.debug(f"Skipping relationship generation - target entity {to_entity} is not queryable")
            return False

        # CRITICAL: Commands cannot be relationship targets (no filtering semantics)
        if target_kind == 'Command':
            logger.info(
                f"BLOCKED: Command {to_entity} cannot be relationship target - Commands have no filtering semantics")
            return False

        # CRITICAL: ObjectTypes must be backed by Models to be relationship targets
        if target_kind == 'ObjectType':
            queryable_via = to_info.get('queryable_via', [])
            if 'Model' not in queryable_via:
                logger.info(
                    f"BLOCKED: Command-only ObjectType {to_entity} cannot be relationship target - no Model backing")
                return False

        # Models are always valid targets if queryable
        if target_kind == 'Model':
            return True

        # For other entity types, they must be queryable
        return target_is_queryable

    @staticmethod
    def generate_relationship_name_from_field(field_name: str, target_entity_name: str,
                                              relationship_type: str = "single",
                                              target_aware: bool = False) -> str:
        """
        Generate relationship name based on the foreign key field name and optionally target entity.

        This approach creates more semantic and unique relationship names by using
        the actual foreign key field name and optionally the target entity name.

        Args:
            field_name: Name of the foreign key field
            target_entity_name: Name of the target entity
            relationship_type: "single" for one-to-one/many-to-one, "multiple" for one-to-many/many-to-many
            target_aware: Whether to include target entity information in the name

        Returns:
            Appropriately named relationship in snake_case
        """
        if not field_name:
            return RelationshipGenerator.generate_relationship_name(target_entity_name, relationship_type)

        # Clean the field name to create a relationship name
        cleaned_name = RelationshipGenerator._clean_field_name_for_relationship(field_name)

        # If cleaning resulted in empty string, fall back to target entity name
        if not cleaned_name:
            return RelationshipGenerator.generate_relationship_name(target_entity_name, relationship_type)

        # If target_aware is True and we have conflicts, incorporate target entity information
        if target_aware and target_entity_name:
            # Use pattern: cleaned_field_name + target_entity
            # e.g., "application" + "ItamBusinessApplication" = "application_itam_business_application"
            target_suffix = to_snake_case(target_entity_name)
            base_name = to_snake_case(cleaned_name)
            snake_name = f"{base_name}_{target_suffix}"
        else:
            # Use simple naming (default case)
            snake_name = to_snake_case(cleaned_name)

        # Apply pluralization if needed
        if relationship_type == "multiple":
            return smart_pluralize_snake(snake_name)
        else:
            return snake_name

    @staticmethod
    def generate_relationship_name(target_entity_name: str,
                                   relationship_type: str = "single") -> str:
        """
        Generate appropriate relationship names based on target entity and cardinality.

        Args:
            target_entity_name: Name of the target entity
            relationship_type: "single" for one-to-one/many-to-one, "multiple" for one-to-many/many-to-many

        Returns:
            Appropriately named relationship in snake_case
        """
        if not target_entity_name:
            return ""

        base_name = to_snake_case(target_entity_name)

        if relationship_type == "multiple":
            return smart_pluralize_snake(base_name)
        else:
            return base_name

    @staticmethod
    def _clean_field_name_for_relationship(field_name: str) -> str:
        """
        Clean a field name to create a semantic relationship name.

        Removes common suffixes like '_id', '_key', '_ref' and handles prefixes.

        Examples:
        - user_id -> user
        - created_by_user_id -> createdByUser
        - external_data_clive_route_lane_data_id -> externalDataCliveRouteLaneData
        - company_ref -> company
        - owner_key -> owner
        """
        if not field_name:
            return ""

        # Convert to lowercase for processing
        cleaned = field_name.lower().strip()

        # Remove common foreign key suffixes
        suffixes_to_remove = ['_id', '_key', '_ref', '_fk', '_foreign_key', 'id', 'key', 'ref']

        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)]
                break  # Only remove one suffix

        # Handle cases where the field name was just the suffix
        if not cleaned:
            return ""

        # Remove trailing underscores
        cleaned = cleaned.rstrip('_')

        return cleaned

    @staticmethod
    def check_relationship_conflicts(entity_info: Dict,
                                     proposed_relationship_name: str) -> bool:
        """
        Check if a proposed relationship name conflicts with existing fields.

        Args:
            entity_info: Entity information dictionary
            proposed_relationship_name: Proposed relationship name

        Returns:
            True if there's a conflict, False otherwise
        """
        existing_field_names = {f.get('name', '').lower() for f in entity_info.get('fields', [])}
        return proposed_relationship_name.lower() in existing_field_names

    @classmethod
    def resolve_relationship_name_conflicts(cls, base_name: str, entity_info: Dict,
                                            used_names: Set[str], target_entity_name: str = None) -> str:
        """
        Resolve naming conflicts by adding suffixes or modifying the name.

        Enhanced to include target entity information in conflict resolution.
        All names generated in snake_case.

        Args:
            base_name: Base relationship name
            entity_info: Entity information dictionary
            used_names: Set of already used relationship names for this entity
            target_entity_name: Name of target entity for additional context

        Returns:
            Unique relationship name in snake_case
        """
        if not cls.check_relationship_conflicts(entity_info, base_name) and \
                base_name.lower() not in {name.lower() for name in used_names}:
            return base_name

        # Try variations with target entity information first if available
        variations = []

        if target_entity_name:
            target_suffix = to_snake_case(target_entity_name)
            base_snake = to_snake_case(base_name)
            variations.extend([
                f"{base_snake}_{target_suffix}",
                f"{base_snake}_to_{target_suffix}",
                f"related_{target_suffix}"
            ])

        # Then try generic variations
        base_snake = to_snake_case(base_name)
        variations.extend([
            f"{base_snake}_ref",
            f"{base_snake}_link",
            f"related_{base_snake}",
            f"{base_snake}_entity"
        ])

        for variation in variations:
            if not cls.check_relationship_conflicts(entity_info, variation) and \
                    variation.lower() not in {name.lower() for name in used_names}:
                return variation

        # Last resort: add numbers
        counter = 2
        base_snake = to_snake_case(base_name)
        while counter <= 10:
            numbered_name = f"{base_snake}_{counter}"
            if not cls.check_relationship_conflicts(entity_info, numbered_name) and \
                    numbered_name.lower() not in {name.lower() for name in used_names}:
                return numbered_name
            counter += 1

        # If all else fails, return the original with a warning
        logger.warning(f"Could not resolve naming conflict for relationship '{base_name}'. Using original name.")
        return to_snake_case(base_name)

    @staticmethod
    def create_relationship_yaml_structure(relationship_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the complete YAML structure for a relationship definition.

        Args:
            relationship_def: Relationship definition dictionary

        Returns:
            Complete YAML structure with kind, version, and definition
        """
        return {
            "kind": "Relationship",
            "version": "v1",
            "definition": relationship_def
        }

    @staticmethod
    def group_relationships_by_file(relationships: List[Dict[str, Any]],
                                    entities_map: Dict[str, Dict]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group generated relationships by their target file paths.

        Args:
            relationships: List of relationship definitions with metadata
            entities_map: Map of entity qualified names to entity info

        Returns:
            Dictionary mapping file paths to lists of relationships
        """
        grouped = {}

        for rel_item in relationships:
            if isinstance(rel_item, dict) and 'target_file_path' in rel_item:
                file_path = rel_item['target_file_path']
                if file_path not in grouped:
                    grouped[file_path] = []
                grouped[file_path].append(rel_item['relationship_definition'])

        return grouped

    def deduplicate_relationships(self, relationships: List[Dict[str, Any]],
                                  existing_signatures: Set[Tuple]) -> List[Dict[str, Any]]:
        """
        Remove duplicate relationships based on their signatures.

        Args:
            relationships: List of relationship definitions
            existing_signatures: Set of existing relationship signatures

        Returns:
            Deduplicated list of relationships
        """
        deduplicated = []
        seen_signatures = existing_signatures.copy()

        for rel_item in relationships:
            signature = self._extract_relationship_signature(rel_item)
            if signature and signature not in seen_signatures:
                deduplicated.append(rel_item)
                seen_signatures.add(signature)
            elif not signature:
                # If we can't create a signature, include it with a warning
                logger.warning(f"Could not create signature for relationship, including anyway: {rel_item}")
                deduplicated.append(rel_item)

        logger.info(f"Deduplicated {len(relationships)} relationships to {len(deduplicated)}")
        return deduplicated

    def _generate_forward_relationships_with_conflict_resolution(self, rel_group: List[Dict[str, Any]],
                                                                 entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Generate forward relationships with smart conflict resolution.

        Only uses target-aware naming when there are actual naming conflicts.
        """
        # First pass: generate all relationships with simple names
        candidate_relationships = []

        for fk_rel in rel_group:
            if not self._validate_entities_are_queryable(fk_rel, entities_map):
                continue

            source_qnk = fk_rel['from_entity']
            target_qnk = fk_rel['to_entity']
            source_info = entities_map.get(source_qnk, {})
            target_info = entities_map.get(target_qnk, {})
            source_name = source_info.get('name')
            target_name = target_info.get('name')

            if not source_name or not target_name:
                continue

            # Generate simple relationship name
            simple_name = self.generate_relationship_name_from_field(
                fk_rel['from_field'], target_name, "single", target_aware=False
            )

            candidate_relationships.append({
                'fk_rel': fk_rel,
                'simple_name': simple_name,
                'target_name': target_name,
                'source_info': source_info,
                'target_info': target_info
            })

        # Second pass: detect naming conflicts and resolve them
        name_groups = {}
        for candidate in candidate_relationships:
            simple_name = candidate['simple_name']
            if simple_name not in name_groups:
                name_groups[simple_name] = []
            name_groups[simple_name].append(candidate)

        # Third pass: generate final relationships with conflict resolution
        generated = []
        for simple_name, candidates in name_groups.items():
            if len(candidates) == 1:
                # No conflict - use simple name
                generated.append(self._generate_single_forward_relationship(
                    candidates[0], use_target_aware=False
                ))
            else:
                # Conflict detected - resolve with target-aware naming
                logger.info(f"Name conflict for '{simple_name}' - resolving with target-aware naming")

                # Sort candidates to prioritize which gets the simple name
                candidates = self._prioritize_relationship_candidates(candidates, simple_name)

                # First candidate gets simple name, others get target-aware names
                for i, candidate in enumerate(candidates):
                    if i == 0:
                        # Keep simple name for the highest priority relationship
                        generated.append(self._generate_single_forward_relationship(
                            candidate, use_target_aware=False
                        ))
                    else:
                        # Use target-aware naming for conflicting relationships
                        generated.append(self._generate_single_forward_relationship(
                            candidate, use_target_aware=True
                        ))

        return [rel for rel in generated if rel is not None]

    def _generate_reverse_relationships_with_conflict_resolution(self, rel_group: List[Dict[str, Any]],
                                                                 entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Generate reverse relationships with smart conflict resolution.

        Only uses target-aware naming when there are actual naming conflicts.
        """
        # First pass: generate all relationships with simple names
        candidate_relationships = []

        for fk_rel in rel_group:
            if not self._validate_entities_are_queryable(fk_rel, entities_map):
                continue

            source_qnk = fk_rel['from_entity']
            target_qnk = fk_rel['to_entity']
            source_info = entities_map.get(source_qnk, {})
            target_info = entities_map.get(target_qnk, {})
            source_name = source_info.get('name')
            target_name = target_info.get('name')

            if not source_name or not target_name:
                continue

            # Generate simple reverse relationship name
            base_source_name = self._clean_field_name_for_relationship(fk_rel['from_field'])
            if base_source_name:
                source_snake = to_snake_case(source_name)
                base_source_snake = to_snake_case(base_source_name)
                simple_name = f"{smart_pluralize_snake(source_snake)}_by_{base_source_snake}"
            else:
                simple_name = self.generate_relationship_name(source_name, "multiple")

            candidate_relationships.append({
                'fk_rel': fk_rel,
                'simple_name': simple_name,
                'source_name': source_name,
                'source_info': source_info,
                'target_info': target_info
            })

        # Group by target entity (reverse relationships are defined on target entities)
        target_groups = {}
        for candidate in candidate_relationships:
            target_qnk = candidate['fk_rel']['to_entity']
            if target_qnk not in target_groups:
                target_groups[target_qnk] = []
            target_groups[target_qnk].append(candidate)

        # Generate relationships for each target entity
        generated = []
        for target_qnk, candidates in target_groups.items():
            # Check for naming conflicts within this target entity
            name_groups = {}
            for candidate in candidates:
                simple_name = candidate['simple_name']
                if simple_name not in name_groups:
                    name_groups[simple_name] = []
                name_groups[simple_name].append(candidate)

            # Resolve conflicts
            for simple_name, name_candidates in name_groups.items():
                if len(name_candidates) == 1:
                    # No conflict - use simple name
                    generated.append(self._generate_single_reverse_relationship(
                        name_candidates[0], use_target_aware=False
                    ))
                else:
                    # Conflict detected - resolve with target-aware naming
                    logger.info(
                        f"Reverse name conflict for '{simple_name}' on {target_qnk} - resolving with target-aware naming")

                    # Sort candidates to prioritize which gets the simple name
                    name_candidates = self._prioritize_relationship_candidates(name_candidates, simple_name)

                    # First candidate gets simple name, others get target-aware names
                    for i, candidate in enumerate(name_candidates):
                        if i == 0:
                            generated.append(self._generate_single_reverse_relationship(
                                candidate, use_target_aware=False
                            ))
                        else:
                            generated.append(self._generate_single_reverse_relationship(
                                candidate, use_target_aware=True
                            ))

        return [rel for rel in generated if rel is not None]

    def _generate_single_forward_relationship(self, candidate: Dict[str, Any],
                                              use_target_aware: bool) -> Optional[Dict[str, Any]]:
        """Generate a single forward relationship from a candidate."""
        fk_rel = candidate['fk_rel']
        source_info = candidate['source_info']
        target_info = candidate['target_info']

        source_name = source_info.get('name')
        target_name = target_info.get('name')
        from_field = fk_rel['from_field']
        to_field = fk_rel['to_field_name']

        # Generate relationship name
        if use_target_aware:
            rel_name = self.generate_relationship_name_from_field(
                from_field, target_name, "single", target_aware=True
            )
        else:
            rel_name = candidate['simple_name']

        # Use static class variable to track used names per entity
        if source_name not in RelationshipGenerator._used_names_per_entity:
            RelationshipGenerator._used_names_per_entity[source_name] = set()

        # Resolve any remaining naming conflicts
        final_rel_name = self.resolve_relationship_name_conflicts(
            rel_name, source_info, RelationshipGenerator._used_names_per_entity[source_name],
            target_name if use_target_aware else None
        )

        # Track this name as used
        RelationshipGenerator._used_names_per_entity[source_name].add(final_rel_name)

        # Build target block
        target_block = {
            "name": target_name,
            "relationshipType": "Object"
        }

        # Add subgraph if cross-subgraph relationship
        if target_info.get('subgraph') and target_info.get('subgraph') != source_info.get('subgraph'):
            target_block['subgraph'] = target_info.get('subgraph')

        # Build relationship definition
        relationship_def = {
            "name": final_rel_name,
            "sourceType": source_name,
            "target": {"model": target_block},
            "mapping": [{
                "source": {"fieldPath": [{"fieldName": from_field}]},
                "target": {"modelField": [{"fieldName": to_field}]}
            }]
        }

        logger.debug(f"Generated forward relationship: {source_name}.{final_rel_name} -> {target_name} "
                     f"(via {from_field} -> {to_field}) [target_aware={use_target_aware}]")

        return {
            'target_file_path': source_info.get('file_path'),
            'relationship_definition': self.create_relationship_yaml_structure(relationship_def)
        }

    def _generate_single_reverse_relationship(self, candidate: Dict[str, Any],
                                              use_target_aware: bool) -> Optional[Dict[str, Any]]:
        """Generate a single reverse relationship from a candidate."""
        fk_rel = candidate['fk_rel']
        source_info = candidate['source_info']
        target_info = candidate['target_info']

        source_name = candidate['source_name']
        target_name = target_info.get('name')
        from_field = fk_rel['from_field']
        to_field = fk_rel['to_field_name']

        # Generate relationship name
        if use_target_aware:
            base_source_name = self._clean_field_name_for_relationship(from_field)
            source_suffix = to_snake_case(source_name)
            source_snake = to_snake_case(source_name)
            base_source_snake = to_snake_case(base_source_name)
            rel_name = f"{smart_pluralize_snake(source_snake)}_by_{base_source_snake}_{source_suffix}"
        else:
            rel_name = candidate['simple_name']

        # Use static class variable to track used names per entity
        if target_name not in RelationshipGenerator._used_names_per_entity:
            RelationshipGenerator._used_names_per_entity[target_name] = set()

        # Resolve any remaining naming conflicts
        final_rel_name = self.resolve_relationship_name_conflicts(
            rel_name, target_info, RelationshipGenerator._used_names_per_entity[target_name],
            source_name if use_target_aware else None
        )

        # Track this name as used
        RelationshipGenerator._used_names_per_entity[target_name].add(final_rel_name)

        # Build target block
        target_block = {
            "name": source_name,
            "relationshipType": "Array"
        }

        # Add subgraph if cross-subgraph relationship
        if source_info.get('subgraph') and source_info.get('subgraph') != target_info.get('subgraph'):
            target_block['subgraph'] = source_info.get('subgraph')

        # Build relationship definition
        relationship_def = {
            "name": final_rel_name,
            "sourceType": target_name,
            "target": {"model": target_block},
            "mapping": [{
                "source": {"fieldPath": [{"fieldName": to_field}]},
                "target": {"modelField": [{"fieldName": from_field}]}
            }]
        }

        logger.debug(f"Generated reverse relationship: {target_name}.{final_rel_name} -> {source_name}[] "
                     f"(via {to_field} <- {from_field}) [target_aware={use_target_aware}]")

        return {
            'target_file_path': target_info.get('file_path'),
            'relationship_definition': self.create_relationship_yaml_structure(relationship_def)
        }

    @staticmethod
    def _find_original_field_name(field_name_lower: str, entity_info: Dict) -> Optional[str]:
        """Find the original case field name from entity info."""
        for field in entity_info.get('fields', []):
            if field.get('name', '').lower() == field_name_lower:
                return field.get('name')
        return None

    @staticmethod
    def _extract_relationship_signature(rel_item: Dict[str, Any]) -> Optional[Tuple]:
        """Extract a unique signature from a relationship definition."""
        try:
            if 'relationship_definition' in rel_item:
                rel_def = rel_item['relationship_definition']
            else:
                rel_def = rel_item

            definition = rel_def.get('definition', {})
            source_type = definition.get('sourceType')
            mapping = definition.get('mapping', [])

            if not source_type or not mapping:
                return None

            canonical_mapping_parts = []
            for m_item in mapping:
                if isinstance(m_item, dict):
                    # Extract source field path
                    source_fp = m_item.get('source', {}).get('fieldPath', [])
                    source_field_names = tuple(
                        fp.get('fieldName', fp) if isinstance(fp, dict) else fp
                        for fp in source_fp
                    )

                    # Extract target field path (prioritize modelField)
                    target_block = m_item.get('target', {})
                    target_fp = target_block.get('modelField', target_block.get('fieldPath', []))
                    target_field_names = tuple(
                        fp.get('fieldName', fp) if isinstance(fp, dict) else fp
                        for fp in target_fp
                    )

                    canonical_mapping_parts.append((source_field_names, target_field_names))

            canonical_mapping_parts.sort()
            return source_type, frozenset(canonical_mapping_parts)

        except Exception as e:
            logger.warning(f"Could not create signature for relationship: {e}")
            return None

    def generate_relationship_descriptions(self, relationships: List[Dict[str, Any]],
                                           entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Generate descriptions for relationship definitions.

        Only adds descriptions if they don't already exist, preserving any existing descriptions.

        Args:
            relationships: List of relationship definitions
            entities_map: Map of entity qualified names to entity info

        Returns:
            List of relationships with added descriptions
        """
        enhanced_relationships = []
        descriptions_added = 0
        descriptions_skipped = 0

        logger.info(f"Generating descriptions for {len(relationships)} relationships...")

        for rel_item in relationships:
            enhanced_rel = rel_item.copy()

            # Extract relationship info
            rel_def = rel_item.get('relationship_definition', {}).get('definition', {})
            rel_name = rel_def.get('name', '')
            source_type = rel_def.get('sourceType', '')
            target_info = rel_def.get('target', {}).get('model', {})
            target_name = target_info.get('name', '')
            relationship_type = target_info.get('relationshipType', 'Object')

            # Check if description already exists
            existing_description = None
            if 'relationship_definition' in enhanced_rel:
                existing_description = enhanced_rel['relationship_definition']['definition'].get('description')
            else:
                existing_description = enhanced_rel.get('definition', {}).get('description')

            # Only generate and add description if none exists
            if not existing_description:
                description = self._generate_relationship_description(
                    rel_name, source_type, target_name, relationship_type
                )

                if description:
                    # Add description to relationship definition
                    if 'relationship_definition' in enhanced_rel:
                        enhanced_rel['relationship_definition']['definition']['description'] = description
                    else:
                        if 'definition' not in enhanced_rel:
                            enhanced_rel['definition'] = {}
                        enhanced_rel['definition']['description'] = description

                    descriptions_added += 1
                    logger.debug(f"Added description for relationship {source_type}.{rel_name}: {description}")
                else:
                    logger.warning(f"Failed to generate description for relationship {source_type}.{rel_name}")
            else:
                descriptions_skipped += 1
                logger.debug(f"Preserving existing description for relationship {source_type}.{rel_name}")

            enhanced_relationships.append(enhanced_rel)

        logger.info(
            f"Relationship descriptions: {descriptions_added} added, {descriptions_skipped} skipped (already existed)")
        return enhanced_relationships

    @staticmethod
    def _generate_relationship_description(rel_name: str, source_type: str,
                                           target_name: str, relationship_type: str) -> str:
        """Generate a description for a relationship."""
        if relationship_type == "Array":
            description = f"Collection of {target_name} entities related to this {source_type}."
        else:
            description = f"Reference to the associated {target_name} entity."

        logger.debug(f"Generated description for {source_type}.{rel_name}: '{description}'")
        return description

    def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about relationship generation.

        Returns:
            Dictionary with generation statistics
        """
        return {
            'total_generated': len(self.generated_relationships),
            'unique_signatures': len(self.relationship_signatures),
            'relationships_by_type': self._count_by_relationship_type(),
            'cross_subgraph_count': self._count_cross_subgraph_relationships(),
            'used_names_statistics': self.get_used_names_statistics()
        }

    def _count_by_relationship_type(self) -> Dict[str, int]:
        """Count relationships by their target relationship type."""
        counts = {}
        for rel in self.generated_relationships:
            rel_def = rel.get('relationship_definition', {}).get('definition', {})
            rel_type = rel_def.get('target', {}).get('model', {}).get('relationshipType', 'Unknown')
            counts[rel_type] = counts.get(rel_type, 0) + 1
        return counts

    def _count_cross_subgraph_relationships(self) -> int:
        """Count relationships that cross subgraph boundaries."""
        count = 0
        for rel in self.generated_relationships:
            rel_def = rel.get('relationship_definition', {}).get('definition', {})
            if 'subgraph' in rel_def.get('target', {}).get('model', {}):
                count += 1
        return count


def create_relationship_generator(input_dir: str = None) -> RelationshipGenerator:
    """
    Create a RelationshipGenerator instance.

    Args:
        input_dir: Base directory for schema files (required for YAML validation)

    Returns:
        Configured RelationshipGenerator instance
    """
    return RelationshipGenerator(input_dir)
