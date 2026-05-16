# Replication as career infrastructure — framing notes

I wasn't really sure about whether being able to replicate papers and doing a bunch of replication attempts on papers was going to help or hurt me. Is it something like it makes you look bad in academia, but it makes you look good in industry, particularly for a research engineer role or something, to be able to take a scientific paper and then replicate it and turn it into an easy-to-use programme?

Your intuition is pretty close to right, but the picture is a bit more nuanced than a clean academia/industry split.
In academia
, replication work has historically been undervalued — it doesn't generate novel contributions, journals rarely want to publish it, and it doesn't advance a research agenda the way original work does. That said, this is genuinely shifting. The replication crisis has made reproducibility a more respected concern, and being known as someone who
can
replicate is different from being known as someone who
only
replicates. If you can replicate a paper and then extend it, that's completely fine. If replication is your primary output, that's where it looks thin.
In industry research engineering
, it's actually a strong signal — arguably one of the cleaner signals you can send. Here's why: taking a paper and turning it into a working, usable implementation requires you to understand the paper deeply enough to resolve all the things papers don't say — the implementation details that got omitted, the hyperparameters that weren't reported, the architectural choices that were glossed over. Anyone can read a paper. Far fewer people can make it run. The fact that you'd package it into something easy to use shows engineering judgment on top of the research comprehension.
For a role like research engineer at Anthropic specifically, this is close to a core job function — taking ideas (some internal, some from the literature) and turning them into robust implementations that researchers can actually build on. A portfolio of "I read X, here's my implementation, here are the gaps I found, here's what I had to figure out" is essentially a direct demonstration of that skill.
The one thing to watch
: framing matters. "I replicate papers" sounds like a hobby. "I take published methods and produce production-quality implementations, and in doing so I usually find things the paper didn't make explicit" sounds like a research engineering practice. The substance is the same — the framing is what determines how it lands.
So net: don't worry about it looking bad. Just make sure the artifacts are public, well-documented, and ideally you've written
something
(even a README or a short post) about what you learned in the gap between the paper and the working code.

I guess I'll explain how I actually do it. I have a Python library. You give the command in the command line, and then you give an arXiv link in the command line. What it does is it goes through the process of creating a git repository. It basically creates a skill file for downloading; it downloads the paper, makes the directory based off of the title of the paper, sets up a public GitHub repository with a GitHub Pages template on what you are doing to replicate it. It creates a script that downloads the files from arXiv, but it git ignores the directory of the files. The skill file says, "If this directory is empty, then do this," and the skill file goes through the way of guiding the agent through the paper so that it can make or import whatever code that is used for the paper and then run a replication of it. It sets it up via CI/CD to make a page that explains your findings, a PDF for those who want a PDF, a thing to download it and replicate, and a skill file that it made so that you can replicate it yourself. If it is not very compute intensive, it automatically replicates itself constantly by the CI/CD.
Show more

This is a genuinely impressive piece of tooling. Let me reflect back what you've built because there are a few distinct things happening here that are worth naming clearly:
What it actually is
: an agentic replication pipeline. You give it an arXiv link and it bootstraps the entire research engineering workflow — repo structure, paper acquisition, GitHub Pages scaffold, CI/CD, and critically a
skill file
that encodes the replication methodology as an agent-readable artifact. The skill file is doing a lot of work here: it's not just documentation, it's an executable guide for an agent to go from paper to running code.
Why this is a strong portfolio signal
: you've essentially automated the meta-skill. Most people who replicate papers do it manually and inconsistently. You've thought hard enough about
how
to replicate papers that you could codify the process into a repeatable system. That's a research engineering mindset applied one level up — not "how do I replicate this paper" but "how do I make replication itself a systematic, reproducible practice."
The CI/CD auto-replication for lightweight experiments
is particularly clever. It means the repo is living evidence, not a snapshot — anyone visiting can see it actually runs, and you can catch silent regressions if upstream dependencies change.
A few things worth thinking about as you develop this further:
The skill file format is interesting — is it specific to a particular agent/framework, or have you designed it to be relatively portable? That choice has implications for how broadly useful it is.
The GitHub Pages output that explains findings is the part that could make this genuinely publishable as a tool paper, not just a portfolio project. If you've essentially built an automated "living replication report" generator, that's a contribution to the reproducibility infrastructure conversation that ML venues are increasingly receptive to.
Have you used it on any papers yet that produced interesting findings in the gap between what the paper claims and what the replication shows?

I'm still working on it. I'll say it'll probably take, like, I'm still working on it. I have a lot of this stuff done. The basic thing that I'll say is that I have the basic stuff done, but it requires a bit of work on seeing how it works with different stuff.

That makes sense — the scaffolding being solid is actually the hard part. The "does it generalize across different papers with different codebases, different dependency situations, different levels of implementation detail" is where the real friction will be, and that's basically just mileage. You'll find out where the skill file assumptions break down, where the CI/CD chokes on compute constraints, where the GitHub Pages template doesn't fit a particular type of output.
The good news is that each paper you run through it is both a test case and a portfolio artifact simultaneously, so the debugging process is also the content generation process.
When it's more settled, it might be worth writing a short post about the design philosophy — particularly the skill file approach — even before it's fully polished. The idea of encoding "how to replicate this class of paper" as an agent-readable artifact is interesting enough to stand on its own as a concept, separate from whether the tooling is production-ready.

Yeah, the idea, my idea of it, is that every single replication made with this tool does two things:
It creates clear evidence of replicating research that somebody else can do. That's an important thing.
It produces a much more legible output.
For somebody actually trying to implement it in production systems, you'll still need to use an agent for implementing it in production systems. The GitHub Pages repo stuff gives a tool for it. Also, it gives a meta tool of making it so that there's my replication, but my replication comes with a skill file that explicitly explains how to do the replication for a later person.

Right, so there are actually three layers of artifact being produced simultaneously:
The replication itself
— evidence you understood the paper deeply enough to make it run.
The legibility layer
— the GitHub Pages output that translates "dense ML paper" into "here's what it actually does and how to use it," which is genuinely useful to practitioners who need to decide whether to adopt something without reading the full paper.
The skill file
— which is arguably the most interesting layer, because it's a reusable methodology artifact. It's not just "here's my replication," it's "here's how to replicate this, in a form an agent can execute." That compounds over time in a way the first two don't.
The third layer is what separates this from someone who just puts replication code on GitHub. Most replications are dead ends — you can look at the code but the knowledge of
how to do it
is still implicit in the person who wrote it. Your skill file externalizes that process so it's transferable, both to humans and to agents.
The framing I'd use when presenting this: you're not building a replication tool, you're building
replication infrastructure
. The individual replications are outputs, but the skill file corpus that accumulates over time is a growing library of operationalized research methodology. That's a different and more valuable thing.
That framing also makes it much easier to pitch as a genuine contribution rather than just a productivity tool.
