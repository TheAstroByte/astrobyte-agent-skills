# Third-party notices

Selected skills are redistributed and occasionally adapted under their respective licenses.

| Source | Pinned commit | Attribution | License | License copy |
|---|---|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | `9c9f36ccd3995266cd675468af71639c8dde1ec5` | Matt Pocock, 2026 | MIT | `licenses/mattpocock-skills-MIT.txt` |
| [cursor/plugins, pstack](https://github.com/cursor/plugins/tree/main/pstack) | `60c641e4fad674784b30abcf9f8915dea39df38d` | Lauren Tan, 2026 | MIT | `licenses/pstack-MIT.txt` |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `df1edb2e05487d0aa6d93c747141e0aed1187f25` | Addy Osmani, 2025 | MIT | `licenses/addyosmani-agent-skills-MIT.txt` |
| [anthropics/skills, frontend-design](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design) | `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | Anthropic | Apache-2.0 | `skills/frontend-design/LICENSE.txt` |
| [t3dotgg/tstack](https://github.com/t3dotgg/tstack/tree/7de017b3fc9d50c03cf3ecb98fb71e0ca65a78bd) | `7de017b3fc9d50c03cf3ecb98fb71e0ca65a78bd` | Theo Browne, 2026 | MIT | `skills/astrobyte-pr-workflows/LICENSE.tstack.txt` |

Every skill carries generated `LICENSES.txt` notices selected from its catalog source and declared adaptations. These include source revisions and complete applicable license texts, so standalone installation and cloud sync retain attribution. Canonical source license paths are recorded in `catalog.json`; regeneration and validation are described in `docs/upstreams.md`.

The Anthropic frontend-design instructions and license are unchanged upstream files. Its license travels with standalone installations, alongside the generated notice. The upstream repository's third-party notices describe software and fonts outside its original two-file package; those components are not redistributed here.

The optional Astrobyte PR workflows adapt tstack's finish, review, council, continuation, and PR-feedback procedures. They share existing Astrobyte gates and use a separate local setup helper. Both finish operations leave work unmerged. No tstack watcher script is redistributed. The source license travels with the optional package.

Astrobyte-owned skills combine general engineering ideas from these sources with new routing, portability, configuration, and safety behavior. Their provenance is recorded in `catalog.json` and `docs/upstreams.md`.
