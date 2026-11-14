# Host adapters

The repository exposes one host-neutral CLI. A Codex, Pi or Claude adapter only
needs to identify the host and call `plan`; it does not write global client
configuration. Provider loading and credentials remain host-owned and are
reported as `unverified` until a real handshake is observed.
