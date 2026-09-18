# Mutations and pending state

How a mutation hook reports its own settledness, and how a container may render a mutation's predictable outcome before
it settles. A spoke of the [frontend structure hub](../frontend-structure.md); each rule follows the slot skeleton owned
by `winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## A mutation settles only once its invalidations refetch (`bzh:frontend-mutation-settles-on-refresh`)

**Rule.** A mutation hook (`inject*Mutation`) stays `isPending()` true until its cache invalidations have actually
refetched: every `queryClient.invalidateQueries(...)` call inside the hook is returned (or `Promise.all`'d and returned)
from `onSettled`, never fired with `void` from `onSuccess`. The control that triggers the mutation is disabled while it
is pending, scoped to the specific item it acts on — one row's control does not disable a sibling row's. A mutation's
failure renders through the view's existing inline `actionError` slot via `errorMessage`
(`fleet/src/lib/error-message.ts`); no mutation fails silently.

**Why.** Without this, the UI acknowledges a click as "done" before the visible state has actually changed — the change
only appears on the next SSE/poll-driven refetch, so a user can't tell whether their click worked, and nothing stops a
duplicate click.

**Detect.** A mutation hook whose `onSuccess`/`onSettled` calls `void queryClient.invalidateQueries(...)` (the promise
discarded) rather than returning it — tooled by `web:structural-gate`'s `assertInvalidateReturnedDetectorWorks` sweep. A
triggering control with no `disabled` binding tied to its own item's pending state, or a mutation site with no `onError`
path to `errorMessage` — these two halves are review questions, not tooled.

**Do.**

- `local-panel/src/lib/status.query.ts`'s `injectLocalPauseMutation` returns `queryClient.invalidateQueries(...)` from
  `onSettled` rather than voiding it; `local-pause-control.ts` binds `[disabled]="pending()"` off that same mutation's
  `isPending()`, scoped to its own control.

**Don't.** `onSuccess: () => { void queryClient.invalidateQueries({ queryKey: someKey }); }` — the mutation reports
settled before the refetch lands, and the view can show stale data as if the action had already taken effect.

## A predictable outcome renders from mutation variables, never a cache write (`bzh:frontend-pending-override`)

**Rule.** Where a control's resulting change is predictable, its container renders that change immediately by reading
the in-flight mutation's variables through `injectMutationState` (filtered by `mutationKey` and `status: 'pending'`) and
applying them over the query data in a `computed()` — never by writing to the query cache (no `setQueryData`, no
`onMutate` snapshot/rollback). When the mutation settles, the override disappears and the view renders the refetched
server data; on failure the item reverts to its prior state and the error renders per
`bzh:frontend-mutation-settles-on-refresh`. A shared helper (`fleet/src/lib/mutation-pending/`) provides the
pending-state read and the per-item lookup; every override site uses it rather than writing `injectMutationState`
plumbing of its own. Containers apply the override; presentational components only receive the result as inputs, per
`bzh:frontend-container-presentational`. A pending override never re-derives a status precedence ladder that already has
one prose home ([`../../domain/work/statuses.md`](../../domain/work/statuses.md)) — where an override's prediction is
not total over the currently rendered status, the control falls back to disabled-and-pending with no rendered status
change, rather than guessing.

**Why.** A cache write races the real server response and can leave the cache holding a guess if the request fails or
the server's actual outcome differs from the guess; deriving the overlay in the container's own `computed()` from the
mutation's own variables can never diverge from what was actually requested, and disappears the instant the mutation
settles.

**Detect.** `setQueryData` anywhere in the frontend, not only inside the mutation hook itself — a container consuming a
hook can write the cache directly just as easily as the hook can — and `onMutate` anywhere in a mutation hook; both
tooled by `web:structural-gate`'s `assertNoCacheWriteDetectorWorks` sweep. Which controls get an override at all, and
whether a given override site reuses the shared helper instead of a bespoke `injectMutationState` call, is a review
question.

**Do.** A container reads `injectPendingMutationVariables(promoteChunkMutationKey)` and derives
`computed(() => isPendingFor(pending(), v => v.chunkId === card.id) ? 'ready' : card.status)`, handing the result to a
presentational card as an input.

**Don't.**
`onMutate: async (vars) => { const prev = queryClient.getQueryData(key); queryClient.setQueryData(key,
optimisticUpdate(prev, vars)); return { prev }; }`
— a snapshot-and-rollback cache write, forbidden regardless of correctness, because it gives the cache two writers (the
real response and the guess).
