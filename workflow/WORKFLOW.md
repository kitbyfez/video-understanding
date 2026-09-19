# Video-Understanding Workflow

Mandatory for every video the agent edits, reviews, or cuts. The 1fps
catalog pass runs **first**, before any edit decisions. It is the price of
admission for precision work later.

## Pass 1 — Understand (mandatory, once per video)

1. **Transcribe first.** Extract audio, run word-level transcription
   (faster-whisper, `word_timestamps=True`). Apply known corrections
   (proper nouns, script-verified wording). Save `transcript.json`.
2. **Sample 1 fps.** Extract one frame per second, downscaled for analysis
   (480px wide is enough), into `frames/fNNN.jpg` where `f001` = `[0,1)`.
3. **Describe in parallel.** Fan out workers over contiguous second ranges
   (4-8 seconds per worker; 8-12 workers is the working default — tokens are
   plentiful, gap time is the enemy). Each worker gets its frames plus the
   full word-timed transcript and returns, per second:
   - `visual`: summary, subjects, setting, on-screen text, transition, camera
   - `narration`: words overlapping that second
   - `match`: whether the visual illustrates the narration
4. **Merge.** Assemble `catalog.json` per `spec/FORMAT.md`. Validate:
   one record per second, no gaps, no overlapping narration claims,
   frames present for every record.
5. **Commit.** The catalog, transcript, and frames are committed to the repo
   under an id derived from the video. The catalog is durable data — it must
   survive the agent.

## Pass 2 — Precision (on demand)

Precision cuts never re-scan the video. Procedure:

1. **Locate via catalog.** Find the target second(s) with `jq` / grep over
   `catalog.json` — by narration word, by visual subject, by transition.
2. **Dump full-rate frames.** Extract every frame at native fps for the
   located second(s) into `precision/<t0>-<t1>/`.
3. **Pick the frame.** Examine the full-rate frames, choose the exact cut
   frame. Record the decision (second + frame number + reason) — it becomes
   part of the video's edit history.

## Cost posture

Pass 1 costs minutes and is amortized across every future edit of that
video. Pass 2 costs seconds per cut. Never skip Pass 1 to "save time" —
an unindexed video forces a full re-scan on every question, which is the
expensive path.
