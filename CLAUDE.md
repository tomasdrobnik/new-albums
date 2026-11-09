# Project Instructions

## 🚨 CONTEXTVAULT - MANDATORY (DO NOT SKIP!) 🚨

**STOP. READ THIS. FOLLOW IT.**

### ⚡ AFTER EVERY TASK - DOCUMENT IMMEDIATELY ⚡

┌─────────────────────────────────────────────────────────────────┐
│  COMPLETED A TASK? → DOCUMENT IT NOW!                           │
│                                                                 │
│  ✅ Fixed a bug?        → /ctx-error or /ctx-doc                │
│  ✅ Made a decision?    → /ctx-decision                         │
│  ✅ Learned something?  → /ctx-doc                              │
│  ✅ Found useful code?  → /ctx-doc type=snippet                 │
│  ✅ Explored codebase?  → /ctx-doc type=intel                   │
│  ✅ Ending session?     → /ctx-handoff                          │
│                                                                 │
│  💭 Not every edit needs documenting                             │
│  💭 Document at milestones, not mid-edit                         │
│  💭 Skip if nothing meaningful was learned                       │
└─────────────────────────────────────────────────────────────────┘

### SESSION START (AUTOMATIC):
1. Read `./.claude/vault/index.md` immediately
2. Review what's already documented
3. Use that knowledge in your work

### WHEN TO DOCUMENT:
- Feature complete → /ctx-doc
- Bug fix solved → /ctx-error
- Architecture decision → /ctx-decision
- Session ending → /ctx-handoff
- NOT: trivial edits, version bumps, mid-refactor

### RULES:
- Project docs → `./.claude/vault/` with P### prefix
- ALWAYS update index after doc changes
- Search before creating (no duplicates)

### COMMANDS:
`/ctx-doc` `/ctx-error` `/ctx-decision` `/ctx-handoff` `/ctx-search` `/ctx-read` `/ctx-bootstrap` `/ctx-plan`

## Git: confirm, then commit AND push

When a task/topic is coded and no open questions remain, give a brief summary and ask me to confirm via `AskUserQuestion` ("Commit and push?"). After I confirm, commit and push in the same step. Never leave a commit unpushed or finished work uncommitted. Do not commit/push before I confirm.

## Idle session: offer /ctx-handoff

To avoid losing prompt-cache data and wasting tokens: when I have been inactive for a while (a turn ends with work paused, or my next message arrives after a long gap, roughly 5+ minutes), ask via `AskUserQuestion` whether to run `/ctx-handoff` now. Do not run it without my answer.
