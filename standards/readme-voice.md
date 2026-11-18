# The README

The voice `blizzard`'s `README.md` is written in. What the README holds is decided in the README itself.

## The README's voice (`bzh:readme-voice`)

Write the way a senior engineer explains a tool they built and use every day to a peer who might adopt it. The reader is
an engineer deciding whether Blizzard is worth an evening. They are capable, a little skeptical, and short on time. They
have seen a hundred agent tools promise the moon, and they trust a project that says plainly what it does, shows it, and
lets them try it.

Say what happens, the way a person would say it out loud. Every sentence has a subject and a verb and makes one claim
the product backs today. Prefer the concrete thing over the category: "a `kill -9` at any moment loses at most the
tokens in flight" beats "robust crash recovery". Talk to the reader as "you" and about the product as "Blizzard".
Explain a term the first time it appears, in the sentence that uses it, and then use that one term every time after.

> Run the hub and a runner on your laptop tonight, against a side project or the repo you work on. When your team wants
> in, move the hub to a shared server and give each engineer their own runner. Nothing about your graphs changes.

The same idea in the register this README never uses:

> Start small, scale infinitely — solo, team, org. Same graphs, same workflow, zero rewrites. Not a demo mode: the real
> thing.

The second reads like a slide. Its fragments are built for rhythm, it joins its points with dashes instead of saying how
they connect, and it asserts instead of showing. Specifically, the README never uses:

- slogans or chains of clipped fragments, where a plain sentence with a verb would do;
- em-dash asides, or the shape "thing, thing — result". Name the things and let the reader see the result;
- middle dots or slashes joining terms into a list (`SSO · roles · invitations`). Pick the one term that matters, or
  write the list as a sentence;
- the "X, not Y" contrast as a flourish ("leases and epochs, not retries and hope"). Use it only where the contrast is
  the point and the reader would otherwise assume Y;
- hype words such as seamless, powerful, blazing, effortless, revolutionary or magic, and claims of being the first or
  the only;
- emoji in headings or as bullet decoration.

Arrows (`→`) are fine in code blocks and command output; prose says "then".
