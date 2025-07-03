# Copyright (c) 2025 Benjamin Mummery

"""The underlying dictionary for the Americanise hook.
"""

DICTIONARY = {
    # -se -> -ize
    "characterise": "characterize",
    "initialise": "initialize",
    "instantiater": "instantiator",
    "parametrise": "parametrize",
    "prioritise": "prioritize",
    "specialise": "specialize",
    "organise": "organize",
    # -yse -> -yze
    "analyse": "analyze",
    "catalyse": "catalyze",
    # -our -> -or
    "armour": "armor",
    "behaviour": "behavior",
    "colour": "color",
    "flavour": "flavor",
    "neighbour": "neighbor",
    # -re -> -er
    "centre": "center",
    "fibre": "fiber",
    "litre": "liter",
    # -ae, -oe -> -e
    "amoeba": "amoebae",
    "anaesthesia": "anesthesia",
    "caesium": "cesium",
    # -ce -> -se
    "defence": "defense",
    "practise": "practice",  # british uses "practice" as the noun and "practise" as the verb. US uses "practice" for both.
    "licence": "license",  # british uses "licence" as the noun and "license" as the verb. US uses "license" for both.
    # -ge -> -g
    "ageing": "aging",
    "acknowledgement": "acknowledgment",
    "judgement": "judgment",
    # -ogue -> -og
    "analogue": "analog",
    "dialogue": "dialog",
    # -l -> -ll
    "fulfil": "fulfill",
    "enrol": "enroll",
    "skilful": "skillful",
    # -ll -> -l
    "labelled": "labeled",
    "signalling": "signaling",
}
