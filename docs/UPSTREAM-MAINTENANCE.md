# Upstream Maintenance

Official components remain official by default. Use `components/official/manifest.json` and create an update record before changing a pin.

For REA and Spec Kit, compare schema/API/runtime changes and run focused adapters before adopting. For Craft, reapply the fixed patch series on a detached upstream tree and regenerate its source manifest before adopting. For Reverse core, port domain improvements selectively while preserving the single route owner.

An update is accepted only when source identity, affected contracts, focused tests, representative acceptance and rollback are recorded.
