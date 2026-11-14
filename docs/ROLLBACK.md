# Rollback

Source/code rollback uses git revert in this repository. Upstream/bundle rollback selects the previous manifest identity. Host rollback uses the new receipt transaction journal only. User projects, case/Evidence, Spec features, app and checks are preserved.

Cleanup uncertainty retains the writer lease and blocks a replacement writer until the owner confirms termination.
