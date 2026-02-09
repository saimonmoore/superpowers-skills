# Napkin

A skill for LLM CLIs that gives the agent persistent memory of its mistakes.

The agent maintains a markdown file in your repo (`.agent/napkin.md`) where it tracks what went wrong, what you corrected, and what worked. It reads the file at session start and writes to it continuously as it works. By session 3-5 the behavior shift is significant — the agent stops making mistakes you've already corrected and starts pre-empting issues before you catch them.

Baby continual learning in a markdown file.

## Install

Install via [open-skills](https://github.com/numman-ali/openskills)

That's it. The skill activates every session, unconditionally.

## How it works

1. **Session start**: Agent reads `.agent/napkin.md` in the current repo. If it doesn't exist, it creates one.
2. **During work**: Agent logs mistakes (its own and yours), corrections, patterns, preferences — as they happen, not just at session end.
3. **Over sessions**: The napkin compounds. Session 1 is normal. Session 3 the agent is catching things before you do. Session 5 it's a different tool.

## What gets logged

- Agent's own mistakes — wrong assumptions, bad approaches, failed commands
- Your corrections — anything you told it to do differently
- Tool/environment surprises — things about the repo that weren't obvious
- Your preferences — how you like things done
- What worked — successful approaches worth repeating

## The napkin

Lives at `.agent/napkin.md` in each repo (one per repo) and logs generic personal preferences to `~/.agent/napkin.md`. The agent designs the initial structure and adapts it to the project's domain.

You can `.gitignore` it or commit it — your call. Committing it means other contributors' agents benefit from the same learned patterns. Ignoring it keeps it personal.

## License

MIT
