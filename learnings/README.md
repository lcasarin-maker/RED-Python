# Learnings

This directory is the upstream registry for normalized satellite findings.

## Purpose

- store learning packets that have already been distilled by the satellite
- keep evidence compact and structured
- give CC something reusable to review

## Expected content

- `{repo}-YYYY-MM-DD.json`: structured learning event packets
- `synthesis.json`: cross-repo pattern synthesis

## Flow

1. The satellite records a local observation.
2. The observation is distilled into a structured packet.
3. CC reviews the packet and classifies it as local, CC-reusable, or GS-ready.
4. Only normalized learnings move farther upstream.

## Related docs

- [Satellite learning flow](../docs/learning/SATELLITE_LEARNING_FLOW.md)
- [Learning schema](../docs/learning/LEARNING_EVENT_SCHEMA.json)
