# DeepSeek V4 + Claude Code: research notes and a ready-to-use prompt

Source video: [youtube.com/watch?v=YFUdWCN9nj4](https://www.youtube.com/watch?v=YFUdWCN9nj4) — a "DeepSeek V4 destroys Claude Opus, set it up with Claude Code via Ollama" tutorial. The setup steps are real; most of the specific numbers in the script are not. Fact-check below, prompt at the bottom.

## What the video gets right

- **Ollama does speak Claude Code's protocol.** Since Ollama v0.14.0 (shipped Jan 16, 2026), Ollama exposes an Anthropic-compatible `/v1/messages` endpoint. Pointing Claude Code at a local or Ollama-cloud-hosted model is just:
  ```
  export ANTHROPIC_BASE_URL=http://localhost:11434
  export ANTHROPIC_AUTH_TOKEN=ollama
  claude
  ```
  No proxy, no translation layer. ([morphllm.com](https://www.morphllm.com/ollama-claude-code), [localaimaster.com](https://localaimaster.com/blog/claude-code-offline-ollama))
- **DeepSeek V4 is real and it is cheap.** DeepSeek shipped V4-Flash and V4-Pro as open weights (MIT license) starting April 24, 2026; Flash reached GA July 31, Pro reached GA Aug 12, 2026. ([techtimes.com](https://www.techtimes.com/articles/324241/20260813/deepseek-v4-pro-0813-goes-ga-benchmark-claims-await-independent-proof.htm))
- **The "build on a frontier model, deploy on a cheap one" strategy is sound** — it's just standard model-tiering, which is already the design of this repo's own fleet (8 model tiers, cache-first).

## What the video gets wrong or inflates

| Claim in video | Reality (Aug 2026) |
|---|---|
| "Opus 4.8 released 2 months ago" | Current flagship is **Opus 5**, launched July 24, 2026, at the same $5/$25 per-million-token pricing as 4.8. There's no current "Opus 4.8 is 2 months old" — the script is stale or garbled. ([ayautomate.com](https://www.ayautomate.com/blog/claude-opus-5-pricing)) |
| "DeepSeek V4 ranked 7th, beats Opus 4.8, Grok 4.5, Sonnet 5" | On Artificial Analysis's Intelligence Index, DeepSeek V4 Flash scores **52** vs Claude Sonnet 5 at **55** — close, but Sonnet 5 is still ahead, and this is Flash vs Sonnet, not vs Opus. ([artificialanalysis.ai](https://artificialanalysis.ai/models/comparisons/deepseek-v4-flash-vs-claude-sonnet-5)) |
| "Output costs $50/M for Opus" | Opus 5 output is **$25/M** standard (**$50/M** only in 2.5x Fast Mode). The video picked the Fast Mode number and presented it as the default. ([ayautomate.com](https://www.ayautomate.com/blog/claude-opus-5-pricing)) |
| "35–300x cheaper, 10x faster" | Real numbers: DeepSeek V4 Flash ≈ **$0.06/M** blended vs Sonnet 5 ≈ **$1.54/M** blended (~25x, not 300x) — that ratio only hits triple digits if you cherry-pick Opus-tier input pricing against DeepSeek's cheapest tier. Speed: **~120–140 tok/s** vs Sonnet 5's **~67 tok/s** — about 2x, not 10x. ([artificialanalysis.ai](https://artificialanalysis.ai/models/comparisons/deepseek-v4-flash-vs-claude-sonnet-5)) |
| Benchmark scores generally | DeepSeek's headline benchmark gains (**+49.9 pp** in their own materials) have **not been reproduced by any third-party evaluator**. The scores circulated via DeepSeek's WeChat group → Reddit → an ASCII table on Hacker News — not a controlled release. On the independent DeepSWE agentic-coding eval, DeepSeek V4 Pro scored **8% pass@1**, against DeepSeek's self-reported **80.6%** on SWE-bench Verified. That's the gap that matters most for a coding agent: self-reported vs. independently verified agentic performance is wildly different. ([techtimes.com](https://www.techtimes.com/articles/324241/20260813/deepseek-v4-pro-0813-goes-ga-benchmark-claims-await-independent-proof.htm)) |
| "Cursor free plan + Ollama = unlimited compute for $20/mo, cheaper than $200 Max" | Plausible on raw token cost, but unverified against current Ollama Cloud plan terms — treat as a marketing claim, not a checked fact. |

**Bottom line:** the plumbing (Claude Code → Ollama → DeepSeek V4) works exactly as described. The economics direction (open-weight models are now genuinely competitive on cost, and usably close on quality for a lot of tasks) is real. The specific numbers in the video are cherry-picked or wrong, and the one benchmark that matters most for a coding agent — independently verified agentic coding accuracy — shows DeepSeek V4 badly underperforming its own marketing (8% vs. a claimed 80.6%). Don't route production agent work to it on the strength of a YouTube script; eval it on your own tasks first.

## The prompt

A Claude Code task prompt that applies the *correct* version of the video's strategy to this repo's existing fleet model (8 tiers, cache-first, $0 target): prototype on a frontier model, add DeepSeek V4 Flash as a new bottom tier, but gate it behind an actual eval instead of trusting headline numbers.

```
You are setting up a new bottom-tier model in a cost-tiered LLM fleet (currently
8 tiers, cache-first, budget target ~$0/month). Add DeepSeek V4 Flash, served
locally or via Ollama Cloud, as a candidate cheapest tier — but do not promote
it to production routing until it's been verified, not just benchmarked.

1. Wire it up
   - Point Claude Code (or the fleet's LLM client) at Ollama's Anthropic-
     compatible endpoint: ANTHROPIC_BASE_URL=http://localhost:11434,
     ANTHROPIC_AUTH_TOKEN=ollama, model deepseek-v4-flash.
   - Confirm it responds and streams correctly before touching any routing logic.

2. Build a small eval set from THIS fleet's real traffic
   - Pull 15-20 recent real tasks this fleet has actually run (a mix of the
     easy/repetitive kind this tier would be used for, not synthetic prompts).
   - Run each one on both the current cheapest working tier and DeepSeek V4
     Flash. Score pass/fail against the existing tier's known-good output,
     not against DeepSeek's own claimed benchmarks — self-reported scores
     for this model have not been reproduced independently and should not
     be trusted as a proxy for real task accuracy.

3. Only promote it if it earns it
   - If DeepSeek V4 Flash matches accuracy within an acceptable margin on
     that eval set AND is cheaper/faster in practice, add it as a new tier
     with circuit breakers and fall back to the next tier up on failure —
     same pattern as the existing tiers.
   - If it doesn't hold up on real tasks, don't wire it into production
     routing just because it's cheap; note the gap and stop there.

4. Report back
   - Cost per task, latency, and pass rate for DeepSeek V4 Flash vs. the
     tier it would replace, plus which of the eval tasks it failed on.
```

## Sources

- [DeepSeek V4 Pro 0813 Goes GA: Benchmark Claims Await Independent Proof](https://www.techtimes.com/articles/324241/20260813/deepseek-v4-pro-0813-goes-ga-benchmark-claims-await-independent-proof.htm)
- [DeepSeek V4 Flash 0731 vs Claude Sonnet 5 — Artificial Analysis](https://artificialanalysis.ai/models/comparisons/deepseek-v4-flash-vs-claude-sonnet-5)
- [Claude Opus 5 Pricing: $5 and $25 per Million Tokens](https://www.ayautomate.com/blog/claude-opus-5-pricing)
- [Ollama + Claude Code: Run Local Models (2026 Setup Guide)](https://www.morphllm.com/ollama-claude-code)
- [Run Claude Code Offline with Ollama (2026)](https://localaimaster.com/blog/claude-code-offline-ollama)
