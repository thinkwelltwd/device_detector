The files in this directory correspond to python classes
by the same name.

### Words

Regexes can be unbounded, or expand to needlessly detailed
variations of words.

These files contain distinctive words that the AhoCorasick structure
should contain. The goal is that words here should be specific enough
to ONLY cover the regexes that are likely to match to this specific 
class.

### Scrub Words

ScrubWords can also be added, to make sure that variations expanded
from regexes are _excluded_.

This keeps "too general" words from being added to this class. 
Matching too broadly across classes defeats the entire purpose of the
AhoCorasick optimization.
