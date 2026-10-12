# Local input data cards

The audit supports nine settings across seven benchmark families. These cards
describe adapter behavior and source metadata available in the local research
configuration. They do not bundle data or grant data rights. Selected
upstream metadata checks are dated and distinguished from the original cache
acquisition revision. Unknown metadata is explicit.

| Family | CLI setting(s) | Unit | Ranking pool / CV group |
| --- | --- | --- | --- |
| [STALE](stale.md) | `stale` | Session | Scenario / scenario |
| [LongMemEval](longmemeval.md) | `lme_s` | Session | Non-abstention question / question haystack |
| [LoCoMo](locomo.md) | `locomo` | Session | Evidence-bearing question / conversation |
| [LoCoMo-Plus](locomo-plus.md) | `locomo_plus` | Turn | Inserted-cue item / host conversation |
| [BEAM](beam.md) | `beam_100k`, `beam_500k`, `beam_1m` | User message | Conversation / conversation |
| [HaluMem](halumem.md) | `halumem_medium` | Session | Matched question / user |
| [PersonaMem-v2](personamem2.md) | `personamem2` | User message | Persona history / persona |

[ForgetEval/Lethe](forgeteval.md) is the separate input for `baselines nulls`;
it is not a tenth audit setting. MemoryAgentBench and MemOps are not exposed by
these audit adapters.

Every input needs an explicit local path and a full 64-hex SHA-256. There is no
unpinned bypass or implicit download. The report records verified input
digests and byte sizes, not local paths or raw text. PersonaMem manifests pin
each child file; LoCoMo-Plus pins both the cue file and the host file; Lethe
pins its manifest and exactly three executable source files.

For a new dataset revision, keep a local source record of the upstream URL,
revision, licence evidence, content digest, size, adapter version, exclusions,
and access date. The digest proves byte identity with that record; it does not
prove source authenticity, permission, label validity, or independence of
benchmark construction. Reproduction reports must name changed inputs and
changed protocols rather than inheriting a historical result.

Known hashes below combine existing local constants/pin records with fresh
streaming hash-only inventories. The BEAM, HaluMem, and PersonaMem-v2 cards
also record official repository/file metadata checks dated 2026-10-03; those
checks downloaded no corpus bytes. Each card identifies its evidence and
remaining gaps. A card with no recorded hash requires a user-supplied protocol
pin; missing metadata must be resolved before claiming source-complete
reproduction or publication.
Licence statements are recorded source information, with uncertainty retained;
see [licence status](../licences.md).

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
