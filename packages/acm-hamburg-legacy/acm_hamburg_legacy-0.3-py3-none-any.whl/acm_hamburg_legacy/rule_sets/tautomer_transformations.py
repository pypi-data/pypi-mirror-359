import molvs

__all__ = ["tautomer_transformations"]

tautomer_transformations = [
    molvs.tautomer.TautomerTransform(
        "1,3 (thio)keto/enol f", "[CX4!H0]-[C]=[O,S,Se,Te;X1]"
    ),
    molvs.tautomer.TautomerTransform(
        "1,3 (thio)keto/enol r", "[O,S,Se,Te;X2!H0]-[C]=[C]"
    ),
    molvs.tautomer.TautomerTransform(
        "1,5 (thio)keto/enol f", "[CX4,NX3;!H0]-[C]=[C][CH0]=[O,S,Se,Te;X1]"
    ),
    molvs.tautomer.TautomerTransform(
        "1,5 (thio)keto/enol r", "[O,S,Se,Te;X2!H0]-[CH0]=[C]-[C]=[C,N]"
    ),
    molvs.tautomer.TautomerTransform("aliphatic imine f", "[CX4!H0]-[C]=[NX2]"),
    molvs.tautomer.TautomerTransform("aliphatic imine r", "[NX3!H0]-[C]=[CX3]"),
    molvs.tautomer.TautomerTransform("special imine f", "[N!H0]-[C]=[CX3R0]"),
    molvs.tautomer.TautomerTransform("special imine r", "[CX4!H0]-[c]=[n]"),
    molvs.tautomer.TautomerTransform(
        "1,3 aromatic heteroatom H shift f", "[#7!H0]-[#6R1]=[O,#7X2]"
    ),
    molvs.tautomer.TautomerTransform(
        "1,3 aromatic heteroatom H shift r", "[O,#7;!H0]-[#6R1]=[#7X2]"
    ),
    molvs.tautomer.TautomerTransform(
        "1,3 heteroatom H shift", "[#7,S,O,Se,Te;!H0]-[#7X2,#6,#15]=[#7,#16,#8,Se,Te]"
    ),
    molvs.tautomer.TautomerTransform(
        "1,5 aromatic heteroatom H shift",
        "[#7,#16,#8;!H0]-[#6,#7]=[#6]-[#6,#7]=[#7,#16,#8;H0]",
    ),
    molvs.tautomer.TautomerTransform(
        "1,5 aromatic heteroatom H shift f",
        "[#7,#16,#8,Se,Te;!H0]-[#6,nX2]=[#6,nX2]-[#6,#7X2]=[#7X2,S,O,Se,Te]",
    ),
    molvs.tautomer.TautomerTransform(
        "1,5 aromatic heteroatom H shift r",
        "[#7,S,O,Se,Te;!H0]-[#6,#7X2]=[#6,nX2]-[#6,nX2]=[#7,#16,#8,Se,Te]",
    ),
    molvs.tautomer.TautomerTransform(
        "1,7 aromatic heteroatom H shift f",
        "[#7,#8,#16,Se,Te;!H0]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#6]-[#6,#7X2]=[#7X2,S,O,Se,Te,CX3]",
    ),
    molvs.tautomer.TautomerTransform(
        "1,7 aromatic heteroatom H shift r",
        "[#7,S,O,Se,Te,CX4;!H0]-[#6,#7X2]=[#6]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[NX2,S,O,Se,Te]",
    ),
    molvs.tautomer.TautomerTransform(
        "1,9 aromatic heteroatom H shift f",
        "[#7,O;!H0]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#7,O]",
    ),
    molvs.tautomer.TautomerTransform(
        "1,11 aromatic heteroatom H shift f",
        "[#7,O;!H0]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#7X2,O]",
    ),
    molvs.tautomer.TautomerTransform(
        "furanone f", "[O,S,N;!H0]-[#6r5]=[#6X3r5;$([#6]([#6r5])=[#6r5])]"
    ),
    molvs.tautomer.TautomerTransform(
        "furanone r", "[#6r5!H0;$([#6]([#6r5])[#6r5])]-[#6r5]=[O,S,N]"
    ),
    molvs.tautomer.TautomerTransform(
        "keten/ynol f", "[C!H0]=[C]=[O,S,Se,Te;X1]", bonds="#-"
    ),
    molvs.tautomer.TautomerTransform(
        "keten/ynol r", "[O,S,Se,Te;!H0X2]-[C]#[C]", bonds="=="
    ),
    molvs.tautomer.TautomerTransform(
        "ionic nitro/aci-nitro f", "[C!H0]-[N+;$([N][O-])]=[O]"
    ),
    molvs.tautomer.TautomerTransform(
        "ionic nitro/aci-nitro r", "[O!H0]-[N+;$([N][O-])]=[C]"
    ),
    molvs.tautomer.TautomerTransform("oxim/nitroso f", "[O!H0]-[N]=[C]"),
    molvs.tautomer.TautomerTransform("oxim/nitroso r", "[C!H0]-[N]=[O]"),
    molvs.tautomer.TautomerTransform(
        "oxim/nitroso via phenol f", "[O!H0]-[N]=[C]-[C]=[C]-[C]=[OH0]"
    ),
    molvs.tautomer.TautomerTransform(
        "oxim/nitroso via phenol r", "[O!H0]-[c]=[c]-[c]=[c]-[N]=[OH0]"
    ),
    molvs.tautomer.TautomerTransform(
        "cyano/iso-cyanic acid f", "[O!H0]-[C]#[N]", bonds="=="
    ),
    molvs.tautomer.TautomerTransform(
        "cyano/iso-cyanic acid r", "[N!H0]=[C]=[O]", bonds="#-"
    ),
    molvs.tautomer.TautomerTransform(
        "isocyanide f", "[C-0!H0]#[N+0]", bonds="#", charges="-+"
    ),
    molvs.tautomer.TautomerTransform(
        "isocyanide r", "[N+!H0]#[C-]", bonds="#", charges="-+"
    ),
    molvs.tautomer.TautomerTransform("phosphonic acid f", "[OH]-[PH0]", bonds="="),
    molvs.tautomer.TautomerTransform("phosphonic acid r", "[PH]=[O]", bonds="-"),
]
